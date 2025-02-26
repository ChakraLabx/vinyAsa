import re
import spacy
import json
import pickle
import logging
import numpy as np
from typing import Optional, List, Literal

import infinity_embedded
from infinity_embedded.common import SparseVector
from infinity_embedded.common import ConflictType
from infinity_embedded.index import IndexInfo, IndexType

from hashlib import sha256
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

from vision.file_utils import llm, embedding

logger = logging.getLogger(__name__)

NLP_MODEL = spacy.load("en_core_web_sm")

class SpacyBM25Handler:
    def __init__(self):
        self.nlp = NLP_MODEL
        self.bm25 = None
        self.corpus_tokens = []
        
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using spaCy and return filtered tokens."""
        doc = self.nlp(text)
        tokens = [token.text.lower() for token in doc if not token.is_stop]
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(token)
            sub_tokens = re.findall(r"\w+", token)
            if len(sub_tokens) > 1:
                expanded_tokens.extend(sub_tokens)
        return expanded_tokens

    def normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to [0,1] range."""
        max_score = max(scores) if scores.size > 0 else 1.0
        return [score / max_score for score in scores]


    def get_sparse_vector(self, text: str, vocab_size: int = 3072, min_score: float = 0.01) -> SparseVector:
        """Convert text to BM25 sparse vector."""
        tokens = self.tokenize(text)

        # Initialize BM25 only once
        if self.bm25 is None:
            self.corpus_tokens = [tokens]
            self.bm25 = BM25Okapi(self.corpus_tokens)
        elif tokens not in self.corpus_tokens:  # Avoid adding duplicate tokens
            self.corpus_tokens.append(tokens)
            self.bm25 = BM25Okapi(self.corpus_tokens)

        # Get BM25 scores
        scores = self.bm25.get_scores(tokens)
        scores = self.normalize_scores(scores)

        indices = [i for i, score in enumerate(scores) if score > min_score]
        values = [float(scores[i]) for i in indices]

        if len(indices) > vocab_size:
            sorted_pairs = sorted(zip(values, indices), reverse=True)[:vocab_size]
            values, indices = zip(*sorted_pairs)
            values = list(values)
            indices = list(indices)

        return SparseVector(indices, values)


class CacheEmbedding:
    def __init__(self, inf_db_name: str, sparse_method: Literal["tfidf", "bm25"] = "bm25", embedding_instance=None, infinity_object=None) -> None:
        self._embeddings_instance = embedding_instance
        self._infinity_object = infinity_object
        self._sparse_method = sparse_method
        self._inf_db_name = inf_db_name
        
        if sparse_method == "tfidf":
            self._vectorizer = TfidfVectorizer(max_features=3072)
            self._spacy_handler = None
        else:  
            self._vectorizer = None
            self._spacy_handler = SpacyBM25Handler()

    # def __del__(self):
    #     if hasattr(self, '_infinity_object'):
    #         try:
    #             self._infinity_object.disconnect()
    #         except:
    #             pass

    def _get_sparse_vector(self, text: str) -> SparseVector:
        """Get sparse vector based on selected method."""
        if self._sparse_method == "tfidf":
            sparse_matrix = self._vectorizer.fit_transform([text])
            indices = sparse_matrix.indices.tolist()
            values = sparse_matrix.data.tolist()
            return SparseVector(indices, values)
        else:  
            return self._spacy_handler.get_sparse_vector(text)

    def inf_obj(self, create_table: bool = True):
        tbl_name = self._inf_db_name+'_tbl'
        id_idx = self._inf_db_name+'_id_idx'
        vec_idx = self._inf_db_name+'_vec_idx'
        sparse_idx = self._inf_db_name+'_sparse_idx'

        # Ensure the database exists
        self._infinity_object.create_database(self._inf_db_name, conflict_type=ConflictType.Ignore)
        db_object = self._infinity_object.get_database(self._inf_db_name)
        
        # Define table schema
        columns_definition = {
            "id": {"type": "varchar", "unique": True}, 
            "text": {"type": "varchar"},
            "vec": {"type": "vector, 3072, float"}, 
            "sparse": {"type": "sparse,3072,float,int"}
        }
        

        db_object.drop_table(tbl_name, conflict_type = ConflictType.Ignore) if create_table else db_object
        table_object = db_object.create_table(tbl_name, columns_definition, conflict_type=ConflictType.Ignore)
        table_object.create_index(id_idx, IndexInfo("text", IndexType.FullText), conflict_type=ConflictType.Ignore)
        table_object.create_index(vec_idx, IndexInfo("vec", IndexType.Hnsw, {"metric": "cosine"}), conflict_type=ConflictType.Ignore)
        table_object.create_index(sparse_idx, IndexInfo("sparse", IndexType.BMP), conflict_type=ConflictType.Ignore)

        return table_object

    def embed_documents(self, db_name: str, texts: list[str]) -> list[list[float]]:
        table_object = self.inf_obj()
        """Embed search docs with both dense and sparse embeddings."""
        # Fetch existing IDs to avoid duplication
        df_result = table_object.output(["id"]).to_pl()
        existing_ids = []
        if df_result[0] is not None:  # Check if the DataFrame is not None
            existing_ids = df_result[0]["id"].to_list()

        max_chunks = 1024
        text_embeddings = []
        for i in range(0, len(texts), max_chunks):
            batch_texts = texts[i:i + max_chunks]
            embedding_results = self._embeddings_instance.embeddings.create(
                input=batch_texts,
                model="text-embedding-3-large"
            )
            
            # Process each text and its embedding
            for text, emb_data in zip(batch_texts, embedding_results.data):
                vector = emb_data.embedding
                normalized_embedding = (vector / np.linalg.norm(vector)).tolist()
                text_embeddings.append(normalized_embedding)
                
                hash_text = str(text) + "None"
                hash_value = sha256(hash_text.encode()).hexdigest()
                
                # Skip if the document already exists
                if hash_value in existing_ids:
                    print(f"Document already exists in the database: {text}")
                    continue
                
                sparse_vec = self._get_sparse_vector(text)
                
                # Insert new document
                table_object.insert({
                    "id": hash_value,
                    "text": text,
                    "vec": normalized_embedding,
                    "sparse": sparse_vec
                })
                print("hello")

        return table_object

    def embed_query(self, db_name: str, text: str) -> list[float]:
        """Embed query text with both dense and sparse embeddings."""
        hash_text = str(text) + "None"
        hash_value = sha256(hash_text.encode()).hexdigest()
        
        embedding_result = self._embeddings_instance.embeddings.create(
            input=[text],
            model="text-embedding-3-large"
        )
        vector = embedding_result.data[0].embedding
        embedding_results = (vector / np.linalg.norm(vector)).tolist()
        
        sparse_vec = self._get_sparse_vector(text)  
        
        return sparse_vec, embedding_results

class QueryPraśna:
    def __init__(self, layout_data):
        self.layout_data = layout_data
        self.chat_history = []

    # Example usage
    def store_infinity_vec(self, texts, db_name):
        embedding_instance = embedding
        infinity_object = infinity_embedded.connect("/var/infinity")
        
        # Create cache embedding instance
        cache_embedding = CacheEmbedding(
            inf_db_name=db_name,
            sparse_method="bm25",
            embedding_instance=embedding_instance,
            infinity_object=infinity_object
        )

        return cache_embedding.embed_documents(db_name, texts)
        
    def get_infinity_vec(self, query, db_name, n):
        # query = "What is machine learning?"
        embedding_instance = embedding
        infinity_object = infinity_embedded.connect("/var/infinity")
        
        # Create cache embedding instance
        cache_embedding = CacheEmbedding(
            inf_db_name=db_name,
            sparse_method="bm25",
            embedding_instance=embedding_instance,
            infinity_object=infinity_object
        )
        sparse, dense = cache_embedding.embed_query(db_name, query)
        tb_obj = cache_embedding.inf_obj(create_table=False)
        
        op = tb_obj.output(["id", "text", "vec", "sparse", "_score"]) \
                .match_dense("vec", dense, "float", "cosine", n) \
                .match_sparse("sparse", sparse, "ip", n) \
                .match_text("text", query, 10) \
                .fusion("weighted_sum", n, {"weights": "2,1,0.5"}) \
                .to_pl()
        return op[0]

    def process_document_json(self, layout_data):
        chunks = []
        current_text = ""
        chunk_count = 1
        max_words = 200

        for pages in layout_data[0]:
            elements = sorted(pages, key=lambda x: x['top'])
            current_header = None
            
            for element in elements:
                element_type = element['type'].lower()
                text = element['text'].strip()
                
                if not text:
                    continue
                    
                if element_type == 'header':
                    if current_text:
                        chunks.append(f"{current_text.strip()}")
                        chunk_count += 1
                        current_text = ""
                    current_header = text
                    current_text = text + "\n"
                else:
                    words = len(text.split())
                    if len((current_text + " " + text).split()) > max_words and current_text:
                        chunks.append(f"{current_text.strip()}")
                        chunk_count += 1
                        current_text = text + " "
                    else:
                        current_text += text + " "
        
        # Add remaining text if exists
        if current_text:
            chunks.append(f"{current_text.strip()}")
            current_text = ""
        
        return chunks

    def _get_insights_llm(self, query, context):
        prompt = f"""
           Get the
            {query}
            reponse from
            {context}
                """

        response = llm.chat.completions.create(
            model="deepseek-reasoner",
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are a insight finder."},
                # *((self.chat_history)),
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    def __call__(self, query):
        # lb = layout_bodh("layout")
        # layout_data = lb(filepath, model_name="RAGFLOW", threshold=0.005)
        chunks = self.process_document_json(self.layout_data)
        
        for chunk in chunks:
            self.store_infinity_vec([chunk], 'prasna')
        
        pl_data = self.get_infinity_vec(query, 'prasna', 3)
        context = "\n\n".join(pl_data['text'].to_list())
        return self._get_insights_llm(query, context)
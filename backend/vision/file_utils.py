#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import base64
import json
import os
import re
from io import BytesIO

import os
import logging
# import chromadb

from openai import OpenAI
from openai import AzureOpenAI
# from chromadb.config import Settings
# import cohere

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('openai').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"
COHERE_API_KEY = "BGsS3IKBNffUCeWobPpIzmXUgTTgboJfhvZmaOBO"

embedding = AzureOpenAI(
    api_key="10eef653f8634d70997b27548577dcf4",  
    api_version="2024-06-01",
    azure_endpoint="https://azureunadaopenai.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"
)

# llm = AzureOpenAI(
#     azure_endpoint="https://unadalabsai.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview", 
#     api_key="a6203e4a768b40b5acfc41b01f71a2a0",  
#     api_version="2024-07-01-preview"
# )

llm = OpenAI(api_key="sk-5bb4a39a57954879b760ff1724a37b44", base_url="https://api.deepseek.com")

def get_project_base_directory():
    return os.getcwd()

def traversal_files(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

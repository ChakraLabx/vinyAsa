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

# embedding = AzureOpenAI(
#     api_key="",  
#     api_version="",
#     azure_endpoint=""
# )

# llm = AzureOpenAI(
#     azure_endpoint="", 
#     api_key="",  
#     api_version=""
# )

# llm = OpenAI(api_key="", base_url="")

def get_project_base_directory():
    return os.getcwd()

def traversal_files(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname

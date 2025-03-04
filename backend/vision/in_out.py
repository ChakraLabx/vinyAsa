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

import os
import traceback
from PIL import Image
import pdfplumber
import numpy as np
from vision.file_utils import traversal_files

def init_in_out(inputs, output_dir):
    images = []
    outputs = []

    if output_dir and not os.path.exists(output_dir):
        os.mkdir(output_dir)

    def pdf_pages(fnm, zoomin=3):
        nonlocal outputs, images
        pdf = pdfplumber.open(fnm)
        images = [p.to_image(resolution=72 * zoomin).annotated for i, p in enumerate(pdf.pages)]

        if output_dir:
            for i, page in enumerate(images, 1):
                outputs.append(os.path.split(fnm)[-1] + f"_{i}.jpg")

    def images_and_outputs(fnm):
        nonlocal outputs, images
        if fnm.split(".")[-1].lower() == "pdf":
            pdf_pages(fnm)
            return
        try:
            img = Image.open(fnm)
            if img.mode == 'RGBA':
                img = img.convert('RGB')  
            images.append(img)
            if output_dir:
                outputs.append(os.path.split(fnm)[-1])
        except Exception as e:
            traceback.print_exc()

    if os.path.isdir(inputs):
        for fnm in traversal_files(inputs):
            images_and_outputs(fnm)
    else:
        images_and_outputs(inputs)

    if output_dir:
        for i in range(len(outputs)): 
            outputs[i] = os.path.join(output_dir, outputs[i])

    return images, outputs

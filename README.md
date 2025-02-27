# vinyAsa: Open-Source Document AI Platform

Welcome to **vinyAsa**, an open-source Document AI solution developed by [ChakraLabx](https://github.com/ChakraLabx). This platform is designed to make text extraction, analysis, and interaction with scanned documents, PDFs, and images more efficient. By leveraging multiple OCR and layout analysis models, Vinyāsa provides a versatile environment for users who need to process various types of documents—from medical forms and invoices to legal contracts.

[![Watch the video](https://img.youtube.com/vi/gLFQBTxSijk/0.jpg)](https://youtu.be/gLFQBTxSijk)

---

## Table of Contents
1. [Features](#features)  
2. [Project Structure](#project-structure)  
3. [Getting Started](#getting-started)  
    - [Prerequisites](#prerequisites)  
    - [Installation](#installation)  
    - [Running the Project](#running-the-project)  
4. [Usage](#usage)  
5. [Future Works (TODO)](#future-works-todo)  
6. [Acknowledgments](#acknowledgments)  
7. [Citation](#citation)  

---

## Features

- **Multi-Model OCR**: Integrates various OCR engines like Ragflow, Tesseract, PaddleOCR, Surya, EasyOCR, RapidOCR, and MMOCR for optimal text extraction results.  
- **Layout Analysis**: Retains document structure (paragraphs, headers, tables) for more accurate data retrieval.  
- **Forms & Tables Extraction**: Easily extract key-value pairs and tabular data, even from complex layouts.  
- **Query-Based Search**: Hybrid (sparse + semantic) search powered by an infinity vector database for intelligent document querying.  
- **Signature Detection**: Identify and highlight signatures in scanned or digital documents.  
- **User-Friendly Interface**: Switch seamlessly between multiple tabs—Raw Text, Layout, Forms, Tables, Queries, and Signature.

---

## Project Structure

```
vinyAsa/
  ├── frontend/
  │    ├── public/
  │    ├── src/
  │    ├── package.json
  │    └── ...
  ├── backend/
  │    ├── app.py
  │    ├── requirements.txt
  │    └── ...
  └── README.md
```

- **frontend/**: Contains the React application.  
- **backend/**: Contains the Python Flask (or similar) server application.

---

## Getting Started

### Prerequisites

- **Node.js** (v14 or later recommended)  
- **npm** (v6 or later recommended)  
- **Python** (3.7+ recommended)  
- **Git** (for cloning the repository)

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ChakraLabx/vinyAsa.git
   ```
2. **Frontend Setup**  
   ```bash
   cd vinyAsa/frontend
   npm install
   ```
3. **Backend Setup**  
   ```bash
   cd ../backend
   # Create and activate a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the Project

1. **Start the Backend**  
   ```bash
   cd vinyAsa/backend
   python app.py
   ```
   - This should start the Python server at a specified port (e.g., `http://127.0.0.1:5000`).

2. **Start the Frontend**  
   ```bash
   cd ../frontend
   npm start
   ```
   - By default, the React app runs on `http://localhost:3000`.  

3. **Open in Browser**  
   - Navigate to `http://localhost:3000` to access the Vinyāsa UI.

---

## Usage

1. **Raw Text Tab**:  
   - Upload PDFs or images.  
   - Choose an OCR model to extract text.  
   - Click on any line of extracted text to see the highlighted region in the document.  

2. **Layout Tab**:  
   - Detect and visualize document structure.  
   - Ideal for identifying paragraphs, headings, and sections.  

3. **Forms Tab**:  
   - Extract key-value pairs from structured or semi-structured forms.  
   - Validate data by clicking on any extracted field.  

4. **Tables Tab**:  
   - Identify and extract rows, columns, and cells from tabular data.  
   - Useful for invoices, medical test results, and more.  

5. **Queries Tab**:  
   - Perform natural language queries on your document.  
   - The system uses a hybrid (sparse + semantic) search to retrieve the most relevant sections.  

6. **Signature Tab**:  
   - Detect and highlight signatures in scanned documents.  
   - Useful for contract validation and approvals.

---

## Future Works (TODO)

- **Voice Agent**:  
  - Implement a voice-based assistant to **load PDFs** and **navigate** through tabs or models using spoken commands.  
- **Additional Model Integrations**:  
  - Incorporate more OCR and layout analysis models for improved accuracy across different document types.  
- **Enhanced Collaboration**:  
  - Support real-time collaboration for teams processing large volumes of documents.  
- **Containerization**:  
  - Provide Docker images for easier deployment and scaling.

---

## Acknowledgments

We extend our gratitude to the **developers and communities** behind the following open-source models and libraries:

- **Tesseract OCR**: [GitHub](https://github.com/tesseract-ocr/tesseract)  
- **PaddleOCR**: [GitHub](https://github.com/PaddlePaddle/PaddleOCR)  
- **EasyOCR**: [GitHub](https://github.com/JaidedAI/EasyOCR)  
- **RapidOCR**: [GitHub](https://github.com/RapidAI/RapidOCR)  
- **MMOCR**: [GitHub](https://github.com/open-mmlab/mmocr)  
- **Surya**: Specialized OCR model (check project docs)  
- **Ragflow**: ChakraLabx’s in-house OCR and layout analysis solution  
- **Viny**: ChakraLabx’s model for forms and layout analysis  

---

## Citation

If you find **Vinyāsa** helpful in your research or commercial project, please consider citing our work:

```
@misc{vinyAsa2025,
  author = {ChakraLabx},
  title = {Vinyāsa: Open-Source Document AI Platform},
  year = {2025},
  howpublished = {\url{https://github.com/ChakraLabx/vinyAsa}}
}
```

---

We welcome contributions! Feel free to open an issue or pull request for any bug fixes, enhancements, or new features. Thank you for using **Vinyāsa**, and we hope it transforms the way you process and analyze documents. 

For more details, check out our [GitHub repo](https://github.com/ChakraLabx/vinyAsa.git) or get in touch with us directly. 

**Happy Document Processing!**

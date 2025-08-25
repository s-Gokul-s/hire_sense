# Read a Multiple Format  Resume and Pull Out The Text

import fitz   # PyMuPDF library for working with PDF files
from typing import BinaryIO  ## Used to type-hint(specify dataype) the input as a binary file stream
import docx2txt  
import os
import tempfile

""" Extract Text from a PDF file stream """
def extract_text_from_pdf_file(file:BinaryIO)->str:
    try:
        text='' 
        pdf=fitz.open(stream=file.read(),filetype="pdf") 
        for page in pdf:
            text+=page.get_text()
        pdf.close()
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF file: {e}")


""" Extract Text from a DOCX file stream """
def extract_text_from_docx_file(file: BinaryIO) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        text = docx2txt.process(temp_file_path)
        os.remove(temp_file_path)
        return text.strip()
    except Exception as e:
         raise RuntimeError(f"Error extracting text from DOCX file: {e}")



""" Extract Text from a TXT file stream """
def extract_text_from_txt_file(file: BinaryIO) -> str:
    try:
        content= file.read().decode("utf-8")
        return content.strip()
    except Exception as e:
        raise RuntimeError(f"Error extracting text from TXT file: {e}")


"""Detect file type based on content_type and delegate:Unified Extractor"""
def extract_text_from_file(file:BinaryIO,content_type:str)-> str:
    if content_type == "application/pdf":
        return extract_text_from_pdf_file(file)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx_file(file)
    elif content_type == "text/plain":
        return extract_text_from_txt_file(file)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")
    


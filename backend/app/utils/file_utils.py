# Use later to save the ranked files

import os
from fastapi import UploadFile


UPLOAD_DIR="uploads"

def save_file(uploaded_file:UploadFile)->str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())

    return file_path


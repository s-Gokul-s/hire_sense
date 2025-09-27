import io
import pandas as pd
import zipfile
from typing import List, Dict, Any
from pathlib import Path

# Define the directory where the original, ranked resumes are stored.
# Based on your file structure, this is the 'temp_resumes' folder.
TEMP_RESUMES_DIR = Path("temp_resumes")

def generate_excel_report(data: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Generates a detailed resume ranking report in Excel format (XLSX).

    Args:
        data: A list of dictionaries containing ranked resume data (including
              Rank, Filename, Score, Matched Skills, Missing Skills).

    Returns:
        io.BytesIO: A BytesIO buffer containing the Excel file content.
    """
    # Define the desired column order for the Excel file
    column_order = ["Rank", "Resume Filename", "Relevance Score (%)", "Matched Skills", "Missing Skills"]
    df = pd.DataFrame(data, columns=column_order)
    
    excel_buffer = io.BytesIO()
    
    # Use xlsxwriter engine for advanced formatting
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        
        df.to_excel(writer, index=False, sheet_name="Resume_Insights")
        worksheet = writer.sheets['Resume_Insights']
        
        # Define header format
        header_format = writer.book.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC', # Light green background
            'border': 1
        })
        
        # Apply header format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Define data format (required for skill wrapping)
        data_format = writer.book.add_format({'text_wrap': True, 'valign': 'top'})
        
        # Set column widths and apply data formatting to all columns (starting from row 1)
        worksheet.set_column(0, 0, 5) 
        worksheet.set_column(1, 1, 35) 
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 60, data_format) # Matched Skills (with wrap)
        worksheet.set_column(4, 4, 60, data_format) # Missing Skills (with wrap)
        
        # Freeze the header row
        worksheet.freeze_panes(1, 0)

    excel_buffer.seek(0)
    return excel_buffer

def generate_csv_report(data: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Generates a resume ranking report in CSV format.

    Returns:
        io.BytesIO: A BytesIO buffer containing the CSV file content.
    """
    column_order = ["Rank", "Resume Filename", "Relevance Score (%)", "Matched Skills", "Missing Skills"]
    df = pd.DataFrame(data, columns=column_order)
    
    csv_buffer = io.BytesIO()
    # Write the DataFrame to the buffer as a CSV file
    csv_buffer.write(df.to_csv(index=False, encoding='utf-8').encode('utf-8'))
    csv_buffer.seek(0)
    return csv_buffer


def generate_resumes_zip(resumes: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Creates a ZIP archive containing the ORIGINAL binary files (PDF/DOCX)
    from the temp_resumes directory, using their exact original extensions.

    Args:
        resumes: A list of resume dictionaries, each containing 'filename' (name of the file in temp_resumes).

    Returns:
        io.BytesIO: A BytesIO buffer containing the ZIP file content.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for resume in resumes:
            filename = resume['filename']
            file_path = TEMP_RESUMES_DIR / filename

            if file_path.exists() and file_path.is_file():
                # Read the original file content in binary mode
                try:
                    with open(file_path, 'rb') as f:
                        original_content = f.read()
                    
                    # Write the original binary content to the zip archive
                    # The file inside the zip is saved with its original extension (e.g., .pdf)
                    zf.writestr(f"ranked_resumes/{filename}", original_content)
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
            else:
                print(f"Warning: Original file not found for {filename} at {file_path}")

    zip_buffer.seek(0)
    return zip_buffer

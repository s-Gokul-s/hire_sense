import re
import string

def preprocess_text(text : str) -> str:
    """
    Cleans and preprocesses raw text by:
    1. Converting to lowercase.
    2. Removing punctuation.
    3. Removing extra whitespace.
    """
    if not isinstance(text,str):
        return ""
    
    # Convert to lowercase
    text=text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("","",string.punctuation))

    # Remove extra whitespace
    text = re.sub(r"\s+"," ",text).strip()

    return text

from sentence_transformers import SentenceTransformer

# Load the model once when the app starts for efficiency.
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer model loaded successfully.")
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    model = None


def generate_embedding(text : str) -> list[float]:
    """
    Generates a numerical vector (embedding) for a given text.
    """
    if model is None:
        raise RuntimeError("Embedding model is not available.")
    
    embedding = model.encode(text)

    return embedding.tolist()


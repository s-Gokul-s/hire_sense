import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(jd_embedding : list[float] , resume_embedding : list[float]) -> float:
    """
    Calculates the cosine similarity score between two embeddings.
    """

    # Reshape lists into 2D arrays for the function
    jd_vec = np.array(jd_embedding).reshape(1,-1)

    resume_vec = np.array(resume_embedding).reshape(1, -1)

    # Calculate similarity
    score = cosine_similarity(jd_vec, resume_vec)[0][0]

    return float(score)
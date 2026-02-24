import faiss
import numpy as np
import os

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index


def save_index(index, path="faiss_index/index.bin"):
    faiss.write_index(index, path)


def load_index(path="faiss_index/index.bin"):
    return faiss.read_index(path)
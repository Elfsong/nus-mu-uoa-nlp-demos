# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

from sentence_transformers import SentenceTransformer



class SimilarityModel(object):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def embeddings(self, sentences: list) -> list:
        embeddings = self.model.encode(sentences)
        return embeddings



if __name__ == "__main__":
    sm = SimilarityModel("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = sm.embeddings(["Cisco SE1500 router", "SE1500 router", "SE1500", "routers"])
    print(embeddings)
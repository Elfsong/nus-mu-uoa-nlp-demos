# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

from torch import tensor
from sentence_transformers import SentenceTransformer, util


class SimilarityModel(object):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def embeddings(self, sentences: list) -> list:
        embeddings = self.model.encode(sentences)
        return embeddings

    def similarity(self, source: tensor, tagart: tensor):
        return util.pytorch_cos_sim(source, tagart)
    
    def product_search(self, product_list: list, source_product: str):
        product_embeddings = self.embeddings(product_list + [source_product])
        similarity_scores = [self.similarity(product_embeddings[-1], pe) for pe in product_embeddings[:-1]]
        max_similarity_score = max(similarity_scores)
        max_index = similarity_scores.index(max_similarity_score)
        return product_list[max_index], max_similarity_score


if __name__ == "__main__":
    sm = SimilarityModel("sentence-transformers/all-MiniLM-L6-v2")

    results = sm.product_search(["Cisco SE1500 router", "SE1500 router", "SE1500", "routers"], "Router")

    print(results)
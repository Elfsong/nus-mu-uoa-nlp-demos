# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-08
# Email: mingzhe@nus.edu.sg

from ast import Num
import csv
from os import stat
import numpy as np
from sklearn.manifold import TSNE
import yaml
import pandas as pd

from . utils.build_features_matrix import build_matrix
from . utils.clustering_algo import ClusteringAlgo, ClusteringAlgoSparse
from . utils.eval import general_statistics, cluster_event_match, mcminn_eval


class TweetsCluster(object):
    def __init__(self):
        # model options: 'tfidf_dataset', 'tfidf_all_tweets', 'w2v_gnews_en', "elmo", "bert", "sbert_nli_sts", "use"
        self.model = "tfidf_dataset"
        self.lang = "en"
        self.annotation = "no"
        self.threshold = 0.8
        self.window = 24
        self.distance = "cosine"

        # Tweet cluster keywords
        self.filter_words = [ "medicine", "medication", "cure", "treat", \
                              "heal", "remedy", "drug", "dose", "dosage", \
                              "prescription", "medicament", "eliminate", \
                              "remove", "restore", "rehabilita", "make well", \
                              "make better", "curative"]

        # Tweet id-text mappings
        self.tweet_id2text = dict()

        # Load the yaml configuration file
        with open("./app/cure/static/options.yaml", "r") as f:
            self.options = yaml.safe_load(f)
        self.params = self.options["standard"]

        # Change standard parameters for this specific model
        if self.model in self.options:
            for opt in self.options[self.model]:
                self.params[opt] = self.options[self.model][opt]

        self.params["model"] = self.model
        self.params["lang"] = self.lang
        self.params["annotation"] = self.annotation
        self.params["threshold"] = self.threshold
        self.params["window"] = self.window
        self.params["distance"] = self.distance
    
    @staticmethod
    def containsAny(seq, aset):
        return True if any(i in seq for i in aset) else False

    @staticmethod
    def group_filter(df, filter_words):
        group_candidates = list(df["pred"].unique())

        df["selected"] = False
        
        for group_number in group_candidates:
            tc, hc = 1e-5, 0
            for instance in df[df["pred"] == group_number].itertuples():
                tweet = instance.text
                if tweet and TweetsCluster.containsAny(tweet, filter_words):
                    hc += 1
                tc += 1
            proportion = hc / tc

            if proportion > 0.1:
                df.loc[df["pred"] == group_number, "selected"] = True
        
        return df

    @staticmethod
    def embedding_process(df, embeddings):
        # Manifold Compression
        plot = TSNE(n_components=2, learning_rate='auto', init='random').fit_transform(embeddings.A)

        # Sparse Embedding to Dense Embedding
        df["embedding"] = pd.Series([row.tolist() for row in embeddings.A])
        df["plot"] = pd.Series([row.tolist() for row in plot])
        
        return df

    def cluster(self, folder_name, date):
        input_file = f"./app/cure/static/data/{folder_name}/{date}_converted.tsv"
        output_file = f"./app/cure/static/data/{folder_name}/{date}_clustered.tsv"

        self.params["dataset"] = input_file

        X, data = build_matrix(**self.params)

        self.params["window"] = int(data.groupby("date").size().mean() * self.params["window"] / 24 // self.params["batch_size"] * self.params["batch_size"])
        threshold = self.params["threshold"]

        if self.params["model"].startswith("tfidf") and self.params["distance"] == "cosine":
            clustering = ClusteringAlgoSparse(threshold=float(threshold), window_size=self.params["window"], 
                                              batch_size=self.params["batch_size"], intel_mkl=False)
        else:
            clustering = ClusteringAlgo(threshold=float(threshold), window_size=self.params["window"],
                                        batch_size=self.params["batch_size"], distance=self.params["distance"])

        clustering.add_vectors(X)
        y_pred = clustering.incremental_clustering()
        stats = general_statistics(y_pred)
        p, r, f1 = cluster_event_match(data, y_pred)

        data["pred"] = data["pred"].astype(int)
        data["id"] = data["id"].astype(int)

        # Add embeddings to the columns
        data = TweetsCluster.embedding_process(data, X)

        candidate_columns = ["date", "time", "label", "pred", "user_id_str", "id", "embedding", "plot"]
        result_columns = []

        for rc in candidate_columns:
            if rc in data.columns:
                result_columns.append(rc)

        data[result_columns].to_csv(output_file, index=False, sep="\t", quoting=csv.QUOTE_NONE)
    
    def filter(self, folder_name, date):
        cluster_file = f"./app/cure/static/data/{folder_name}/{date}_clustered.tsv"
        tweets_file = f"./app/cure/static/data/{folder_name}/{date}_converted.tsv"
        output_file = f"./app/cure/static/data/{folder_name}/{date}_filtered.tsv"

        # Merge dataframes
        cluster_df = pd.read_csv(cluster_file, sep='\t')
        tweets_df = pd.read_csv(tweets_file, sep='\t', keep_default_na=False)
        merged_df = pd.merge(cluster_df, tweets_df, on='id')

        merged_df = TweetsCluster.group_filter(merged_df, self.filter_words)
        # merged_df[merged_df["selected"] == True].to_csv(output_file, index=False, sep="\t", quoting=csv.QUOTE_NONE)
        merged_df.to_csv(output_file, index=False, sep="\t", quoting=csv.QUOTE_NONE)

if __name__ == "__main__":
    tc = TweetsCluster()
    tc.cluster("alzheimers_tweets", "2022-07-12")
    tc.filter("alzheimers_tweets", "2022-07-12")





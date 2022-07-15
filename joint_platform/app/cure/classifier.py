# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-12
# Email: mingzhe@nus.edu.sg

import time
import pandas as pd
from transformers import AutoTokenizer, T5ForConditionalGeneration


class TweetClassifier(object):
    def __init__(self, callback):
        print("[CURE Model] Model init...")
        self.model_path = "./app/cure/static/model"
        self.tokenizer = AutoTokenizer.from_pretrained("t5-large", model_max_length=512)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
        self.callback = callback
        print("[CURE Model] Model init successfully!")

    def classify(self, tweet_text):
        tweet_text = TweetClassifier.normalize_tweet(tweet_text)
        time.sleep(1)
        op = self.run_model(tweet_text)
        return op[0]
    
    def run_model(self, input_string, **generator_args):
        input_ids = self.tokenizer.encode(input_string, return_tensors="pt")
        res = self.model.generate(input_ids, **generator_args)
        return self.tokenizer.batch_decode(res, skip_special_tokens=True)

    @staticmethod
    def normalize_tweet(orgtweet):
        words2 = str(orgtweet).lower().split()
        ftweet=""
        for word in words2:
            if word.startswith("@") or \
                word.startswith("https"):
                continue
            else:
                ftweet+=" "+word.replace("#","")

        return ftweet.strip()

    def process(self, folder_name, date, socketio, client_id):
        input_file = f"./app/cure/static/data/{folder_name}/{date}_filtered.tsv"
        output_file = f"./app/cure/static/data/{folder_name}/{date}_classified.tsv"

        tweets_df = pd.read_csv(input_file, sep='\t')

        check_worthy_list = list()

        for instance in list(tweets_df.itertuples()):
            result = False
            if instance.selected:
                result = self.classify(instance.text)
                self.callback(result, instance.text, socketio, client_id)

            check_worthy_list += [result]

        tweets_df['check_worthy'] = check_worthy_list

        with open(output_file, 'w') as write_tsv:
            write_tsv.write(tweets_df.to_csv(sep='\t', index=False))
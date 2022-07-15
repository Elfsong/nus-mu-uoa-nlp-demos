# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-08
# Email: mingzhe@nus.edu.sg


from doctest import OutputChecker
import os
import re
import sys
import csv
import json
import emoji
import string
import numpy as np
import pandas as pd
from emot.emo_unicode import UNICODE_EMOJI, EMOTICONS_EMO

# Fields needed for next steps
fields = [
    'created_at',
    'id',
    'id_str',
    'text',
    'geo',
    'coordinates',
    'place',
    'retweet_count',
    'favorite_count',
    'retweeted',
    'lang',
    'extended_tweet.full_text',
]


class TweetProcessor(object):
    def __init__(self):
        self.fields = fields
        self.preprocess_pipeline = True

    @staticmethod
    def remove_emoticons(text):
        emoticon_pattern = re.compile(
            u'(' + u'|'.join(k for k in EMOTICONS_EMO) + u')')
        return emoticon_pattern.sub(r'', text)

    @staticmethod
    def remove_emoji(text):
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

    @staticmethod
    def remove_urls(text):
        result = re.sub(r"http\S+", "", text)
        return(result)

    @staticmethod
    def remove_twitter_urls(text):
        clean = re.sub(r"pic.twitter\S+", "", text)
        return(clean)

    @staticmethod
    def give_emoji_free_text(text):
        return emoji.replace_emoji(text, replace='')

    @staticmethod
    def normalize_tweet(orginal_tweet):
        words2 = orginal_tweet.lower().split()
        ftweet = ""
        for word in words2:
            if word.startswith("@") or word.startswith("https"):
                continue
            else:
                ftweet += " " + word.replace("#", "")
        return ftweet.strip()

    def preprocess(self, folder_name, date):
        input_file_name = f"./app/cure/static/data/{folder_name}/{date}_original.json"
        output_file_name = f"./app/cure/static/data/{folder_name}/{date}_preprocessed.tsv"

        with open(input_file_name, 'r') as f:
            data = [json.loads(line) for line in f.readlines()]

        tweet_df = pd.json_normalize(data)
        tweet_df = tweet_df.loc[:, tweet_df.columns.isin(fields)]

        tweet_df.loc[tweet_df["extended_tweet.full_text"].isnull(), "extended_tweet.full_text"] = tweet_df["text"]
        tweet_df.rename(columns={'extended_tweet.full_text':'full_text'}, inplace = True)

        # tweet_df['original_text'] = tweet_df['full_text']

        tweet_df['full_text'] = tweet_df['full_text'].str.replace('\n', ' ')
        tweet_df['full_text'] = tweet_df['full_text'].str.replace('\r', ' ')
        tweet_df['full_text'] = tweet_df['full_text'].str.replace('\"', '')
        tweet_df['full_text'] = tweet_df['full_text'].str.replace('\'', '')

        if self.preprocess_pipeline:
            tweet_df['full_text'] = tweet_df['full_text'].apply(lambda x: TweetProcessor.remove_urls(x))
            tweet_df['full_text'] = tweet_df['full_text'].apply(lambda x: TweetProcessor.remove_twitter_urls(x))
            tweet_df['full_text'] = tweet_df['full_text'].apply(lambda x: TweetProcessor.remove_emoji(x))
            tweet_df['full_text'] = tweet_df['full_text'].apply(lambda x: TweetProcessor.give_emoji_free_text(x))
            tweet_df['full_text'] = tweet_df['full_text'].apply(lambda x: TweetProcessor.normalize_tweet(x))

        with open(output_file_name, 'w') as write_tsv:
            write_tsv.write(tweet_df.to_csv(sep='\t', index=False))
    
    def convert(self, folder_name, date):
        input_file_name = f"./app/cure/static/data/{folder_name}/{date}_preprocessed.tsv"
        output_file_name = f"./app/cure/static/data/{folder_name}/{date}_converted.tsv"

        tweet_df = pd.read_csv(input_file_name, sep='\t')

        # Construct a new DataFrame
        converted_df = pd.DataFrame(columns=['id', 'label', 'text', 'created_at'])
        converted_df['id'] = tweet_df['id']
        converted_df['label'] = 0
        converted_df['text'] = tweet_df['full_text']
        converted_df['created_at'] = tweet_df['created_at']

        with open(output_file_name, 'w') as write_tsv:
            write_tsv.write(converted_df.to_csv(sep='\t', index=False))

if __name__ == '__main__':
    tp = TweetProcessor()
    tp.preprocess("alzheimers_tweets", "2022-07-12")
    tp.convert("alzheimers_tweets", "2022-07-12")

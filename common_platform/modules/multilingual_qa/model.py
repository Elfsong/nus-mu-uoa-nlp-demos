# -*- coding: utf-8 -*-
# Author: Mingzhe Du (mingzhe@nus.edu.sg)
# Date: 2022-03-12

import nltk
import json
import torch
import numpy as np
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize  
from sklearn.feature_extraction.text import TfidfVectorizer

from transformers.pipelines import pipeline
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

class TFIDF_proxy(object):
    def __init__(self):
        # TF-IDF Hyperparameters
        self.top_k = 3
        self.min_gram = 1
        self.max_gram = 2
        
        self.wordnet_lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        self.vectorizer = TfidfVectorizer(ngram_range=(self.min_gram, self.max_gram))
    
    def preprocess(self, text, language):
        text = text.replace('/', ' / ')
        text = text.replace('.-', ' .- ')
        text = text.replace('.', ' . ')
        text = text.replace('\'', ' \' ')
        text = text.lower()

        if (language == "EN"):
            # Tokenization
            tokens = [token for token in word_tokenize(text) if token not in punctuation and token not in self.stop_words]
            # Lemmatization
            tokens = [self.wordnet_lemmatizer.lemmatize(token) for token in tokens]
            text =  " ".join(tokens)

        return text

    def get_doc_vectors(self, docs, language):
        doc_vectors = self.vectorizer.fit_transform([self.preprocess(doc, language) for doc in docs])
        return doc_vectors
    
    def get_query_vector(self, query, language):
        query_vector = self.vectorizer.transform([self.preprocess(query, language)]).todense()
        return query_vector

    def rank(self, docs, query, language):
        doc_vectors = self.get_doc_vectors(docs, language)
        query_vector = self.get_query_vector(query, language)

        doc_scores = np.asarray(doc_vectors @ query_vector.T).squeeze()
        doc_indices_rank = doc_scores.argsort()[::-1].tolist()

        return [docs[index] for index in doc_indices_rank]
    
    def rank_vector(self, doc_vectors, query_vector):
        doc_scores = np.asarray(doc_vectors @ query_vector.T).squeeze()
        doc_indices_rank = doc_scores.argsort()[::-1].tolist()

        return doc_indices_rank

class QAProxy(object):
    def __init__(self):
        self.model_map = {
            "EN": {
                "model_name": "zhufy/squad-en-bert-base",
                "tokenizer_name": "zhufy/squad-en-bert-base"
            },
            "MS": {
                "model_name": "zhufy/squad-ms-bert-base",
                "tokenizer_name": "zhufy/squad-ms-bert-base"
            },
            "TH": {
                "model_name": "zhufy/xquad-th-mbert-base",
                "tokenizer_name": "zhufy/xquad-th-mbert-base"
            },
            "MI": {
                "model_name": "twmkn9/bert-base-uncased-squad2",
                "tokenizer_name": "twmkn9/bert-base-uncased-squad2"
            }
        }

        for language in self.model_map:
            print("[+] initializing config [%s] ..." % language)
            config = self.model_map[language]
            print("[-] initializing model [%s] ..." % config["model_name"])
            self.model_map[language]["model"] = AutoModelForQuestionAnswering.from_pretrained(config["model_name"])
            print("[-] initializing tokenizer [%s] ..." % config["tokenizer_name"])
            self.model_map[language]["tokenizer"] = AutoTokenizer.from_pretrained(config["tokenizer_name"])
        print("[*] Initialization Finished")

    def question_answering(self, language, passage, question):
        if language in ["EN", "MS", "TH", "MI"]:
            model = self.model_map[language]["model"]
            tokenizer = self.model_map[language]["tokenizer"]
        else:
            return "Not supported Language"

        # old-school way
        # input_text = "[CLS] " + question + " [SEP] " + passage + " [SEP]"

        # if len(input_text) >= 512:
        #     return "passage exceeds 512 tokens"

        # input_ids = tokenizer.encode(input_text, add_special_tokens=False)

        # token_type_ids = [0 if i <= input_ids.index(102) else 1 for i in range(len(input_ids))]
        # start_scores, end_scores = model(torch.tensor([input_ids]), 
        #                                  token_type_ids=torch.tensor([token_type_ids]), 
        #                                  return_dict=False)
        # all_tokens = tokenizer.convert_ids_to_tokens(input_ids)

        # answer_start = torch.argmax(start_scores)
        # answer_end = torch.argmax(end_scores)
        # answer = all_tokens[answer_start]

        # for i in range(answer_start + 1, answer_end + 1):
        #     # If it's a subword token, then recombine it with the previous token.
        #     if all_tokens[i][0:2] == '##':
        #         answer += all_tokens[i][2:]
        #     # Otherwise, add a space then the token.
        #     else:
        #         answer += ' ' + all_tokens[i]

        # return answer

        # New wave
        nlp_model = pipeline("question-answering", model=model, tokenizer=tokenizer)
        inputs = {"question": question, "context":passage }
        output = nlp_model(inputs)

        return output["answer"]

class MultilingualQAModel(object):
    def __init__(self):
        self.qa_proxy = QAProxy()
        self.tf_idf_proxy = TFIDF_proxy()

        # language documents
        self.corpus = dict()
        self.set_corpus()
    
    def set_corpus(self):
        print("[+] Loding [EN] corpus...")
        self.corpus["EN"] = dict()
        docs, vectors = self.get_corpus("modules/multilingual_qa/static/data/EnglishDocuments.json", "EN")
        self.corpus["EN"]["docs"] = docs
        self.corpus["EN"]["vectors"] = vectors

        print("[+] Loding [MS] corpus...")
        self.corpus["MS"] = dict()
        docs, vectors = self.get_corpus("modules/multilingual_qa/static/data/MalayDocuments.json", "MS")
        self.corpus["MS"]["docs"] = docs
        self.corpus["MS"]["vectors"] = vectors

        print("[+] Loding [TH] corpus...")
        self.corpus["TH"] = dict()
        docs, vectors = self.get_corpus("modules/multilingual_qa/static/data/ThaiDocuments.json", "TH")
        self.corpus["TH"]["docs"] = docs
        self.corpus["TH"]["vectors"] = vectors

        print("[*] Corpus loaded successfully")
    
    def get_corpus(self, file_path, language):
        with open(file_path, "r", encoding="utf-8") as f:
            docs = json.loads(f.readline())
            processed_docs = ["\n\n".join(docs[doc_id]["passages"]) for doc_id in docs]
            doc_vectors = self.tf_idf_proxy.get_doc_vectors(processed_docs, language)
        return processed_docs, doc_vectors

    def document_retrieval(self, language, context, question, result):
        if context == "":
            docs = self.corpus[language]["docs"]
            doc = self.tf_idf_proxy.rank(docs, question, language)[0]
            result["document"] = [doc]
        else:
            result["document"] = [context]

    def passage_retrieval(self, language, context, question, result):
        context_segments = result["document"][0].split('\n\n')
        ranked_result = self.tf_idf_proxy.rank(context_segments, question, language)
        result["passages"] = [ranked_result[0]]

    def question_answering(self, language, context, question, result):
        answer = self.qa_proxy.question_answering(language, result["passages"][0], question)
        result["answer"] = answer

if __name__ == "__main__":
    broker = MultilingualQAModel()

    result = {}

    broker.document_retrieval('EN', "", "Computational complexity theory is a branch of the theory of computation in theoretical computer science that focuses on classifying computational problems according to their inherent difficulty", result)
    # broker.passage_retrieval('EN', context, question, result)
    # broker.question_answering('TH', context, question, result)

    # print(result)
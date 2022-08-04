# coding: utf-8

# Author: Ang Beng Heng
# Date: 2022-08-03
# Email: bengheng.ang@u.nus.edu

import re
import torch
import random
import numpy as np
from jury import Jury
from time import time
from nltk import word_tokenize
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
from transformers import T5Tokenizer, T5ForConditionalGeneration


# Check if CUDA is available
if torch.cuda.is_available():
    device = torch.device("cuda:0")
else:
    device = torch.device("cpu")

class QG_Model(object):
    def __init__(self) -> None:
        print("[+] Loading T5 model...")
        self.tokenizer = T5Tokenizer.from_pretrained("./app/socratic_qg/static/model/")
        self.model = T5ForConditionalGeneration.from_pretrained("./app/socratic_qg/static/model/")
        self.model.eval()
        self.model.to(device)
        print("[*] Loading T5 model successfully!")

        print("[+] Loading bleu...")
        self.bleu = Jury(metrics = ["bleu"])
        print("[*] Loading bleu successfully!")
        
        print("[+] Loading SentenceTransformer...")
        self.model_sbert = SentenceTransformer('./app/socratic_qg/static/sbert_model/', device=device)
        self.model_sbert.eval()
        print("[*] Loading SentenceTransformer successfully!")

        # Configuration
        self.max_length = 300
        self.top_rank = 3
        self.top_p = 0.55
        self.top_k = 3
        
        self.labels = ["alternative_perspectives_viewpoints", "implications_consequences", "clarity", "assumptions", "reasons_evidence"]
        self.repetition_penalties = [2.4, 2.4, 0.8, 1.2, 1.2]
        self.temperatures = [0.8, 0.8, 0.8, 2.4, 0.8]
        self.sample_sizes = [5,5,5,5,5]
    
    def precision_bleu(self, context, question, score_type = "bleu"):
        output = self.bleu(predictions=[question], references=[context])[score_type]
        return round(output["precisions"][1],3)

    def predict_sbert(self, text1s, text2):
        encode1s = self.model_sbert.encode(text1s, convert_to_tensor=True)
        encode2 = self.model_sbert.encode(text2, convert_to_tensor=True)
        output = util.cos_sim(encode1s, encode2).reshape(-1,).tolist()
        output = [round(score, 3) for score in output]
        return output

    def ranking(self, texts, context, top = 3, rand=False):
        if not rand:
            scores = np.array(self.predict_sbert(texts, context))
            inds = scores.argsort()[-top:]
            return inds.tolist()
        else:
            return np.random.choice(list(range(len(texts))), size = top, replace=False).tolist()

    def generate(self, label="", context="",  min_length=10, sample_size=3, repetition_penalty=1.2, temperature=1.0):
        tokenized_input = self.tokenizer.encode(f"{label}: {context}", return_tensors="pt").to(device)

        with torch.no_grad():
            generated_ids = self.model.generate(tokenized_input, 
                                                max_length=self.max_length, 
                                                min_length=min_length,
                                                do_sample=True, 
                                                top_k=self.top_k, 
                                                top_p=self.top_p, 
                                                num_return_sequences=sample_size, 
                                                repetition_penalty=repetition_penalty, 
                                                temperature=temperature, 
                                                early_stopping=True)

        pred = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in generated_ids]

        questions = []
        for prediction in pred:
            questions.append(re.findall("[A-Z][\w\s,\']+\?", prediction)[0])
        questions = [question for question in questions if len(word_tokenize(question)) != 1]
            
        tmp_output = []
        if label == "alternative_perspectives_viewpoints" or  label == "implications_consequences":
            for question in questions:
                tmp_question = question.replace("What about", "").replace("?", "").replace(",", "").replace("Are you implying that", "")
                tmp_question_tokenized = word_tokenize(tmp_question)
                if self.precision_bleu(context.lower(), tmp_question.lower()) > 0.55 or len(tmp_question_tokenized) == 1:
                    continue
                else:
                    tmp_output.append(question)
            questions = tmp_output 
            
        og_questions = list(set(questions))
        if label in ["alternative_perspectives_viewpoints", "clarity", "assumptions", "reasons_evidence", "implications_consequences"]:
            selected_indices = self.ranking(og_questions, context, top=self.top_rank)
        else:
            selected_indices = self.ranking(og_questions, context, top=self.top_rank, rand=True)  
        questions = [og_questions[ind] for ind in selected_indices]

        return questions
    
    def generate_all_labels(self, context):
        result = dict()

        for label, repetition_penalty, temperature, sample_size in zip(self.labels, self.repetition_penalties, self.temperatures, self.sample_sizes):       
            result[label] =  self.generate(label = label, context=context, sample_size=sample_size, repetition_penalty=repetition_penalty, temperature=temperature)
            
        return result

    
if __name__ == "__main__":
    qg = QG_Model()
    result = qg.generate_all_labels("I know you won't believe me, but the highest form of human excellence is to question oneself and others.")
    print(result)
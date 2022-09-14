#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 14:57:47 2022

@author: sdas
"""
from transformers import AutoTokenizer, T5ForConditionalGeneration
from sentence_transformers import SentenceTransformer
from sentence_transformers import util as stutil
from transformers import pipeline
import numpy as np
import stanza
import string


questions_classcues_f="./app/artquest2/static/data/refq_qtype_engq.map.txt"
sent_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
eqg_tokenizer=AutoTokenizer.from_pretrained("t5-large")
eqg_model = T5ForConditionalGeneration.from_pretrained("./app/artquest2/static/data/model/")
nlp = stanza.Pipeline(lang='en', use_gpu=False, processors='tokenize,pos,ner')

nerlist=["PERSON", "NORP", "LOC", "ORG",
         "GPE", "FAC", "PRODUCT",\
         "EVENT", "WORK_OF_ART", "LANGUAGE"]

## ARTQUEST OPENING/CLOSING SESSION CUES
opening_cues = [
    "Do you like the painting?", 
    "What catches your eye about this painting?", 
    "How do you like this painting?", 
    "What you like the most about this painting?"
]

qae_messages = [
    "Wonderful chatting with you, Goodbye!",
    "Thank you for chatting with ArtQuest!", 
    "Hope you enjoyed our chat, bye now!",
    "B-bye, hope to see you again!",
    "Bye, hope you had fun!"
]

## RELATED TO SENTENCE/QUESTION MAPPING BASED ON SIMILARITY
def getEmbeddings(plines):
    embedding_2 = sent_model.encode(plines, convert_to_tensor=True)
    return embedding_2

def getBestMatch(sentence, embedding_2):
    embedding_1= sent_model.encode(sentence, convert_to_tensor=True)
    simvals = stutil.pytorch_cos_sim(embedding_1, embedding_2).cpu().detach().numpy()
    indx = np.argmax(simvals)
    return indx

def getSimilarities(sentence, embedding_2):
    embedding_1= sent_model.encode(sentence, convert_to_tensor=True)
    simvals = stutil.pytorch_cos_sim(embedding_1, embedding_2).cpu().detach().numpy()
    #print (type(simvals))
    #print (len(simvals[0]))
    return simvals[0]

def getQuestionEmbeddings2():
    q2qc={}
    questions=[]
    lines=open(questions_classcues_f, "r").readlines()
    for line in lines:
        lp = line.strip().split("\t")
        q = lp[0].strip()
        qc = lp[1].strip()
        questions.append(q)
        q2qc[q] = qc
        
    # print ("#questions "+str(len(questions)))
    embedding_2 = sent_model.encode(questions, convert_to_tensor=True)
    
    return q2qc, embedding_2, questions

def generate_engaging_question(input_string, **generator_args):
    input_ids = eqg_tokenizer.encode(input_string, return_tensors="pt")
    res = eqg_model.generate(input_ids, **generator_args)
    return eqg_tokenizer.batch_decode(res, skip_special_tokens=True)[0]

def getWordsPOSNER(text):
    sentwords = []
    postags = []
    entities = []
    tagged = nlp (text)
    
    for sentence in tagged.sentences:
        for token in sentence.tokens:
           
            word = token.words[0]
            
            sentwords.append (word.text)
            postags.append (word.upos)
            
    
    for entity in tagged.entities:
        if entity.type in nerlist:
            entities.append(entity.text)
    
    return sentwords, postags, entities

def getNPs(words, postags):
     kp_tags=[]
     
     for wx, word in enumerate(words):
         if (postags[wx]=="NOUN" or postags[wx]=="ADJ"):
             if wx==0 or (postags[wx-1]!="NOUN" \
                          and postags[wx-1]!="ADJ"
                          and postags[wx-1]!="ADP"
                          and postags[wx-1]!="CCONJ") :
                kp_tags.append('B-KP')
             else:
                kp_tags.append('I-KP')
         elif (postags[wx]=="CCONJ" or postags[wx]=="ADP" ) and (wx<len(words)-1) and \
            (postags[wx+1]=="NOUN" ):
            kp_tags.append('I-KP')
         else:
            kp_tags.append('O')

     kpzones=[]
     covered=-1
     for wx, word in enumerate(words):
        
         if covered!=-1 and wx<covered:
             continue
        
         if kp_tags[wx].startswith("B"):
             temp = word
           
             for wx2 in range(wx+1, len(words)):
                 if kp_tags[wx2]!="O":
                     temp+=" "+words[wx2]
                 else:
                     break
            
             temp = temp.strip()
             kpzones.append(temp)
             covered = wx + len(temp.split())
            #print ("\n"+temp)

     return kpzones

def getGenericAZs(text):
    w, p, e = getWordsPOSNER(text)
    kpzones = getNPs(w, p)
    if len(kpzones)==0:
        for px, ptag in enumerate(p):
            if ptag=="NOUN" or ptag=="ADV" or ptag=="ADV":
                kpzones.append(w[px])
    return kpzones, e
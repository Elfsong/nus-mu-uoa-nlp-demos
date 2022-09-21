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
import os
import stanza
import string
import numpy as np
import time
import torch

questions_classcues_f="./app/artquest3/static/data/refq_qtype_engq.map.txt"
sent_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
device = "cuda:2" if torch.cuda.is_available() else "cpu"
eqg_tokenizer=AutoTokenizer.from_pretrained("t5-large",local_files_only=True)
eqg_model = T5ForConditionalGeneration.from_pretrained("./app/artquest3/static/data/model/")
eqg_model.to(device)
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,ner')


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
    qc2cues={}
    questions=[]
    lines=open(questions_classcues_f, "r").readlines()
    for line in lines:
        lp = line.strip().split("\t")
        q = lp[0].strip()
        qc = lp[1].strip()
        eq = lp[2].strip()
        questions.append(q)
        q2qc[q] = qc
        if qc not in qc2cues:
            qc2cues[qc]=[]
        qc2cues[qc].append(eq)
        
    print ("#questions "+str(len(questions)))
    print ("#qc2cues:"+str(len(qc2cues)))
    embedding_2 = sent_model.encode(questions, convert_to_tensor=True)
    
    return q2qc, embedding_2, questions, qc2cues

def getFirstSentence(text):
    tagged = nlp(text)
    first=""
    sentence =tagged.sentences[0]
    for word in sentence.words:
        first += " "+word.text.strip()
    return first.strip()

def generate_engaging_question(input_string, **generator_args):
    input_ids = eqg_tokenizer.encode(input_string, return_tensors="pt").to(device)
    
    res = eqg_model.generate(input_ids, **generator_args)
    temp = eqg_tokenizer.batch_decode(res, skip_special_tokens=True)[0]
    temp = temp.replace(":","").replace("ArtQuest","").replace("Viewer","").replace("[SEP]","").strip()
    return temp

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

def getQuestions(nerspans_all):
    questions={}
    for nertag in nerspans_all:
        nerspans = nerspans_all[nertag]
        
        for nerspan in nerspans:
            if nertag=="PERSON":
                q="Have you heard of "+nerspan+" before ?"
                questions[q]=nerspan
                q="Do you know "+nerspan+" ?"
                questions[q]=nerspan
            if nertag=="DATE" or nertag=="TIME":
                q="Can you imagine how things were during "+nerspan+" ?"
                questions[q]=nerspan
                q="Would you have liked living during "+nerspan+" ?"
                questions[q]=nerspan
            if nertag=="GPE":
                q="Would you have liked living in "+nerspan+" ?"
                questions[q]=nerspan
                q="Have you been to "+nerspan+" before ?"
                questions[q]=nerspan
                q="Did you visit "+nerspan+" any time?"
                questions[q]=nerspan
                q="Would you like to travel to "+nerspan+" ?"
                questions[q]=nerspan
            if nertag=="LOC":
                q="Do you like "+nerspan+" ?"
                questions[q]=nerspan
                q="I love "+nerspan+" , how about you ?"
                questions[q]=nerspan
                q="Have you seen a "+nerspan+" any time ?"
                questions[q]=nerspan
            if nertag=="FAC" or nertag=="ORG":
                q="Have you been to "+nerspan+" any time ?"
                questions[q]=nerspan
                q="Would you like to see "+nerspan+" any time ?"
                questions[q]=nerspan
            if nertag=="NORP":
                q="Do you know anybody belonging to "+nerspan+" ?"
                questions[q]=nerspan
                q="I do not know anybody from "+nerspan+" , how about you?"
                questions[q]=nerspan
            if nertag=="EVENT":
                q="Do you know about "+nerspan+" ?"
                questions[q]=nerspan
                q="Have you heard about "+nerspan+" ?"
                questions[q]=nerspan
            if nertag=="WORK_OF_ART": 
                q="Do you like "+nerspan+" ?"
                questions[q]=nerspan
                q="Have you heard about "+nerspan+" ?"
                questions[q]=nerspan
            if nertag=="PRODUCT":
                q="Have you heard about "+nerspan+" ?"
                questions[q]=nerspan
                q="Have you used "+nerspan+" any time ?"
                questions[q]=nerspan
            if nertag=="LANGUAGE":
                q="Can you speak "+nerspan+" ?"
                questions[q]=nerspan
                q="Can you understand "+nerspan+" ?"
                questions[q]=nerspan
                q="What languages can you speak, do you know "+nerspan+" ?"
                questions[q]=nerspan
                
    return questions

def getNERSpans(text): 

    ner={}
    tagged = nlp (text)
    for entity in tagged.entities:
        nertag = entity.type
        nerspan = entity.text
        if nertag not in ner:
            ner[nertag] = []
        ner[nertag].append(nerspan)
   
    return ner     

def getNERQuestions(text):

    nerspans = getNERSpans(text)
    return getQuestions(nerspans)
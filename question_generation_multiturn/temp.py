#!/usr/bin/env python
# coding: utf-8


import json
import torch
import torch.nn as nn
from tqdm import tqdm
from pathlib import Path
from datasets import load_dataset
from collections import defaultdict, OrderedDict
from torch.utils.data import DataLoader, Dataset
from transformers import AdamW, get_linear_schedule_with_warmup
from transformers import AutoTokenizer, T5ForConditionalGeneration
import tensorflow as tf
from tensorboardX import SummaryWriter

# Utility functions
import util


# # Global Settings

# In[42]:


# Global variables
k_name = "unifiedQA"
k_banner = "Developed by Mingzhe Du"
k_model = "t5-large"
k_seed = 42
k_max_src_len = 512
k_max_tgt_len = 20
k_batch_size = 4



def run_model(input_string, **generator_args):
    input_ids = tokenizer.encode(input_string, return_tensors="pt")
    res = model.generate(input_ids, **generator_args)
    return tokenizer.batch_decode(res, skip_special_tokens=True)


modeldir="./persona/unifiedQA-01/model/" #./squad-qc/unifiedQA-03/model"
tokenizer = AutoTokenizer.from_pretrained("t5-large")
model = T5ForConditionalGeneration.from_pretrained(modeldir)
#device="cuda:3"
#model.to(device)


#print (op)

personas=[
"PERSONA:  i like to remodel homes. i like to go hunting. i like to shoot a bow. my favorite holiday is halloween. ",\
"PERSONA:  This is a painting \'Family Portrait\'. Family Portrait depicts the Chen family (no relation), Chen’s long-time friends and neighbours when she was living in Penang. Pauline Chen is posed at the centre of this portrait dressed in a plaid cheongsam. Her husband, Chen Fah Shin, gazes past her shoulder at the newspaper",\
#"PERSONA: Rohani was a student of Chen's at the Nanyang Academy of Fine Arts (NAFA). She was also a friend beyond the classroom. Here, she is vibrantly clothed in a matching red dress and headscarf, accessorised with a delicate gold pin in the shape of an R. Chen often drove Rohani home after school, as both lived around Siglap.",\
"PERSONA: This is a painting showing Rohani. The painting was made by Georgette Chen. Rohani was a student of Chen's at the Nanyang Academy of Fine Arts (NAFA). She was also a friend beyond the classroom. Here, she is vibrantly clothed in a matching red dress and headscarf. She is also wearing an accessory, a delicate gold pin in the shape of an R. Chen often drove Rohani home after school, as both lived around Siglap."
]

for psx, persona in enumerate(personas):

    prev_inp=""
    prefix_string=persona
    print("-----------------------")
    print("T5 "+prefix_string)
    print("-----------------------")
    turn=0
    while True:
        print ("\nTurn-"+str(turn))##+"\n\nChat History:"+prev_inp+"\n\n")
        print ("--------------------------") 
        input_var = input("Enter Response/exit to quit: ")
        if input_var=="exit":
            break

     #   print ("You entered " + input_var) 
        inp_string = prefix_string+prev_inp+" GSDAS2: "+input_var
        op = run_model(inp_string)
        if len(op)>0:
            print ("T5 response: "+str(op[0]))
            prev_inp = (prev_inp+" GSDAS2: "+input_var+" GSDAS1: "+op[0]).strip()
            turn+=1
        else:
            break

    print ("Ending loop for persona-"+str(psx))

# -*- coding: utf-8 -*-
# Author: Mingzhe Du (mingzhe@nus.edu.sg)
# Date: 2022-03-12
import json
import torch
from tqdm import tqdm
from collections import defaultdict, OrderedDict
from transformers import AdamW, get_linear_schedule_with_warmup
from transformers import AutoTokenizer, T5ForConditionalGeneration


class Broker(object):
    def __init__(self, model_dir):
        print("Broker init... (It may take minutes, depending on the model size)")
        self.model_dir = model_dir
        self.tokenizer = AutoTokenizer.from_pretrained("t5-large")
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_dir)
    
    def construct_history(self, conversation_lines):
        history = [("GSDAS1: " if index % 2 else "GSDAS2: ") + line for index, line in enumerate(conversation_lines[2:])]
        print("HISTORY: " + " ".join(history))
        return " ".join(history)

    def question_generation(self, persona, conversation_lines):
        input_string = persona + self.construct_history(conversation_lines)

        input_ids = self.tokenizer.encode(input_string, return_tensors="pt")
        res = self.model.generate(input_ids)
        outputs = self.tokenizer.batch_decode(res, skip_special_tokens=True)

        output = outputs[0]
        return output


if __name__ == "__main__":
    broker = Broker("./static/data/persona")
    persona = "PERSONA:  i like to remodel homes. i like to go hunting. i like to shoot a bow. my favorite holiday is halloween."
    conversation_lines = ['Hello This is ArtQuest demo.', 'Ask me anything:)', 'How are you?', 'i like to dress up as a scary ghost this time of year', "How about to reconstruct your home?"]
    print(broker.construct_history(conversation_lines))
    result = broker.question_generation(persona, conversation_lines)
    print(result)
    




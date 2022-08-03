import re
import torch
import random
from jury import Jury
from nltk import word_tokenize
from transformers import T5Tokenizer, T5ForConditionalGeneration


class QGModel(object):
    def __init__(self) -> None:
        self.tokenizer = T5Tokenizer.from_pretrained("./app/socratic_qg/static/model/")
        self.model = T5ForConditionalGeneration.from_pretrained("./app/socratic_qg/static/model/")
        self.model.eval()
        self.bleu = Jury(metrics = ["bleu"])
        self.labels = ["alternative_perspectives_viewpoints", "implications_consequences", "clarity", "assumptions", "reasons_evidence"]
        self.sample_size = 5
        self.top_k = 3
        self.top_p = 0.9
        self.repetition_penalties = [2.4, 2.4, 0.8, 1.2, 1.2]
        self.temperatures = [0.8, 0.8, 0.8, 0.8, 0.8]

    def precision_bleu(self, context, question):
        output = self.bleu(predictions=[question], references=[context])["bleu"]
        return round(output["precisions"][1],3)

    def generate(self, label = "", context="",  min_length=10, top_k=3,  top_p=0.9,  sample_size=3, repetition_penalty=1.2, temperature=1.0):
        tokenized_input = self.tokenizer.encode(f"{label}: {context}", return_tensors="pt")

        with torch.no_grad():
            generated_ids = self.model.generate(tokenized_input, max_length = 300, min_length = min_length,
                                        do_sample=True, top_k= top_k, top_p=top_p,
                                        num_return_sequences = sample_size, repetition_penalty = repetition_penalty, temperature = temperature, early_stopping=True)

        pred = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True)  for g in generated_ids]

        questions = []
        for prediction in pred:
            questions.extend(re.findall("[A-Z][\w\s,\']+\?", prediction))

        questions = [question for question in questions if len(word_tokenize(question)) != 1]

        tmp_output = []
        if label == "alternative_perspectives_viewpoints":
            for question in questions:
                tmp_question = question.replace("What about", "").replace("?", "").replace(",", "")
                tmp_question_tokenized = word_tokenize(tmp_question)
                if self.precision_bleu(context, tmp_question) > 0.55 or len(tmp_question_tokenized) == 1:
                    continue
                else:
                    tmp_output.append(question)
            questions = tmp_output

        questions = list(set(questions))
        return questions

    def generate_all_labels(self, context):
        result = dict()
        for label, repetition_penalty, temperature in zip(self.labels, self.repetition_penalties, self.temperatures):
            result[label] = self.generate(label=label, context=context, sample_size=self.sample_size, repetition_penalty=repetition_penalty, temperature = temperature, top_p=self.top_p, top_k=self.top_k)
        return result
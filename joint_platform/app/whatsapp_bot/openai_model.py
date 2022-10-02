# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

import os
from click import prompt
import openai

# OpenAI handler
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_generate(content, temperature=0.0, max_tokens=128, top_p=1):
    try:
        responses = openai.Completion.create(
            model="text-davinci-002", 
            prompt=content, 
            temperature=temperature, 
            max_tokens=max_tokens, 
            top_p=top_p
        )

        print("=" * 80)
        # print(content)
        print("original output:", responses)
        print("=" * 80)

        response = responses.choices[0]

        # Parse Response
        if response.finish_reason == "length":
            answer = ".".join(response.text.split(".")[:-2]) + "."
        else:
            answer = response.text

        answer = answer.strip()

        return answer
    except Exception as e:
        print(f"ERROR: {e}")
        return "Sorry, I have a problem. Call Mingzhe to fix me."


def product_mentions(sentence):
    try:
        prompt = f"Given the context: {sentence} \nList all mentioned products using bulletpoints:"
        response = openai_generate(prompt, max_tokens=64)
        
        return [e.strip()[1:] for e in response.split("\n") if e.strip()]
    except Exception as e:
        print(f"ERROR: {e}")
        return []
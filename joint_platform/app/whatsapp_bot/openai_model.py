# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

import os
import string
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

        print("OPENAI => $$$$$")

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
        prompt = f"Given the context: {sentence}\nUsing bulletpoints to list all mentioned products in the context:"
        response = openai_generate(prompt, max_tokens=64)
        return [e.strip()[1:] for e in response.split("\n") if e.strip()]
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return []

def remove_punctuation(sentence):
    # return sentence.translate(str.maketrans('', '', string.punctuation))
    return sentence.replace('.', '')

def generate_conversation(history: list) -> str:
    conversation = ""
    for dialogue in history:
        conversation += f"{dialogue[0]}: {dialogue[1]}\n"
    return conversation

def ask_production_location_question(sentence, action) -> str:
    try:
        prompt = f"Given the context: {sentence} \nGenerate a question to ask the customer the {action}:"
        response = openai_generate(prompt, max_tokens=64)
        return response.strip()
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""

def understanding_production_location_answer(question, answer) -> str:
    try:
        prompt = f"Given the context: What is the {question}? {answer}.\nThe {question} is:"
        response = openai_generate(prompt, max_tokens=64)
        return response.strip()
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""

def generate_greeting_sentences(sentence: str) -> str:
    try:
        prompt = f"My name is AsiA. I am a very friendly Cisco tech support team crew. I will try my best to help our customers solve their problems.\nGiven the context: {sentence}\nGenerate a greeting message to introduce myself:"
        response = openai_generate(prompt, max_tokens=128)
        return response.strip()
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""

def generate_question_for_checklist(question: str, answer: str, options: list) -> str:
    try:
        option_str = ", ".join(options)
        prompt = f"Agent: What is {question}? {question} can be {option_str}\nCustomer: {answer}\nGiven the conversation, {question} is:"
        response = openai_generate(prompt, max_tokens=32)
        return response.strip()
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""

def get_answer_from_checklist_question(question: str, answer: str, options: list) -> str:
    try:
        option_str = ", ".join(options)
        prompt = f"Agent: What is {question}? {question} can be {option_str}\nCustomer: {answer}\nGiven the conversation, {question} is:"
        response = openai_generate(prompt, max_tokens=32)
        return remove_punctuation(response.strip())
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""

def problem_intent(question: str, options: list) -> str:
    try:
        options += ["unknown", "others"]
        option_str = "\n".join([f'query: {option}' for index, option in enumerate(options)])
        prompt = f"Given the query: {question}\n{option_str}\nThe most query one is:"
        response = openai_generate(prompt, max_tokens=32)
        return remove_punctuation(response.strip())
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""

def generate_response(context: list, history: list) -> str:
    try:
        context_str = "\n".join(context)
        history_str = generate_conversation(history)
        prompt = f"{context_str}\n{history_str}AsiA:"
        print(prompt)
        response = openai_generate(prompt, max_tokens=256)
        return response.strip()
    except Exception as e:
        print(f"OPENAI {__name__} ERROR: {e}")
        return ""



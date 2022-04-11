# Multimodal QA/QG Demo Application

Multimodal QA/QG Demo Application is a simple template (built with HTML + JavaScript + Bootstrap 5 + Python) that allows quick set-up for presenting QA/QG models to the audiences.

## Installation

The front-end of the web application is almost self-contained and ready for off-line running. All of the required files of the libraries are stored locally in minimised form. The only internet connection requirement is from Google font, but it will not affect the front-end from running.

The back-end requires `Flask` and `nltk`, where `Flask` is a lightweight web framework written in python and `nltk` is a toolkit for natural language processing tasks. 

- Flask: a lightweight web framework, version 2.0.1 is used in the project.  
`pip install flask==2.0.1`
- nltk: stands for Natural Language Toolkit. We use it to parse a whole chunk of string into arrays of sentences. This package is OPTIONAL if data pre-processing is not required by the prediction model. Version 3.6.2 is used in the project.   
`pip install nltk==3.6.2`  
NOTICE: nltk requires additional data for the sentence parsing task, please run the Python interpreter and type the following commands OR act according to the instruction of the error message:  
`>>> import nltk`  
`>>> nltk.download('punkt')` 

## Run the web app

Run the web application with following command:
```
python app.py
```
NOTICE 1: nltk requires additional data for the sentence parsing task, please run the Python interpreter and type the following commands OR act according to the instruction of the error message:  
```
>>> import nltk
>>> nltk.download('punkt')
```
Alternatively, run this command in the Terminal:
```
python -m nltk.downloader punkt
```
NOTICE 2: the server uses port 3000 by default. However, if the port is in use, the application will ask you to specifiy another port number in the range (0 - 65535).

Open any browser, type in the link (with the default or specified port number) and hit "Enter"
`localhost:3000`
OR
`127.0.0.1:3000`
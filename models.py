from pydantic import BaseModel
from utils import clean_text
from openai import OpenAI
import json
import streamlit as st


# Access the OpenAI API key from the secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Set up the OpenAI API client
client = OpenAI(api_key=api_key)


class QuizSample(BaseModel):
    question: str
    choices: list[str]
    answer: str

class Exam(BaseModel):
    quizes: list[QuizSample]

class BaseExtracter():

    def __init__(self):
        self.model_name = "gpt-4o-mini"

    def run(self, text):
        pass

class ExtractA(BaseExtracter):

    def run(self, _input):

        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                        TASK: Extract 10 questions of level A difficulty. Each question should be simple and straightforward, testing basic knowledge or comprehension skills.
                        Provide the output in the format of a list of dictionaries, where each dictionary has the following fields: question (the question text), choices (a list of 4 answer options), and answer (the correct answer from the choices).
                        Make sure the questions cover a variety of general knowledge topics.
                        RULE: questions, choices, and answers in Vietnamese.
                        """
                },
                {
                    "role": "user",
                    "content": f"base on this document: {clean_text(_input)}"
                },
            ],
            response_format=Exam,
        )
        res = json.loads(completion.choices[0].message.content)
        for i in range(len(res["quizes"])):
            res["quizes"][i]["level"] = "Dễ"
        return res


class ExtractB(BaseExtracter):

    def run(self, _input):

        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                        TASK: Extract 6 questions of level B difficulty. Each question should test understanding and the ability to explain or interpret information.
                        Provide the output in the format of a list of dictionaries, where each dictionary has the following fields: question (the question text), choices (a list of 4 answer options), and answer (the correct answer from the choices).
                        Make sure the questions cover a variety of general knowledge topics.
                        RULE: questions, choices, and answers in Vietnamese.
                        """
                },
                {
                    "role": "user",
                    "content": f"base on this document: {clean_text(_input)}"
                },
            ],
            response_format=Exam,
        )
        res = json.loads(completion.choices[0].message.content)
        for i in range(len(res["quizes"])):
            res["quizes"][i]["level"] = "Thông hiểu"
        return res



class ExtractC(BaseExtracter):

    def run(self, _input):

        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                        TASK: Extract 4 questions of level C difficulty. Each question should test the ability to apply knowledge to solve problems or perform tasks.
                        Provide the output in the format of a list of dictionaries, where each dictionary has the following fields: question (the question text), choices (a list of 4 answer options), and answer (the correct answer from the choices).
                        Make sure the questions cover a variety of general knowledge topics.
                        RULE: questions, choices, and answers in Vietnamese.
                        """
                },
                {
                    "role": "user",
                    "content": f"base on this document: {clean_text(_input)}"
                },
            ],
            response_format=Exam,
        )
        res = json.loads(completion.choices[0].message.content)
        for i in range(len(res["quizes"])):
            res["quizes"][i]["level"] = "Vận dụng"
        return res



class ExtractD(BaseExtracter):

    def run(self, _input):

        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": """
                        TASK: Extract 1 question of level D difficulty. The question should test the ability to analyze, evaluate, or create based on complex or abstract information.
                        Provide the output in the format of a dictionary, where the dictionary has the following fields: question (the question text), choices (a list of 4 answer options), and answer (the correct answer from the choices).
                        RULE: The question, choices, and answer should be in Vietnamese.
                        """
                },
                {
                    "role": "user",
                    "content": f"base on this document: {clean_text(_input)}"
                },
            ],
            response_format=Exam,
        )
        res = json.loads(completion.choices[0].message.content)
        for i in range(len(res["quizes"])):
            res["quizes"][i]["level"] = "Vận dụng cao"
        return res


class ExamOneChain():

    def run(self, text, com = []):
        print("INPUT: ", text, "\n", "---------" * 20)
        for x in com:
            res = x().run(text)
            for quiz in res['quizes']:
                print("question:", quiz["question"])
                print("choices:", quiz["choices"])
                print("answer:", quiz["answer"])
                print("level:", quiz["level"])
                print("\n")

#!/usr/bin/env python3

import openai
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

def get_gpt_sentiment_analysis(prompt):
    api_key = os.environ['OPENAI_API_KEY']
    openai.api_key = api_key

    messages = [
        {"role": "system", "content": "You do sentiment analysis on Reddit posts. Give the comment a rating from 0 to 10, where 0 is very negative and 10 is very positive. Only respond with an integer, and no punctuation."},
    ]
    
    message = """Assistant, consider the following Reddit comment for sentiment analysis:
    Reddit comment: +prompt+
    Remember that this analysis should take into account the complexities of online language, like sarcasm, memes, and other non-traditional modes of expression. Provide the following analysis, with the score and confidence ranging from 0 to 10:
    {
    "comment_sentiment_score": int,
    "score_confidence": int
    }"""
    prompt

    messages.append({"role": "user", "content": message})
      # Get raw text response
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    ).choices[0].message.content

    sentiment = json.loads(response)
  
    return sentiment

if __name__ == '__main__':
    response = get_gpt_response("test")
    
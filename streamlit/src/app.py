import os
import streamlit as st
from streamlit_chat import message
import requests
import json
import anthropic
# from transformers import pipeline

from driver import read_query, get_article_text
from train_cypher import examples

st.title("NeoHaiku : Claude3 + Neo4j")

def get_env_variable(key):
    with open('.env', 'r') as file:
        for line in file:
            name, value = line.strip().split('=', 1)
            if name == key:
                return value
    return None

def generate_response(prompt, cypher=True):
    client = anthropic.Anthropic(api_key=get_env_variable('ANTHROPIC_API_KEY'))

    if cypher:
        messages = [
            {"role": "user", "content": "examples : " + examples + "\n Generate query for this #" + prompt}
        ]
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.5,
            system="Task: Generate Cypher query to query a Neo4j graph database for the query as shown in the examples. Note: Do not include any other text except the resulting query like explanations or apologies in your responses. ",
            messages=messages
        )
        print("before query \n " + message.content[0].text)
        cypher_query = message.content[0].text
        message = read_query(cypher_query)
        return message, cypher_query
    else:
        messages = [
            {"role": "user", "content": "Summarize the following article: \n" + prompt}
        ]
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=256,
            temperature=0.5,
            # system="Respond formally.",
            messages=messages
        )
        message = message.content[0].text
        return message, None

# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


col1, col2 = st.columns([2, 1])


with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    # Summarize articles
    if "summar" in user_input.lower():
        article_title = user_input.split(":")[1]
        # try:
        #     article_title = int(article_title)
        # except ValueError:
        #     print(f"Cannot convert {article_title} to an integer.")
        article_text = get_article_text(article_title)
        if not article_text:
            st.session_state.past.append(user_input)
            st.session_state.generated.append(
                (["Couldn't find any text for the given article"], ""))
        else:
            print("ARTICLE TEXT : ")
            print(article_text)
            print("\n")
            output, cypher_query = generate_response(article_text[0], cypher=False)
            st.session_state.past.append(user_input)
            st.session_state.generated.append(([output], cypher_query))
    # English2Cypher with GPT
    else:
        output, cypher_query = generate_response(user_input)
        # store the output
        st.session_state.past.append(user_input)
        st.session_state.generated.append((output, cypher_query))

# # print(st.session_state.past)
# past_as_str = ' '.join(st.session_state.past)
# print("PAST: "+ past_as_str)
# generated_as_str = ' '.join(str(item) for item in st.session_state.generated)
# print("\n GENERATED: \n"+ generated_as_str)

# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        message(st.session_state['past'][-1],
                is_user=True, key=str(-1) + '_user')
        for j, text in enumerate(st.session_state['generated'][-1][0]):
            message(text, key=str(-1) + str(j))

# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['generated']:
        st.text_area("Generated Cypher statement",
                     st.session_state['generated'][-1][1], height=240)

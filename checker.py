from dotenv import load_dotenv
load_dotenv()  # loading all the environment variables

import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Initialize the Streamlit app
st.set_page_config(page_title="Q&A Demo")

st.header("Gemini LLM Application")

submit = st.button("Ask the question")

with open('values.txt', 'r') as file:
    defalut_values = file.read()

with open('temp.txt', 'r') as file:
    file_content = file.read()

input_text = f"""
Compare the following certificate values against the default values to determine if the certificate passes. A certificate passes if all values are greater than or equal to their corresponding default values. If any default value is missing in the certificate, exclude it from the comparison.
\n
Instructions:

Comparison: Ensure each certificate value is greater than or equal to the default value.
Result: Output "Pass" if all present values meet or exceed the defaults. Output "Fail" and specify the failing features if any values are below the default.
\n
Provide results as follows:

Pass or
Fail with specific failing features.
\n
Default Values:

{defalut_values}
\n
Certificate Values:

{file_content}
"""

if submit and input_text:
    response = get_gemini_response(input_text)

    for chunk in response:
        st.write(chunk.text)
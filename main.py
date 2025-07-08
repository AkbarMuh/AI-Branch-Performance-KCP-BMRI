import os
import re
import requests
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime  # Import untuk mendapatkan waktu dan tanggal
import pandas as pd  # Import pandas untuk menyimpan log ke file Excel
import csv  # Import csv untuk menyimpan log ke file CSV
import time
from openai import AzureOpenAI


load_dotenv()
API_KEY = os.getenv("AZURE_API_KEY")
ENDPOINT = os.getenv("AZURE_API_ENDPOINT")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}

def baca_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        return None
    
def bacalistfilefolder(folder_path):
    try:
        files = os.listdir(folder_path)
        return files
    except FileNotFoundError:
        return []



users = {
    'Sunarto':'1234',
}

def login(username, password):
    if 1+1==2:
        return True
    return False

st.set_page_config(page_title="Bank Mandiri Chatbot", layout="wide")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.title("KCP Review")
    with st.form(key='login_form'):
        cabangKCP = st.selectbox("Pilih KCP", options=list(bacalistfilefolder("List-Review/")))  # Dropdown untuk username
        password = st.text_input("Password", type='password')
        submit_button = st.form_submit_button("Login")

    if submit_button:
        if login(cabangKCP, password):
            st.session_state.logged_in = True
            st.session_state.username = cabangKCP  # Menyimpan username dalam session state
            st.rerun()  # Memaksa Streamlit untuk merender ulang
        else:
            st.error("Password salah.")
else:
    
    # Jika sudah login, tampilkan sistem chat
    st.title("BMRI Performance Chat")
    namacabang = st.session_state.username.replace("_", " ").replace("Google Reviews.csv", "")
    st.write(f"Selamat datang, {namacabang}!")
    df = pd.read_csv(f"List-Review/{st.session_state.username}")
    df = df.applymap(str)
    st.dataframe(df)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.messages = []  # Reset pesan saat logout
        st.success("Anda telah logout.")
        st.rerun()  # Memaksa Streamlit untuk merender ulang

    if "messages" not in st.session_state:
        st.session_state.messages = [] 

    

    # Function to call the API
    def get_chatbot_response(user_message, chat_history):
        chat_history_formatted = [{"role": msg["role"], "content": msg["content"]} for msg in chat_history]                        
        payload = {
            "chat_input": user_message,
        }

        print(chat_history_formatted)

        #print("Payload Encrypt:", payload["nama"])
        try:
            
            prompt = "Disini kamu sebagai AI Assistant Branch"+namacabang+" akan membantu menjawab pertanyaan terkait performa cabang Bank Mandiri. Kamu akan menjawab pertanyaan berdasarkan data List-Review dibawah ini.\n\n"
            # Simulasi respons dari API
            data = baca_data(f"List-Review/{st.session_state.username}")
            if data is None:
                return "Data tidak ditemukan. Pastikan file sudah ada di folder List-Review."
            #print("Data Read:", data[:1000])  # Print hanya sebagian data untuk keamanan
            
            
            response = prompt + "\n\n" , data + "\n\n" , "Pertanyaan : " + payload["chat_input"]
            
            def get_azure_openai_response(endpoint, deployment, subscription_key, chat_prompt):
                # Initialize Azure OpenAI client with key-based authentication
                client = AzureOpenAI(
                    azure_endpoint=endpoint,
                    api_key=subscription_key,
                    api_version="2025-01-01-preview",
                )

                # Generate the completion
                completion = client.chat.completions.create(
                    model=deployment,
                    messages=chat_prompt,
                    max_tokens=800,
                    temperature=0.7,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None,
                    stream=False
                )

                # Extract the content from the response
                import json
                json_response = completion.to_json()
                response_data = json.loads(json_response)

                content = response_data["choices"][0]["message"]["content"]
                return content

            # Define your parameters
            endpoint = os.getenv("ENDPOINT_URL", ENDPOINT)
            deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
            subscription_key = os.getenv("AZURE_OPENAI_API_KEY", API_KEY)
            # Prepare the chat prompt
            chat_prompt = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": response[0] + response[1] + response[2]
                        }
                    ]
                }
            ]

            # Call the function and print the response
            response_content = get_azure_openai_response(endpoint, deployment, subscription_key, chat_prompt)
            #response_content = chat_prompt
            print(response_content)

            return response_content

        except requests.RequestException as e:
            return f"An error occurred: {e}"

    if prompt := st.chat_input("Ketik pertanyaan atau permintaan Anda"):
        start_time = time.time()
        st.session_state.messages.append({"role": "user", "content": prompt})
        print("Prompt Content Encrypt:", prompt)
        dataCompareModel = ""
        #mode4o = st.selectbox("Pilih Mode 4o", options=["4o", "4o-mini", "4o&4o-mini"], index=0)
        bot_response = get_chatbot_response(prompt, st.session_state.messages)
        end_time = time.time()
        execution_time = end_time - start_time
        dataCompareModel = f"| Token {len(bot_response)} | {execution_time:.2f} detik"

        print("Resonponse Content:", bot_response)
        
        print(f"Execution time: {execution_time} seconds")
        bot_response = f"{bot_response}\n\n\n| Model Default {dataCompareModel}"

        if bot_response:
            st.session_state.messages.append({"role": "assistant", "content": bot_response})



    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

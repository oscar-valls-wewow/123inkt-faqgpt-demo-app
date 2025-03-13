import os
import time
import streamlit as st
import uuid
from dotenv import load_dotenv
from openai import OpenAI

# Show title and description.
st.title("CS Messages translations chatbot")
st.write(
    "This chatbot automatically translates messages for multilingual Customer Service. "
)
language = st.selectbox(
    "Select the language translation language",
    ("German", "Dutch", "French", "Italian", "Spanish", "Danish", "Portuguese"),
    index=None,
    placeholder="Select language here...",
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

# Create a session state variable to store the chat messages and session_id. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())  # Generate a unique session_id

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    # Add avatars for both assistant and user messages
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if chat_message := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": chat_message})
    with st.chat_message("user", avatar="👤"):
        st.markdown(chat_message)
    if language:
        # Generate a response using the local API.
        response = client.chat.completions.create(
                                                    model="gpt-4o-mini",
                                                    messages=[
                                                        {"role": "developer", "content": system_prompt.format(language=language)},
                                                        {"role": "user", "content": chat_message}
                                                    ]
                                                    )
        # Stream the response to the chat using `st.write_stream`, then store it in 
        def stream_data():
            for word in response.choices[0].message.content.split(" "):
                yield word + " "
                time.sleep(0.05)

        with st.chat_message("assistant", avatar="🤖"):
            response = st.write_stream(stream_data())
    
        # Store the response in session state.
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        response = "Please, select a language to translate."   

        # Stream the response to the chat using `st.write_stream`, then store it in 
        def stream_data():
            for word in response.split(" "):
                yield word + " "
                time.sleep(0.05)
        
        with st.chat_message("assistant", avatar="🤖"):
            response = st.write_stream(stream_data())
    
        # Store the response in session state.
        st.session_state.messages.append({"role": "assistant", "content": response})
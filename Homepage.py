import time
import requests
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import streamlit as st
from langchain.prompts import PromptTemplate
import tiktoken

from langchain.schema import (
    SystemMessage,
    HumanMessage,
)

st.set_page_config(
    page_title="Ai Emailer Tool",
    layout="wide",
)

global orgKey
orgKey = "Organization key here" 

#Initialize key
if 'key' not in st.session_state:
    st.session_state.key = "Your Open Ai Key"

#Initialize temp
if 'temp' not in st.session_state:
    st.session_state.temp = 0.5

#Initialize LLMmodel
if 'LLMmodel' not in st.session_state:
    st.session_state.LLMmodel = 'gpt-3.5-turbo'

#Initialize langueage
if 'language' not in st.session_state:
    st.session_state.language = 'English'

chat = ChatOpenAI(
    openai_api_key=st.session_state.key,
    temperature=st.session_state.temp,
    model=st.session_state.LLMmodel
)

#Hides API Key values from user
def hideKey(key):
    secKey = ''
    for char in key:
        if char != '-':
            secKey += 'x'
        else:
            secKey += char
    return secKey

# Function to reset session state
def reset_session_state():
    st.session_state.button_clicked = False
    st.session_state.field_disabled = False
    st.session_state.button_disabled = False

#Changes button session state 
def toggle_button_on_click():
    # Toggle the disabled state of the button
    st.session_state.button_disabled = not st.session_state.button_disabled
    #Disable Input Fields
    st.session_state.field_disabled = not st.session_state.field_disabled

# Initialize the button_disabled session state variable
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

# Initialize session state variables
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Initialize email_counter in session state
if 'email_counter' not in st.session_state:
    st.session_state.email_counter = 0

if 'field_disabled' not in st.session_state:
    st.session_state.field_disabled = False

message = "Hello OpenAI! I hope this message finds you well. I am excited to explore the capabilities of the OpenAI API. As a user, I am eager to harness the power of language models for various applications. Thank you for providing this incredible tool. Looking forward to creating amazing things together!"

def num_tokens_from_messages(messages):
    """Return the number of tokens used by a list of messages."""
    model=st.session_state.model
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

st.write(num_tokens_from_messages(message))

# Takes URL and Scrapes website for text
def get_URL_text(URL):
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text
            text_content = soup.get_text()
            return text_content
        else:
            #If the request was not successful, print an error message
            print(f"Error: Unable to fetch content from {URL}. Status code: {response.status_code}")
    except Exception as error:
        #Handle any exceptions that might occur during the process
        print(f"An error occurred: {error}")

# Takes URL_Response, CompanyName, DesiredItem as a parameter and returns LLM response
def llm_response(CompanyName, DesiredItem, URL_Text, max_length):
    message = (
        SystemMessage(content=(f'''
        You are a program that creates emails to send to companies in order to seek out sponsorships.
        All of your responses should be in {st.session_state.language}
        for context here is a summary of the organization you represent: Global Formula Racing (GFR), in the Formula Student Competition since 2009, seeks support for designing competitive vehicles. Emphasizing simplicity, reliability, and practical experience, GFR competes globally, excelling in static and dynamic events. With a rich history, including transitioning to electric powertrains and embracing driverless development, GFR aims to shape developments in alternative propulsion and autonomous driving. The team values sponsors contributions in material, manufacturing, finance, and knowledge, offering various sponsorship packages. Sponsors become part of the Formula Student community, gaining visibility on the race car, livery, and website. The team welcomes sponsors to actively recruit and hire members, contributing to the growth of future engineers.
        for context here is text from a website regarding the desired item: {URL_Text}.
        '''
        )),
        HumanMessage(content=f"Create an email to {CompanyName} seeking a sponsorship including but not limited to a(n) {DesiredItem} please limit your response to {max_length} words")
    )
    res = chat(message)
    return res.content

#Function takes error message as input, counts-down and restarts site
def rerun(error):
    st.warning(error, icon="⚠️")
    for i in range(5, -1, -1):
        st.text(f"Restarting in {i}")
        time.sleep(1)
    reset_session_state()
    st.rerun()

def Main():
    st.image('gfr.png')

    st.write("")


    st.title("Sponsor Email Tool")
    tabMain, tabSettings, tabInfo = st.tabs(["Main", "Settings", "Info"])
    
    with tabMain:
        
        st.subheader("This program utlilizes GPT-3.5 to generate emails for potential contributors.",divider='red')
        st.write("")

        # Collect user Input
        CompanyName = st.text_input("Enter Company Name:",disabled= st.session_state.field_disabled)
        DesiredItem = st.text_input("Enter Desired Item:",disabled= st.session_state.field_disabled)
        URL = st.text_input("Enter Relevant URL:",disabled= st.session_state.field_disabled)
        max_length = st.slider("Maximum Word Count",disabled= st.session_state.field_disabled, min_value=100, max_value=2500, value=500)

        if len(CompanyName) != 0 and len(DesiredItem) != 0 and len(URL) != 0:
            #If button hasnt been clicked
            if st.session_state.button_clicked == False:
                #Starts Email Creation & toggles button functionality
                if st.button("Create Email",on_click=toggle_button_on_click,disabled= st.session_state.button_disabled):
                    with st.status("Generating Email", expanded=True):
                        st.write("Downloading Data")
                        URL_Text = get_URL_text(URL)
                        
                        # Error Handling
                        error_message = []
                        if URL_Text is None or len(URL_Text) == 0:
                            error_message.append("Invalid URL")
                        if "sk-" not in st.session_state.key:
                            error_message.append("Invalid API Key")
                        
                        if len(error_message) == 0:
                            # Generate & display the email
                            st.text_area(llm_response(CompanyName, DesiredItem, URL_Text, max_length))
                            st.session_state.email_counter += 1
                        else:
                            errorlist = ', '.join(error_message)
                            rerun(errorlist)

    with tabSettings:
        st.write("")
        st.write("")

        st.subheader("Models 🤖",divider='red')
        st.write("")
        st.markdown(
            """
            ChatGPT 3.5 and ChatGPT 4 are pinnacle models in conversational AI. With 175 billion  
            parameters, ChatGPT 3.5 excels in generating human-like text with remarkable  
            coherence, while ChatGPT 4 takes it a step further, refining language understanding  
            and response generation."""
            )
        #Shows Model
        st.session_state.temp = st.text_input('','gpt-3.5-turbo', disabled= True)

        st.write("")
        st.write("")

        st.subheader("LLM Temperature 🌡️",divider='red')
        st.markdown(
            """
            In a Language Model like GPT-3.5, temperature is a crucial setting that controls the randomness of text generation.  
            Higher values (e.g., 0.8) produce diverse and creative outputs, while lower values (e.g., 0.2) result in more focused  
            and deterministic responses. Adjusting the temperature allows control of the balance, coherence and novelty in the  
            generated content, tailoring it to the desired preferences or applicational needs."""
            )
        st.write("")
        st.session_state.temp = st.slider("Temperature (Default: 0.5)",disabled= st.session_state.field_disabled,min_value=0.0, max_value=1.0, value=0.5)

        st.write("")
        st.write("")

        st.subheader("API Key🗝️",divider='red')
        st.markdown(
            """
            An OpenAI API key is a secure passkey that enables developers to access and  
            integrate OpenAI's language models into their applications, allowing for the retrieval  
            and submission of information with authorized control."""
            )
        
            #API key selection
        whatKey = st.radio(
            "",
            ["Organization Key", "Custom Key"],
            disabled= st.session_state.field_disabled,
            horizontal=True,
            )
    
        if whatKey == "Organization Key":
            st.text_input("",hideKey(st.session_state.key),disabled=True)
            st.session_state.key = orgKey
        else:
            posKey = st.text_input('Your Key',disabled=st.session_state.field_disabled)
            if st.button('submit key',disabled=st.session_state.field_disabled) and len(posKey) != 0:
                st.session_state.key = posKey
        st.write("")
        st.write("")

        st.subheader("Output Language",divider='red')

        #language selection
        whatLang = st.radio(
            "Desired language",
            ["English","Deutsch"],
            disabled=st.session_state.field_disabled,
            horizontal=True,
        )

        st.session_state.language = whatLang
        
    with tabInfo:
        st.write("")
        st.write("")

        st.subheader("Company Name",divider='red')
        st.markdown(
            """
            "Company Name" refers to the company in which we desire a contribution from. 
        """
        )

        st.write("")
        st.write("")

        st.subheader("Desired Item", divider= 'red')
        st.markdown(
            """
            "Desired Item" refers to the desired item in which we want from the Company.
        """
        )

        st.write("")
        st.write("")

        st.subheader("URL", divider= 'red')
        st.markdown(
            """
            "URL" refers to a link to a website that contains information relevant to both the Company and the Desired Item. The information from this website gives ChatGPT context in which to create a relevant email.
        """
        )
        
Main()

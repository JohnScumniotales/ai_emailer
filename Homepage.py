import time
import requests
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import streamlit as st

from langchain.schema import (
    SystemMessage,
    HumanMessage,
)

st.set_page_config(
    page_title="Ai Emailer Tool",
    layout="wide",
)

global key
key = "Your Open Ai Key"

#intialize temp
if 'temp' not in st.session_state:
    st.session_state.temp = 0.5

if 'LLMmodel' not in st.session_state:
    st.session_state.LLMmodel = 'gpt-3.5-turbo'

chat = ChatOpenAI(
    openai_api_key=key,
    temperature=st.session_state.temp,
    model=st.session_state.LLMmodel
)

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

# Takes URL as a parameter and returns text if possible
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
    st.write("")

    st.title("Sponsor Email Tool")
    st.subheader("",divider='red')
    tabMain, tabSettings = st.tabs(["Main", "Settings"])
    
    with tabMain:
        
        st.subheader("This tool utlilizes GPT 3.5 to generate emails for potential sponsors.",divider='red')
        st.subheader("Created for Global Formula Racing (GFR)")
        
        st.write("")

        st.text(f"Emails Generated: {st.session_state.email_counter}")
        
        st.write("")
        
        # Collect user Input
        CompanyName = st.text_input("Enter Company Name:",disabled= st.session_state.field_disabled)
        DesiredItem = st.text_input("Enter Desired Item:",disabled= st.session_state.field_disabled)
        URL = st.text_input("Enter URL:",disabled= st.session_state.field_disabled)
        max_length = st.slider("Max Word Count",disabled= st.session_state.field_disabled, min_value=100, max_value=2500, value=500)

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
                        if "sk-" not in key:
                            error_message.append("Invalid API Key")
                        
                        if len(error_message) == 0:
                            # Generate the email
                            result = llm_response(CompanyName, DesiredItem, URL_Text, max_length)
                            st.write(result)
                            st.session_state.email_counter += 1
                        else:
                            errorlist = ', '.join(error_message)
                            rerun(errorlist)

    with tabSettings:
        st.write("")
        st.write("")

        st.subheader("Models 🤖")
        st.markdown(
            """
            ChatGPT 3.5 and ChatGPT 4 are pinnacle models in conversational AI. With 175 billion  
            parameters, ChatGPT 3.5 excels in generating human-like text with remarkable  
            coherence, while ChatGPT 4 takes it a step further, refining language understanding  
            and response generation.  
        """
        )
        #Shows Model
        st.session_state.temp = st.text_input('','gpt-3.5-turbo', disabled= True)

        st.write("")
        st.write("")

        st.subheader("LLM Temperature 🌡️")
        st.markdown(
            """
            In a Language Model like GPT-3.5, temperature is a crucial setting that controls the randomness of text generation.  
            Higher values (e.g., 0.8) produce diverse and creative outputs, while lower values (e.g., 0.2) result in more focused  
            and deterministic responses. Adjusting the temperature allows control of the balance, coherence and novelty in the  
            generated content, tailoring it to the desired preferences or applicational needs.  
        """
        )
        st.write("")
        st.session_state.temp = st.slider("Temperature (Default: 0.5)",disabled= st.session_state.field_disabled,min_value=0.0, max_value=1.0, value=0.5)

        st.write("")
        st.write("")

        st.subheader("API Key🗝️")
        st.markdown(
            """
            An OpenAI API key is a secure passkey that enables developers to access and  
            integrate OpenAI's language models into their applications, allowing for the retrieval  
            and submission of information with authorized control.  
        """
        )

Main()

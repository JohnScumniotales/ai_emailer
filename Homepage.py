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

chat = ChatOpenAI(
    openai_api_key=key,
    temperature=0.5,
    model='gpt-3.5-turbo'
)

# Function to reset session state
def reset_session_state():
    st.session_state.button_clicked = False

#Changes button session state 
def toggle_button_on_click():
    # Toggle the disabled state of the button
    st.session_state.button_disabled = not st.session_state.button_disabled

# Initialize the button_disabled session state variable
if 'button_disabled' not in st.session_state:
    st.session_state.button_disabled = False

# Initialize session state variables
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Initialize email_counter in session state
if 'email_counter' not in st.session_state:
    st.session_state.email_counter = 0

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
def llm_response(CompanyName, DesiredItem, URL_Text):
    message = (
        SystemMessage(content=(f'''
        You are a program that creates emails to send to companies in order to seek out sponsorships.
        for context here is a summary of the organization you represent: Global Formula Racing (GFR), in the Formula Student Competition since 2009, seeks support for designing competitive vehicles. Emphasizing simplicity, reliability, and practical experience, GFR competes globally, excelling in static and dynamic events. With a rich history, including transitioning to electric powertrains and embracing driverless development, GFR aims to shape developments in alternative propulsion and autonomous driving. The team values sponsors contributions in material, manufacturing, finance, and knowledge, offering various sponsorship packages. Sponsors become part of the Formula Student community, gaining visibility on the race car, livery, and website. The team welcomes sponsors to actively recruit and hire members, contributing to the growth of future engineers.
        for context here is text from a website regarding the desired item: {URL_Text}.
        '''
        )),
        HumanMessage(content=f"Create an email to {CompanyName} seeking a sponsorship including but not limited to a(n) {DesiredItem}")
    )
    res = chat(message)
    return res.content

# Function takes error message as input, counts-down and restarts site
def rerun(error):
    
    st.warning(error, icon="⚠️")
    for i in range(5, -1, -1):
        st.text(f"Restarting in {i}")
        time.sleep(1)
    toggle_button_on_click()
    st.rerun()

def Main():
    st.image('gfr.png')
    #Streamlit UI Title
    st.title("Sponsor Email Generator")
    st.text(f"Total Emails Generated: {st.session_state.email_counter}")
    
    # Collect user Input
    CompanyName = st.text_input("Enter Company Name:",disabled= st.session_state.button_disabled)
    DesiredItem = st.text_input("Enter Desired Item:",disabled= st.session_state.button_disabled)
    URL = st.text_input("Enter URL:",disabled= st.session_state.button_disabled)
    
    #If button hasnt been clicked
    if st.session_state.button_clicked == False:
        #Starts Email Creation & toggles button functionality
        if st.button("Create Email",on_click=toggle_button_on_click,disabled= st.session_state.button_disabled):
            with st.status("Generating Email", expanded=True):
                st.write("Downloading Data")
                URL_Text = get_URL_text(URL)
                
               # Error Handling
                error_message = []
                if len(URL) == 0:
                    error_message.append("No URL Provided")
                if URL_Text is None or len(URL_Text) == 0:
                    error_message.append("Invalid URL")
                if len(CompanyName) == 0:
                    error_message.append("No Company Name")
                if len(DesiredItem) == 0:
                    error_message.append("No Desired Item")
                if "sk-" not in key:
                    error_message.append("Invalid API Key")
                
                if len(error_message) == 0:
                    # Generate the email
                    result = llm_response(CompanyName, DesiredItem, URL_Text)
                    st.write(result)
                    st.session_state.email_counter += 1
                else:
                    errorlist = ', '.join(error_message)
                    rerun(errorlist)
Main()


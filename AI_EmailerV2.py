import requests
from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import streamlit as st



from langchain.schema import (
    SystemMessage,
    HumanMessage,
    #AIMessage ???
)

chat = ChatOpenAI(
    openai_api_key="Your Open Ai Key",
    temperature=0.5,
    model='gpt-3.5-turbo'
)

#Takes URL as a parameter and returns text if possible
def get_URL_text(URL):
    try:
        response = requests.get(URL)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text

            text_content = soup.get_text()

            return text_content
        else:
            # If the request was not successful, print an error message
            print(f"Error: Unable to fetch content from {URL}. Status code: {response.status_code}")
    except Exception as error:
        # Handle any exceptions that might occur during the process
        print(f"An error occurred: {error}")

#Takes URL_Response, CompanyName , DesiredItem as parameter and returns LLM response
def llm_response(CompanyName,DesiredItem,URL_Text):
    #Need to be Array ???
    message = (
        SystemMessage(content=(
            f'You are a program that creates emails to send to companies in order to seek out sponsorships'
            'for context here is a summary of the organization you represent: Global Formula Racing (GFR), in the Formula Student Competition since 2009, seeks support for designing competitive vehicles. Emphasizing simplicity, reliability, and practical experience, GFR competes globally, excelling in static and dynamic events. With a rich history, including transitioning to electric powertrains and embracing driverless development, GFR aims to shape developments in alternative propulsion and autonomous driving. The team values sponsors contributions in material, manufacturing, finance, and knowledge, offering various sponsorship packages. Sponsors become part of the Formula Student community, gaining visibility on the race car, livery, and website. The team welcomes sponsors to actively recruit and hire members, contributing to the growth of future engineers.'
            'for context here is text from a website regarding the desired item: {URL_Text}'
        )),
        HumanMessage(content=f"Create an email to {CompanyName} seeking a sponsorship including but not limited to a(n) {DesiredItem}")
    )
    res = chat(message)
    return res.content

def main():
    #Streamlit UI Title
    st.title("Sponsor Email Tool")

    #collect user Input
    CompanyName = st.text_input("Enter Company Name:")
    DesiredItem = st.text_input("Enter Desired Item:")
    URL = st.text_input("Enter URL:")

    st.header("Sponsor Email")
    if st.button("Generate Email Response"):
        #Scrape Text from URL
        URL_Text = get_URL_text(URL)

        #Take User Input and Generate LLM Response
        #st.write(llm_response(CompanyName,DesiredItem,URL_Text))

        #For Testing purposes
        st.write("generated text: ")
    

main()

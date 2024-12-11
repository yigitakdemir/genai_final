****Lord of the Rings Companion****

The Lord of the Rings Companion is a Retrieval-Augmented Generation (RAG) application built with Streamlit and LangChain. It uses FAISS (Facebook AI Similarity Search) to retrieve context from the full-text PDFs of J.R.R. Tolkien's The Lord of the Rings (LOTR) trilogy stored in a docs folder. This context is then used to support interview-like conversations with main LOTR characters, answer questions, generate quizzes, and provide insights about LOTR's Middle-Earth.


**Features**

•	**Interview a Character:** ask specific questions to a selected main character in LOTR, where the character can elaborate on their actions down to the very minor details in the books. They can also talk about their aims/thoughts about different events and about other characters. They can even tell the user exactly what they said to others at various times in the LOTR timeframe. The conversation history can be seen on the page, and cleared when desired.

•	**Talk with an Expert:** ask questions about anything related to the three LOTR books, including very minor details. The page is able to answer anything as long as it can be deduced or inferred from the content of the book.

•	**Explore a Character or Artifact:** learn about the history and significance of LOTR characters and artifacts. For characters, the page also tells about their powers, and in the case of artifacts, the page describes characters associated with them.

•	**Test your LOTR Knowledge:** a 6-question quiz about the events in the LOTR books. Due to the nature of the website (which I will elaborate on below), this quiz is designed for fans of the LOTR world who want to be tested with advanced-level (detail-level) questions. At the end of the quiz, the user can see their total score along with the result for each question.


**Installation**

The following libraries and modules are imported in the source file:

    from langchain_community.document_loaders import DirectoryLoader
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain.prompts import PromptTemplate
    from langchain.chains.question_answering import load_qa_chain       
    from langchain_openai import OpenAI
    from dotenv import load_dotenv
    import streamlit as st
    import random


**Set Up Environment Variables**

Create a .env file in the project root directory and add the following variables:

    OPENAI_API_KEY=<your_openai_api_key>


**Configure Streamlit**

Ensure you have a .streamlit/config.toml file with the following text for custom theming:

    [theme]
    base = "dark"
    primaryColor = "#F6CF33"
    backgroundColor = "black"
    secondaryBackgroundColor = "#2E2E2D"
    textColor = "white"


**Add the Book PDFs**

Place the PDFs of The Fellowship of the Ring, The Two Towers, and The Return of the King in a folder named docs in the root directory.


**Run the Application**

Launch the app using the following command:

    py -m streamlit run .\lotr_companion.py

The application will start in your default web browser. The initial loading of books into FAISS should take ~5 minutes.


**Usage**

The app is divided into four main pages, accessible via a sidebar:

•	**Interview a Character**

•	**Talk with an Expert**

•	**Explore a Character or Artifact**

•	**Test Your LOTR Knowledge**


**Backend Details**

•	**Document Loader:** Loads PDFs from the docs folder using PyPDFLoader.

•	**Text Splitting:** Splits the books into manageable chunks for FAISS embedding.

•	**FAISS Index:** Two separate indices: General index for lore-related queries, and Character-specific index for in-character responses.
    
•	**Prompt Templates:** Customized prompts for character, general, quiz, and character/artifact description responses.

•	**Context:** Most relevant chunks from FAISS are combined into "context", which is used to enhance the prompts.

•	**Chains:** Uses LangChain to provide the prompt (which includes the FAISS-based context) into OpenAI's ChatGPT.

•	**Response:** Show ChatGPT's "informed" response through the custom styling and format of the main page.


**Interactive Styling**

•	Themed using custom CSS for a Middle-Earth-inspired look.

•	Background images, fonts, and centered character images enhance user experience.


**What if I encounter a bug?**

•	Ensure the book PDFs are in the correct folder (docs).

•	Verify your API key in the .env file.

•	Check for missing dependencies and install them using pip install.

•	Ensure that Streamlit theming is applied through the .streamlit/config.toml file.


**Future Improvements**

•	Add other books from Tolkien's Legendarium such as The Hobbit and Silmarillion.

•	Deploy the website in Streamlit with the FAISS models/indices already hosted, to save time on loading.

•	Add memory functionality when conversing with a character or expert.

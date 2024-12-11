**Lord of the Rings Companion**

The Lord of the Rings Companion is a Retrieval-Augmented Generation (RAG) application built with Streamlit and LangChain. It uses FAISS (Facebook AI Similarity Search) to retrieve context from the full-text PDFs of J.R.R. Tolkien's The Lord of the Rings trilogy stored in a docs folder. This context is then used to answer questions, generate quizzes, and provide insights about Middle-earth.

Features

•	**Interview a Character:** ask specific questions to a selected main character in LOTR, where the character can elaborate on their actions down to the very minor details in the books. They can also talk about their aims/thoughts about different events and about other characters. They can even tell the user exactly what they said to others at various times in the LOTR timeframe. The conversation history can be seen on the page, and cleared when desired.
•	**Talk with an Expert:** ask questions about anything related to the three LOTR books, including very minor details. The page is able to answer anything as long as it can be deduced or inferred from the content of the book.
•	**Explore a Character or Artifact:** learn about the history and significance of LOTR characters and artifacts. For characters, the page also tells about their powers, and in the case of artifacts, the page describes characters associated with them.
•	**Test your LOTR Knowledge:** a 6-question quiz about the events in the LOTR books. Due to the nature of the website (which I will elaborate on below), this quiz is designed for fans of the LOTR world who want to be tested with advanced-level (detail-level) questions. At the end of the quiz, the user can see their total score along with the result for each question.

Installation
Prerequisites

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

Set Up Environment Variables

Create a .env file in the project root directory and add the following variables:

OPENAI_API_KEY=<your_openai_api_key>

Configure Streamlit

Ensure you have a .streamlit/config.toml file for custom theming. An example:

[theme]
primaryColor = "#6b5a01"
backgroundColor = "#1f1700"
secondaryBackgroundColor = "#292929"
textColor = "#ffffff"
font = "sans serif"

Add the Book PDFs

Place the PDFs of The Fellowship of the Ring, The Two Towers, and The Return of the King in a folder named docs in the root directory.
Run the Application

Launch the app using the following command:

py -m streamlit run .\lotr_companion.py

The application will start in your default web browser.
Usage
Navigation

The app is divided into four main pages, accessible via the sidebar:

    Interview a Character: Select a character, ask questions, and receive in-character responses.
    Talk with an Expert: Ask questions about Middle-earth lore and get detailed answers with retrieved context.
    Explore a Character or Artifact: Enter a name and explore detailed insights based on the books.
    Test Your LOTR Knowledge: Take a dynamic quiz based on random excerpts from the books.

Backend Details

    Document Loader: Loads PDFs from the docs folder using PyPDFLoader.
    Text Splitting: Splits the books into manageable chunks for FAISS embedding.
    FAISS Index: Two separate indices:
        General index for lore-related queries.
        Character-specific index for in-character responses.
    Prompt Templates: Customized prompts for character, general, and quiz responses.

Interactive Styling

    Themed using custom CSS for a Middle-earth-inspired look.
    Background images, fonts, and centered character images enhance user experience.

FAQ
Why do I need the PDFs?

The application retrieves answers from the actual text of The Lord of the Rings. Without the books, the FAISS index cannot provide relevant context.
Can I add more characters or artifacts?

Yes! Update the detect_character_tags function to include new character names or modify the artifact exploration logic.
How are quiz questions generated?

Quiz questions are dynamically created using context retrieved from the FAISS index. Each question includes four multiple-choice options with one correct answer.
What if I encounter a bug?

    Ensure the book PDFs are in the correct folder (docs).
    Verify your API key in the .env file.
    Check for missing dependencies and install them using pip install -r requirements.txt.

Future Improvements

    Add support for additional languages or texts from Tolkien's universe (e.g., The Silmarillion).
    Enhance quiz logic with more diverse question types.
    Introduce user account functionality to track quiz scores and favorite characters.

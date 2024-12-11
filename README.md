Lord of the Rings Companion

The Lord of the Rings Companion is a Retrieval-Augmented Generation (RAG) application built with Streamlit and LangChain. It uses FAISS (Facebook AI Similarity Search) to retrieve context from the full-text PDFs of J.R.R. Tolkien's The Lord of the Rings trilogy stored in a docs folder. This context is then used to answer questions, generate quizzes, and provide insights about Middle-earth.
Features

    Character Conversations: Ask questions to iconic characters like Gandalf, Frodo, Aragorn, and more. The responses are crafted in the style of the chosen character using relevant context from the books.
    Expert Q&A: Query an "expert" on The Lord of the Rings lore to gain detailed answers about characters, places, and events.
    Character and Artifact Exploration: Dive into the history, significance, and powers of characters or artifacts from the Middle-earth universe.
    Trivia Quiz: Test your knowledge of The Lord of the Rings with a multiple-choice quiz generated dynamically from the books.

Installation
Prerequisites

    Python 3.11 or later
    pip package manager

Clone the Repository

git clone <repository-url>
cd <repository-folder>

Install Dependencies

Run the following command to install the required Python libraries:

pip install -r requirements.txt

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

# Import necessary libraries
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import random

load_dotenv()

# Set page configuration
st.set_page_config(page_title="LOTR Companion", layout="wide")

# Cache FAISS loading to avoid reloading on every run
@st.cache_resource
def load_faiss():
    loader = DirectoryLoader(f'docs', glob="./*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    chunk_size_value = 1000
    chunk_overlap = 100
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size_value, chunk_overlap=chunk_overlap, length_function=len)

    # General embeddings:
    general_texts = text_splitter.split_documents(documents)
    general_faiss = FAISS.from_documents(general_texts, OpenAIEmbeddings())
    general_faiss.save_local("general_faiss_index")
    general_faiss = FAISS.load_local("general_faiss_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)

    # With character tags: split documents and add metadata
    texts = []
    for doc in documents:
        chunks = text_splitter.split_documents([doc])
        for chunk in chunks:
            # Heuristically tag metadata (e.g., look for mentions of characters)
            character_tags = []
            if "Frodo" in chunk.page_content:
                character_tags.append("Frodo")
            if "Gandalf" in chunk.page_content:
                character_tags.append("Gandalf")
            if "Aragorn" in chunk.page_content:
                character_tags.append("Aragorn")
            if "Galadriel" in chunk.page_content:
                character_tags.append("Galadriel")
            if "Tom Bombadil" in chunk.page_content:
                character_tags.append("Tom Bombadil")
            if "Gollum" in chunk.page_content:
                character_tags.append("Gollum")
            if "Sauron" in chunk.page_content:
                character_tags.append("Sauron")
            if "Saruman" in chunk.page_content:
                character_tags.append("Saruman")

            chunk.metadata = {"characters": character_tags}
            texts.append(chunk)
    
    char_faiss = FAISS.from_documents(texts, OpenAIEmbeddings())
    char_faiss.save_local("llm_faiss_index")
    char_faiss = FAISS.load_local("llm_faiss_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    return char_faiss, general_faiss

char_faiss, general_faiss = load_faiss()

# Define character-specific prompt
char_prompt_template = """You are roleplaying as {character}, a key figure in 'The Lord of the Rings.' Respond in the style and tone of {character}.

Use only the provided context to answer the question. If the context does not contain relevant information, respond as {character} would, acknowledging that you don't know the answer.

Context:
---------
{context}
---------
Question: {question}
Helpful Answer:"""

CHAR_PROMPT = PromptTemplate(
    template=char_prompt_template,
    input_variables=["context", "question", "character"]
)

# Load character-specific QA Chain
def load_char_chain():
    return load_qa_chain(OpenAI(temperature=0), chain_type="stuff", prompt=CHAR_PROMPT)

char_chain = load_char_chain()

# Define general prompt
general_prompt_template = """You are an expert on 'The Lord of the Rings' lore. Answer questions about Middle-earth using the provided context. If you don't know the answer, just say you don't know.

Context:
---------
{context}
---------
Question: {question}
Helpful Answer:"""

general_prompt = PromptTemplate(
    template=general_prompt_template,
    input_variables=["context", "question"]
)

# Load general QA Chain
def load_general_chain():
    return load_qa_chain(OpenAI(temperature=0), chain_type="stuff", prompt=general_prompt)

general_chain = load_general_chain()

# Define quiz prompt
quiz_prompt_template = """You are generating trivia questions about 'The Lord of the Rings.' 
    Generate one multiple-choice question with 4 options (A, B, C, D) and specify the correct answer. 
    Example format:
    Question: [Your question here]
    Options: A. [option1], B. [option2], C. [option3], D. [option4]
    Answer: [one of [option1], [option2], [option3] or [option4]]

    Context:
    ---------
    {context}
    ---------
    Generate one trivia question:
    """

quiz_prompt = PromptTemplate(
    template=quiz_prompt_template,
    input_variables=["context"]
)

# Load quiz QA Chain
def load_quiz_chain():
    return load_qa_chain(OpenAI(temperature=0), chain_type="stuff", prompt=quiz_prompt)

quiz_chain = load_quiz_chain()

# Define character/artifact analysis prompt



# Function to get answers based on the selected character
def get_character_answer(query, character):
    # Retrieve chunks using FAISS
    relevant_chunks = char_faiss.similarity_search_with_score(query, k=10)
    
    # Filter chunks for the selected character
    filtered_chunks = [
        chunk[0] for chunk in relevant_chunks if character in chunk[0].metadata.get("characters", [])
    ]
    
    # If no filtered chunks are found, return a fallback response
    if not filtered_chunks:
        return f"Sorry, I am not sure."
    
    # Prepare inputs for the chain
    context = "\n".join([doc.page_content for doc in filtered_chunks])
    results = char_chain({
        "input_documents": filtered_chunks,
        "context": context,
        "question": query,
        "character": character
    })
    return results["output_text"]

def get_general_answer(query):
    # Retrieve chunks using the general FAISS index
    relevant_chunks = general_faiss.similarity_search_with_score(query, k=5)
    context = "\n".join([doc[0].page_content for doc in relevant_chunks])
    results = general_chain({
        "input_documents": [doc[0] for doc in relevant_chunks],
        "context": context,
        "question": query
    })
    return results["output_text"], context

def get_quiz_question():
    # Get multiple random chunks to increase variety
    query = "Random trivia for LOTR"
    relevant_chunks = general_faiss.similarity_search_with_score(query, k=10)
    # Randomly select one chunk
    selected_chunk = random.choice(relevant_chunks)
    context = selected_chunk[0].page_content

    # Generate a trivia question
    results = quiz_chain({
        "input_documents": [selected_chunk[0]],
        "context": context
    })
    response = results["output_text"]

    try:
        # More robust parsing
        question = ""
        options = []
        correct_answer = ""
        
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        for line in lines:
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif line.startswith("Options:"):
                # Split by the option letters (A., B., C., D.) instead of commas
                options_text = line.replace("Options:", "").strip()
                # Use regex or string operations to split by A., B., C., D.
                option_parts = []
                for prefix, next_prefix in [("A.", "B."), ("B.", "C."), ("C.", "D."), ("D.", None)]:
                    try:
                        start = options_text.index(prefix)
                        if next_prefix:
                            try:
                                end = options_text.index(next_prefix)
                                option = options_text[start:end].strip()
                            except ValueError:
                                option = options_text[start:].strip()
                        else:
                            option = options_text[start:].strip()
                        
                        # Remove trailing comma if it exists
                        if option.endswith(','):
                            option = option[:-1].strip()
                            
                        option_parts.append(option)
                    except ValueError:
                        continue
                options = option_parts
            elif line.startswith("Answer:"):
                correct_answer = line.replace("Answer:", "").strip()

        if not question or not options or not correct_answer or len(options) != 4:
            raise ValueError(f"Invalid quiz question response")

        return question, options, correct_answer

    except Exception as e:
        # Provide a fallback question if parsing fails
        return (
            "Who is the author of The Lord of the Rings?",
            ["A. J.R.R. Tolkien", "B. C.S. Lewis", "C. George R.R. Martin", "D. Terry Pratchett"],
            "A"
        )
#Streamlit UI

def style_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #1f1700; /* Dark sidebar background */
        }
        /* Style the "Navigate" label */
        [data-testid="stSidebar"] label {
            color: white !important; /* Make "Navigate" white */
        }
        /* Style radio button options text */
        [data-testid="stSidebar"] .css-1n76uvr {
            color: white !important; /* Radio options */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

style_sidebar()

# Add background
def add_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.95)), 
                        url('https://rare-gallery.com/thumbs/4520880-the-lord-of-the-rings-rings-the-one-ring-map-middle-earth-text-closeup.jpg');
            background-size: cover;
            background-attachment: fixed;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

add_background()

# Center character images
def center_images():
    st.markdown(
        """
        <style>
        div.stImage {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        div.stImage img {
            height: 150px !important;
            width: auto !important;
            object-fit: contain;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Make text white color
def style_text():
    st.markdown(
        """
        <style>
        body, .stMarkdown, .stTextInput label, .stSelectbox label {
            color: white !important;
        }
        .stSelectbox label, .stTextInput label {
            color: white !important;
        }
        .stSelectbox .css-1okebmr-indicatorContainer, .stSelectbox .css-1uccc91-singleValue {
            color: white !important;
        }
        div.stButton > button {
            background-color: #4a4a4a;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

style_text()

# Add font
def add_custom_fonts():
    st.markdown(
        """
        <style>
        @font-face {
            font-family: 'Ringbearer';
            src: url('https://your-font-url/ringbearer.woff2') format('woff2');
        }
        .title {
            font-family: 'Ringbearer', serif;
            font-size: 36px;
            color: #6b5a01;
            text-align: center;
            margin-bottom: 20px;
        }
                .main_title {
            font-family: 'Ringbearer', serif;
            font-size: 50px;
            color: #FFD700;
            text-align: center;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

add_custom_fonts()

st.markdown('<div class="main_title">Lord of the Rings Companion</div>', unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", ["Interview a Character", "Talk with an Expert", "Explore a Character or Artifact", "Test Your LOTR Knowledge"])

if page == "Interview a Character":
    st.markdown('<div class="title">Chat with a Lord of the Rings Character</div>', unsafe_allow_html=True)

    character_images = {
        "Gandalf": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/3724757.jpg",
        "Frodo": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/185674.jpg",
        "Aragorn": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/6707813.jpg",
        "Galadriel": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/4619594.jpg",
        "Tom Bombadil": "https://static.wikia.nocookie.net/lotr/images/c/c7/Tom_bombadil.jpg",
        "Gollum": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/1416106963.png",
        "Sauron": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/1416112395.png",
        "Saruman": "https://lordoftheringinfo.weebly.com/uploads/4/2/7/6/42762785/1416107528.png"
    }

    character = st.selectbox(
        "Choose a character to interact with:",
        list(character_images.keys())
    )

    st.image(character_images[character], use_column_width=False)
    center_images()

    st.markdown(
        f"""
        <div style="text-align: center; color: white; font-size: 15px; margin-top: 1px;">
            You are speaking with {character}.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display response
    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []

    query = st.text_input(f"Ask {character} a question:")
    if query:
        answer = get_character_answer(query, character)
        st.session_state["conversation"].append((f"You: {query}", f"{character}: {answer}"))

    if st.button("Clear Conversation History"):
        st.session_state["conversation"] = []

    # Display conversation history
    for user, bot in reversed(st.session_state["conversation"]):
        st.markdown(f"**{user}**")
        st.markdown(f"*{bot}*")

elif page == "Talk with an Expert":
    st.markdown('<div class="title">Talk with an Expert</div>', unsafe_allow_html=True)

    query = st.text_input("Ask a question about Middle-Earth:")
    if query:
        answer, context = get_general_answer(query)

        st.subheader("Answer")
        st.write(answer)
   
        st.subheader("Retrieved Context")
        st.write(context)


elif page == "Test Your LOTR Knowledge":
    st.markdown('<div class="title">Test Your LOTR Knowledge</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center;">
            Test your knowledge of Middle-Earth with this interactive quiz!
        </div>
        """,
        unsafe_allow_html=True
    )
    # Initialize quiz state
    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = {
            "questions": [],
            "user_answers": [],
            "current_q_number": 0,
            "score": 0,
            "initialized": False
        }

    # Generate questions only once when starting/restarting
    if not st.session_state.quiz_state["initialized"]:
        questions = []
        used_questions = set()  # Track used questions to avoid duplicates
        
        # Try to generate 6 unique questions
        attempts = 0
        while len(questions) < 6 and attempts < 20:  # Limit attempts to prevent infinite loop
            question, options, correct_answer = get_quiz_question()
            # Create a unique key for the question to check duplicates
            question_key = (question, tuple(options))
            
            if question_key not in used_questions:
                questions.append((question, options, correct_answer))
                used_questions.add(question_key)
            attempts += 1

        st.session_state.quiz_state["questions"] = questions
        st.session_state.quiz_state["initialized"] = True

    # Get current question
    quiz_state = st.session_state.quiz_state
    current_q_index = quiz_state["current_q_number"]

    # Display quiz
    if current_q_index < len(quiz_state["questions"]):
        question, options, correct_answer = quiz_state["questions"][current_q_index]
        
        st.subheader(f"Question {current_q_index + 1} of 6")
        st.write(question)

        # Create a unique key for the form
        form_key = f"quiz_form_{current_q_index}"
        
        with st.form(key=form_key):
            selected_option = st.radio(
                "Choose your answer:",
                options,
                key=f"quiz_q_{current_q_index}"
            )
            submit_button = st.form_submit_button("Submit Answer")
            
            if submit_button:
                quiz_state["user_answers"].append(selected_option)
                if selected_option.startswith(correct_answer):
                    quiz_state["score"] += 1
                quiz_state["current_q_number"] += 1
                st.rerun()  # Force a rerun to show next question

    else:
        # Display results
        st.success(f"Quiz Completed! You scored {quiz_state['score']} out of 6.")
        
        # Show detailed results
        for i, ((question, options, correct_answer), user_answer) in enumerate(
            zip(quiz_state["questions"], quiz_state["user_answers"])
        ):
            with st.expander(f"Question {i + 1}"):
                st.write(f"**Question:** {question}")
                st.write(f"**Your Answer:** {user_answer}")
                st.write(f"**Correct Answer:** {correct_answer}")
                is_correct = user_answer.startswith(correct_answer)
                st.write("**Result:** " + ("✅ Correct" if is_correct else "❌ Incorrect"))

        # Restart button
        if st.button("Start New Quiz"):
            st.session_state.quiz_state = {
                "questions": [],
                "user_answers": [],
                "current_q_number": 0,
                "score": 0,
                "initialized": False
            }
            st.rerun()

elif page == "Explore a Character or Artifact":
    st.markdown('<div class="title">Explore Character or Artifact</div>', unsafe_allow_html=True)
    st.markdown("Dive into the world of Middle-Earth by exploring characters or artifacts.")

    with st.form(key="analyze_form"):
        explore_type = st.radio("What would you like to explore?", ["Character", "Artifact"])
        input_name = st.text_input(f"Enter the name of the character or artifact:")
        analyze_button = st.form_submit_button("Analyze")

        if analyze_button:
            if not input_name:
                st.error(f"Please enter the name of a {explore_type.lower()} to analyze.")
            else:
                # Retrieve relevant text using FAISS
                relevant_chunks = general_faiss.similarity_search_with_score(input_name, k=4)
                
                if not relevant_chunks:
                    st.warning(f"No information found for {input_name}. Try another name.")
                else:
                    # Combine the retrieved chunks
                    context = "\n\n".join([chunk[0].page_content for chunk in relevant_chunks])
                    max_context_length = 2250
                    if len(context) > max_context_length:
                        context = context[:max_context_length]
                    # Use Langchain's chain system to analyze
                    if explore_type == "Character":
                        analysis_prompt_template = """You are an expert on 'The Lord of the Rings.' Provide an analysis of the character '{name}' based on the following context. Always respond in the example format below, and always summarize your response in 200 words or less.
                        (Example format:
                        History: []
                        Significance: []
                        Powers: [])

                        Context:
                        {context}

                        Analysis (summarize in 200 words or less):"""
                    elif explore_type == "Artifact":
                        analysis_prompt_template = """You are an expert on 'The Lord of the Rings.' Provide an analysis of the artifact '{name}' based on the following context. Always respond in the example format below, and always summarize your response in 200 words or less.
                        (Example format:
                        History: []
                        Significance: []
                        Associated Characters: [])

                        Context:
                        {context}

                        Explanation (max 200 words):"""

                    # Langchain PromptTemplate
                    analysis_prompt = PromptTemplate(
                        template=analysis_prompt_template,
                        input_variables=["name", "context"]
                    )

                    # Prepare chain
                    analysis_chain = load_qa_chain(
                        OpenAI(temperature=0.3, max_tokens=3000),
                        chain_type="stuff",
                        prompt=analysis_prompt
                    )

                    # Run the chain
                    result = analysis_chain({
                        "input_documents": [chunk[0] for chunk in relevant_chunks],
                        "context": context,
                        "name": input_name
                    })

                    # Display the retrieved context and the generated analysis
                    st.subheader(f"Analysis of {explore_type}: {input_name}")
                    st.write(result["output_text"])

                    with st.expander("Retrieved Context"):
                        st.write(context)

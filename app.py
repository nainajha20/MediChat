
from flask import Flask, render_template, request, session
from dotenv import load_dotenv

from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from src.prompt import system_prompt

import os
import re
import uuid
import traceback
import ollama


# --------------------------------------------------
# Flask App and Session Setup
# --------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "medichat-local-development-key"
)

load_dotenv()

# Store conversations on the server, not in browser cookies.
# Conversation history resets when the Flask server restarts.
conversation_store = {}


# --------------------------------------------------
# Pinecone API Key
# --------------------------------------------------

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError(
        "PINECONE_API_KEY is not set in the .env file"
    )

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


# --------------------------------------------------
# Ollama Model
# --------------------------------------------------

OLLAMA_MODEL = "llama3.2:3b"

print("Using Ollama model:", OLLAMA_MODEL)


# --------------------------------------------------
# Load Embeddings
# --------------------------------------------------

print("Loading Hugging Face embeddings...")

embeddings = download_hugging_face_embeddings()

print("Embeddings loaded successfully.")


# --------------------------------------------------
# Connect to Pinecone
# --------------------------------------------------

index_name = "medical-chatbot"

print("Connecting to Pinecone...")

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

print("Connected to Pinecone successfully.")


# --------------------------------------------------
# Retriever
# --------------------------------------------------

retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)


# --------------------------------------------------
# Prompt
# --------------------------------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


# --------------------------------------------------
# Greeting Detection
# --------------------------------------------------

def get_greeting_response(question):

    text = question.lower().strip()
    text = re.sub(r"[!?.\s]+$", "", text)

    greetings = {
        "hi": "Hello! Welcome to MediChat. How can I help you today?",
        "hello": "Hello! Welcome to MediChat. How can I help you today?",
        "hey": "Hey! I'm MediChat. How can I help you today?",
        "good morning": "Good morning! How can MediChat help you today?",
        "good afternoon": "Good afternoon! How can I help you today?",
        "good evening": "Good evening! How can I help you today?",
        "how are you": "I'm doing well, thank you for asking! I'm here to help with your medical questions.",
        "how are you doing": "I'm doing well, thank you! What can I help you with today?",
        "thank you": "You're welcome! Feel free to ask if you have another question.",
        "thanks": "You're welcome! I'm happy to help.",
        "bye": "Goodbye! Take care, and feel free to return whenever you need help.",
        "goodbye": "Goodbye! Take care of yourself."
    }

    return greetings.get(text)


# --------------------------------------------------
# RAG Function with Conversation History
# --------------------------------------------------

def get_rag_response(question, history):

    print("\n----------------------------------------")
    print("Starting MediChat...")
    print("Question:", question)

    # Step 1: Handle greetings without searching medical documents

    greeting = get_greeting_response(question)

    if greeting:
        print("Greeting detected. No retrieval needed.")

        return {
            "answer": greeting,
            "context": []
        }

    # Step 2: Improve retrieval for follow-up questions

    retrieval_query = question

    follow_up_words = [
        "they", "them", "their", "it", "its",
        "those", "these", "symptoms", "treatment",
        "causes", "signs", "complications"
    ]

    lower_question = question.lower()

    is_follow_up = (
        len(question.split()) <= 8
        or any(
            re.search(r"\b" + re.escape(word) + r"\b", lower_question)
            for word in follow_up_words
        )
    )

    if is_follow_up:
        previous_question = next(
            (
                item["content"]
                for item in reversed(history)
                if item["role"] == "user"
            ),
            None
        )

        if previous_question:
            retrieval_query = (
                previous_question + "\n" + question
            )

    # Step 3: Retrieve relevant medical documents

    print("Searching Pinecone...")

    documents = retriever.invoke(retrieval_query)

    print("Documents retrieved:", len(documents))

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    print("Context created successfully.")

    # Step 4: Build the system prompt with retrieved context

    formatted_prompt = prompt.invoke(
        {
            "input": question,
            "context": context
        }
    )

    system_message = formatted_prompt.messages[0].content

    # Step 5: Include recent conversation history

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    # Use recent messages so the model understands follow-ups.
    messages.extend(history[-8:])

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Step 6: Generate an answer using Ollama

    print("Sending request to Ollama...")

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages
    )

    answer = response["message"]["content"].strip()

    print("Ollama response received.")
    print("Answer:", answer)
    print("----------------------------------------\n")

    return {
        "answer": answer,
        "context": documents
    }


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def index():

    # Give each browser session its own conversation.
    if "conversation_id" not in session:
        session["conversation_id"] = str(uuid.uuid4())

    conversation_id = session["conversation_id"]

    if conversation_id not in conversation_store:
        conversation_store[conversation_id] = []

    return render_template("chat.html")


# --------------------------------------------------
# Chat Route
# --------------------------------------------------

@app.route("/get", methods=["GET", "POST"])
def chat():

    try:

        msg = request.form.get("msg", "").strip()

        if not msg:
            return "Please enter a question.", 400

        # Ensure the conversation exists.
        if "conversation_id" not in session:
            session["conversation_id"] = str(uuid.uuid4())

        conversation_id = session["conversation_id"]

        if conversation_id not in conversation_store:
            conversation_store[conversation_id] = []

        history = conversation_store[conversation_id]

        print("\nQuestion received:", msg)

        # Generate the response using the existing history.
        response = get_rag_response(msg, history)

        answer = response["answer"]

        # Save both messages for future follow-up questions.
        history.extend(
            [
                {
                    "role": "user",
                    "content": msg
                },
                {
                    "role": "assistant",
                    "content": answer
                }
            ]
        )

        # Keep the conversation from growing indefinitely.
        conversation_store[conversation_id] = history[-12:]

        return answer

    except Exception as e:

        print("\n========================================")
        print("ERROR OCCURRED")
        print("========================================")

        print("Error type:", type(e).__name__)
        print("Error message:", str(e))

        traceback.print_exc()

        print("========================================\n")

        return (
            "Sorry, something went wrong. "
            "Please check the terminal for the error."
        ), 500


# --------------------------------------------------
# Run Flask Application
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========================================")
    print("Starting Medical Chatbot...")
    print("========================================")

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )

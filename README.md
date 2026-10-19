MediChat -- Medical Chatbot
MediChat is a medical question-answering chatbot that provides simple
information about medical conditions. It uses a Retrieval-Augmented
Generation (RAG) approach to retrieve relevant information from medical
documents and generate answers using a locally running language model.
The project uses Flask for the web interface, Pinecone for vector
storage, Hugging Face embeddings for document retrieval, and Ollama to
generate responses locally.
Disclaimer: MediChat is an educational project and does not
replace professional medical advice, diagnosis, or treatment.

Features
- Answers medical questions using information retrieved from medical
  documents.
- Responds to common greetings and simple conversational messages.
- Supports follow-up questions using recent conversation history
  within a browser session.
- Retrieves relevant medical information from Pinecone.
- Runs the language model locally through Ollama.
- Provides a web interface built with Flask.
Tech Stack
- Programming language: Python
- Web framework: Flask
- AI framework: LangChain
- LLM runtime: Ollama
- Language model: Llama 3.2 (3B)
- Embeddings: Hugging Face Sentence Transformers
- Vector database: Pinecone
Prerequisites
Before running MediChat, install or prepare:
- Python 3.10
- Anaconda or Miniconda
- Git
- Ollama
- A Pinecone account and API key
Setup and Installation
1. Clone the repository
Open a terminal and run:
git clone https://github.com/nainajha20/MediChat.git
cd MediChat
2. Create and activate a Conda environment
conda create -n medibot python=3.10 -y
conda activate medibot
3. Install dependencies
pip install -r requirements.txt
If the Ollama Python package is not included in requirements.txt,
install it with:
pip install ollama
4. Install Ollama and download the model
Download and install Ollama from
ollama.com/download.
Download the model used by MediChat:
ollama pull llama3.2:3b
Check that the model is available:
ollama list
Make sure Ollama is running before starting the chatbot.
5. Configure environment variables
Create a .env file in the root directory of the project and add your
Pinecone API key:
PINECONE_API_KEY=your_pinecone_api_key
If your application uses a configurable Flask session secret, you can
also add:
FLASK_SECRET_KEY=replace_with_a_long_random_secret
Replace the example values with your own values. Do not commit your
.env file or API keys to GitHub.
6. Store document embeddings in Pinecone
If you are creating or rebuilding the Pinecone index, run:
python store_index.py
Make sure the index name and embedding model used by the indexing script
match the settings in the application.
The application is configured to use the Pinecone index named:
medical-chatbot
If this index has already been created and populated with the required
documents, you usually do not need to run store_index.py again.
7. Run MediChat
Start the Flask application:
python app.py
Open this address in your browser:
http://127.0.0.1:5001
Keep the terminal running while you use the chatbot.
How It Works
1. The user enters a question in the web interface.
2. Flask receives the question.
3. Hugging Face embeddings and Pinecone are used to retrieve relevant
   medical document chunks.
4. The retrieved context is added to the prompt.
5. Ollama runs the Llama 3.2 model to generate a response based on the
   prompt and retrieved information.
6. Flask sends the response back to the web interface.
7. Recent conversation history can help the chatbot understand
   follow-up questions.
Troubleshooting
Pinecone API key error
- Check that the .env file is in the project root.
- Confirm that PINECONE_API_KEY is valid and that the Pinecone index
  exists.
- Restart the application after changing environment variables.
Ollama connection error
Check that Ollama is running and the model is installed:
ollama list
If the model is missing, download it again:
ollama pull llama3.2:3b
Website cannot be reached
- Check the terminal for errors after running python app.py.
- Keep the Flask terminal open.
- Open http://127.0.0.1:5001 in your browser.
- Confirm that the application is configured to use port 5001.
The chatbot gives unrelated answers
- Check that the correct medical documents have been indexed in
  Pinecone.
- Confirm that the retrieved context is relevant to the question.
- Review the prompt instructions and retrieval settings.
Follow-up questions lose context
The application may keep recent conversation history in memory.
Restarting Flask clears in-memory history. Check the
conversation-history logic if follow-up questions are not understood
correctly.
Future Improvements
- Improve document retrieval and ranking.
- Add more reliable support for follow-up questions.
- Add multilingual question answering.
- Improve the user interface and response formatting.
- Add automated testing and response-quality evaluation.
Author
Naina Jha
GitHub: nainajha20
Medical Disclaimer
MediChat is an educational project intended to provide general medical
information. Its responses may be incomplete or inaccurate. It does not
provide a medical diagnosis and should not be used as a substitute for
professional healthcare. Always consult a qualified healthcare
professional for medical advice, diagnosis, or treatment.
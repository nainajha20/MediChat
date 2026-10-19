# MediChat

# MediChat – Medical Chatbot

MediChat is a medical question-answering chatbot that provides users with simple information about medical conditions. It uses a Retrieval-Augmented Generation (RAG) approach to retrieve relevant information from medical documents and generate answers using a locally running language model.

The project uses Flask for the web interface, Pinecone for vector storage, Hugging Face embeddings for document retrieval, and Ollama to generate responses locally.

## Features

- Answers medical questions using information retrieved from medical documents.
- Supports natural greetings and simple conversations.
- Maintains conversation history for follow-up questions within a browser session.
- Uses Pinecone to retrieve relevant medical information.
- Runs the language model locally through Ollama.
- Provides a simple web interface using Flask.

**Note:** MediChat is intended for informational purposes only. It does not replace professional medical advice, diagnosis, or treatment.

## Tech Stack

- **Programming Language:** Python
- **Web Framework:** Flask
- **LLM Runtime:** Ollama
- **Language Model:** Llama 3.2 (3B)
- **AI Framework:** LangChain
- **Embeddings:** Hugging Face Sentence Transformers
- **Vector Database:** Pinecone
- **Deployment:** Docker, AWS EC2, Amazon ECR, GitHub Actions

## Project Setup

### Prerequisites

Install the following before starting:

- Python 3.10
- Anaconda or Miniconda
- Git
- Ollama
- A Pinecone account and API key

### Step 1: Clone the repository

Open your terminal and run:

```bash
git clone https://github.com/nainajha20/MediChat.git
cd MediChat
```

### Step 2: Create a Conda environment

```bash
conda create -n medibot python=3.10 -y
conda activate medibot
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

If the Ollama Python package is not included in the requirements, install it using:

```bash
pip install ollama
```

### Step 4: Install and run Ollama

Download Ollama from:

https://ollama.com/download

Download the model used by MediChat:

```bash
ollama pull llama3.2:3b
```

Check the installed models:

```bash
ollama list
```

Make sure Ollama is running before starting the chatbot.

### Step 5: Configure environment variables

Create a `.env` file in the root directory of the project.

Add your Pinecone API key:

```env
PINECONE_API_KEY=your_pinecone_api_key
```

Optionally, configure a Flask session secret:

```env
FLASK_SECRET_KEY=replace_with_a_long_random_secret
```

Keep your API keys private. Never commit your `.env` file to GitHub.

### Step 6: Store embeddings in Pinecone

If you are creating the Pinecone index for the first time or rebuilding it, run:

```bash
python store_index.py
```

Make sure the index name and embedding model in the indexing script match the settings used by the application.

The current application expects a Pinecone index named:

```text
medical-chatbot
```

If the index has already been created and populated, you generally do not need to run this command again.

### Step 7: Run MediChat

Start the Flask application:

```bash
python app.py
```

Open the following URL in your browser:

http://127.0.0.1:5001

You can now ask MediChat medical questions.

## How It Works

1. The user enters a question through the web interface.
2. Flask receives the question.
3. Pinecone retrieves relevant document chunks using Hugging Face embeddings.
4. The retrieved information is added to the prompt.
5. Ollama generates an answer using the local Llama 3.2 model.
6. Flask returns the answer to the web interface.
7. Conversation history helps the chatbot understand follow-up questions.

## AWS Deployment Using Docker and GitHub Actions

MediChat can be deployed to AWS using Amazon EC2, Amazon ECR, Docker, and GitHub Actions.

### Deployment Overview

1. Build a Docker image of the application.
2. Push the image to Amazon ECR.
3. Launch an Ubuntu EC2 instance.
4. Configure the EC2 instance as a self-hosted GitHub Actions runner, if using that deployment approach.
5. Pull the Docker image from ECR.
6. Run the container on the EC2 instance.

### Step 1: Create an IAM user

Create an IAM user for deployment and assign only the permissions required for the deployment workflow.

The original setup used these policies:

- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEC2FullAccess`

For production deployments, prefer least-privilege IAM permissions instead of broad full-access policies.

### Step 2: Create an ECR repository

Create an Amazon Elastic Container Registry repository named:

```text
medicalbot
```

The previously configured repository URI is:

```text
315865595366.dkr.ecr.us-east-1.amazonaws.com/medicalbot
```

Use this URI only if the repository still exists in your AWS account and region.

### Step 3: Create an EC2 instance

Launch an Ubuntu EC2 instance and configure its security group to allow only the required traffic.

Install Docker:

```bash
sudo apt-get update -y
sudo apt-get upgrade -y

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo usermod -aG docker ubuntu
newgrp docker
```

Verify the installation:

```bash
docker --version
```

### Step 4: Configure a self-hosted GitHub Actions runner

In your GitHub repository:

1. Open **Settings**.
2. Select **Actions → Runners**.
3. Choose **New self-hosted runner**.
4. Select Linux and follow the displayed instructions.
5. Configure the runner on your EC2 instance.

Keep the runner software and Docker environment updated.

### Step 5: Configure GitHub repository secrets

Open **Settings → Secrets and variables → Actions** and add the secrets required by your deployment workflow.

Typical secrets include:

| Secret | Purpose |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS authentication |
| `AWS_SECRET_ACCESS_KEY` | AWS authentication |
| `AWS_DEFAULT_REGION` | AWS deployment region |
| `ECR_REPO` | Amazon ECR repository URI |
| `PINECONE_API_KEY` | Pinecone access |

Do not add `OPENAI_API_KEY` unless your deployment is specifically using an OpenAI-based version. The current local Ollama implementation does not require it.

### Step 6: Build and deploy

Configure your Dockerfile and GitHub Actions workflow to:

1. Build the application image.
2. Authenticate with Amazon ECR.
3. Push the image to the repository.
4. Pull the image on the EC2 instance.
5. Start the application container.

**Deployment note:** The current application uses a local Ollama model. Your EC2 deployment must also provide access to Ollama and the `llama3.2:3b` model, or be configured to connect to a separate Ollama service. The Docker image alone does not include the model automatically.

Ensure that the deployed application exposes port `5001` as configured in `app.py`, or update the application and container configuration consistently.

## Troubleshooting

### 1. Pinecone API key error

Check that the `.env` file exists in the project root and contains a valid `PINECONE_API_KEY`.

### 2. Ollama connection error

Make sure Ollama is running and the model is installed:

```bash
ollama list
```

If necessary, download the model again:

```bash
ollama pull llama3.2:3b
```

### 3. Website cannot be reached

Check that Flask starts without errors:

```bash
python app.py
```

Keep the terminal running and open:

http://127.0.0.1:5001

### 4. The chatbot gives unrelated answers

Check whether the correct documents are stored in Pinecone and whether the retrieved context matches the question. The quality of the response depends on the relevance of the retrieved documents and the prompt instructions.

### 5. Follow-up questions lose context

The application keeps recent conversation history in memory. Restarting Flask clears this history. Check that the Flask session and conversation-history handling are working correctly.

## Future Improvements

- Improve document retrieval and ranking.
- Add support for more medical documents.
- Improve conversation-history management.
- Add multilingual question answering.
- Improve the user interface and response formatting.
- Add automated testing and deployment monitoring.

## Author

**Naina Jha**

GitHub: https://github.com/nainajha20

## Disclaimer

MediChat is an educational project intended to provide general medical information. Its responses may be incomplete or inaccurate. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.

# AI Learning Assistant

An interactive **AI-powered educational assistant** built with **LangChain**, **OpenAI**, and **Streamlit**, designed to enhance learning from textbooks. This tool allows users to upload PDF study material and either:
- Take a **quiz** auto-generated from the content, or
- Ask **doubts/questions** about the material and receive intelligent responses.
  
## Features

### Upload and Learn
- Upload any **textbook PDF** (academic, technical, etc.)
- Text is parsed and indexed with vector embeddings for retrieval-based Q&A

### Quiz Mode
- Generate topic-based questions dynamically
- Submit answers and receive:
  - Contextual evaluation
  - Scoring (1-10 scale)
  - Feedback and improvement tips

### Doubt Mode
- Chat-based interface to ask questions related to the uploaded document
- Powered by **OpenAI's GPT-3.5 Turbo** and **LangChain's RAG**

### Session Persistence
- Retains session state for smooth user experience across steps
- Option to reset/restart session

---

## 📂 Project Structure

📁 ai-learning-assistant/
│
├── main.py                # Streamlit app
├── .env                  # (Optional) For local OpenAI API key
├── requirements.txt       # Python dependencies
├── README.md              # Project overview


## Tech Stack

| Component       | Technology Used                   |
|----------------|------------------------------------|
| UI              | Streamlit                         |
| Language Model  | OpenAI (gpt-3.5-turbo)             |
| Vector Store    | FAISS (via LangChain)             |
| Embeddings      | text-embedding-ada-002            |
| Text Splitter   | CharacterTextSplitter (LangChain) |
| File Loader     | PyPDFLoader (LangChain)           |
| Environment     | Python 3.10+                      |


##  Setup Instructions
### 1. Clone the Repository
git clone https://github.com/madhunikitha/mini_project_mouritech
cd mini_project_mouritech
### 2.Create virtual environment
python -m venv myenv
myenv\Scripts\activate
### 3. Install Dependencies
  pip install -r requirements.txt
### 4. Set OpenAI API Key
Option A: Streamlit Cloud
  Create .streamlit/secrets.toml and add:
  [general]
  OPENAI_API_KEY = "sk-..."
Option B: Local Environment
  Create a .env file and add:
  OPENAI_API_KEY=sk-...
### 5. Run the App
streamlit run main.py

## 🎯 Use Cases

- 🎓 **Academia**: Help students self-test on educational material
- 📚 **Independent Learning**: Self-assessment tool for personal development
- 🧑‍🏫 **Tutoring**: AI-powered assistant for exam prep and subject clarification

## 🧠 Behind the Scenes

### 🔄 Retrieval Augmented Generation (RAG)

- Uploaded PDFs are **split into chunks**
- Embeddings are generated using **`text-embedding-ada-002`**
- Chunks are **indexed using FAISS**
- During interactions, the app **retrieves the most relevant chunks** before invoking GPT

### 📝 Evaluation System

For each quiz answer, the system:

- Retrieves **relevant context** from the textbook
- **Scores** the answer based on:
  - Correctness
  - Completeness
  - Relevance
  - Clarity
- Provides **specific feedback and suggestions** for improvement


## 📌 Sample Workflow

1. **Upload** a textbook or study material (PDF)
2. Choose a mode:
   - 🧪 **Quiz**:  
     - Enter a topic  
     - Get 3 AI-generated questions  
     - Submit answers  
     - Receive contextual evaluation with scores and feedback
   - ❓ **Doubt**:  
     - Ask a question  
     - Get a GPT-powered response using content from your uploaded material
3. Use the 🔄 **Restart** button to reset and start over

import os
import streamlit as st
import tempfile
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from openai import RateLimitError, OpenAIError
import time

# Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# Debug API key loading (remove in production)
if not api_key:
    print("❌ API key not loaded. Check your .env file.")
else:
    print("✅ API key loaded.")

# LLM
llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

# Session State Initialization
for key in ["mode", "step", "topic", "questions", "answers", "chat_history", "rag_chain"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []

# Restart Button
if st.button("🔄 Restart"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.title("📘 AI Learning Assistant")

# Step 0: Upload PDF
if st.session_state.rag_chain is None:
    st.subheader("Step 1: Upload your textbook PDF")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        # Split documents
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        split_docs = splitter.split_documents(docs[:5])  # Limit to first 5 pages for testing

        # Create embeddings (with error handling)
        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
            vectorstore = Chroma.from_documents(split_docs, embedding=embeddings, collection_name="user_pdf")
            retriever = vectorstore.as_retriever()
            st.session_state.rag_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
            st.success("✅ PDF processed! Choose what to do next.")
            st.rerun()

        except RateLimitError:
            st.error("🚨 Rate limit or quota exceeded. Please wait or check your plan.")
            st.stop()
        except OpenAIError as e:
            st.error(f"❌ OpenAI error: {e}")
            st.stop()

# Step 1: Choose Mode
elif st.session_state.mode is None:
    st.subheader("Step 2: Choose what you want to do:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Take a Quiz"):
            st.session_state.mode = "quiz"
            st.session_state.step = 0
            st.rerun()
    with col2:
        if st.button("❓ Ask a Doubt"):
            st.session_state.mode = "doubt"
            st.rerun()

# Generate Quiz Questions
def generate_topic_questions(topic):
    context_result = st.session_state.rag_chain.invoke(f"Give study material or explanation about: {topic}")
    context = context_result.get("result", "")
    prompt = f"""
You are an expert question setter.

Based on the following textbook content related to the topic **{topic}**, generate 3 relevant exam-style questions.

Textbook Excerpt:
\"\"\"{context}\"\"\"

Output Format:
1. <Question>
2. <Question>
3. <Question>
"""
    response = llm.invoke(prompt)
    content = response.content.strip()
    questions = [line.strip()[3:] for line in content.splitlines() if line.strip().startswith(tuple("123"))]
    return questions[:3]

# Evaluate Student Answers
def evaluate_all_answers(questions, answers):
    total_score = 0
    results = []

    for q, a in zip(questions, answers):
        context = st.session_state.rag_chain.invoke(f"Context for: {q}")["result"]
        prompt = f"""
You are an expert academic evaluator.

Using the provided textbook content, evaluate the student's answer for the question below.

Be strict but fair. Consider the following:
- Factual correctness
- Completeness of the answer
- Relevance to the textbook context
- Clarity and understanding

Give the final result in this format:

Score: <1-10>  
Feedback: <brief but specific comment>  
Improvement: <one suggestion for a better answer>

---

Question: {q}

Student's Answer:
\"\"\"{a}\"\"\"

Textbook Context:
\"\"\"{context}\"\"\"
"""
        evaluation = llm.invoke(prompt).content.strip()
        try:
            score_line = next(line for line in evaluation.splitlines() if "Score" in line)
            score = int("".join(filter(str.isdigit, score_line)))
        except:
            score = 0
        total_score += score
        results.append(f"📌 Q: {q}\n📝 A: {a}\n✅ {evaluation}")

    final = f"\n📊 Final Score: {total_score} / {len(questions) * 10}"
    return "\n\n---\n\n".join(results) + final

# Quiz Mode
if st.session_state.mode == "quiz":
    st.header("🧪 Quiz Mode")

    if st.session_state.step == 0:
        topic = st.text_input("Enter a topic you'd like to be quizzed on:")
        if topic and st.button("Start Quiz"):
            questions = generate_topic_questions(topic)
            if not questions:
                st.error("⚠️ Could not generate questions. Try a different topic.")
            else:
                st.session_state.topic = topic
                st.session_state.questions = questions
                st.session_state.step = 1
                st.rerun()

    elif 1 <= st.session_state.step <= 3:
        current_q = st.session_state.questions[st.session_state.step - 1]
        st.markdown(f"**❓ Question {st.session_state.step}: {current_q}**")
        answer = st.text_area("Your Answer:")

        if st.button("Submit Answer"):
            if st.session_state.answers is None:
                st.session_state.answers = []
            st.session_state.answers.append(answer)
            st.session_state.step += 1
            st.rerun()

    elif st.session_state.step > 3:
        st.success("✅ Quiz Completed!")
        evaluation = evaluate_all_answers(st.session_state.questions, st.session_state.answers)
        st.markdown(evaluation)

# Doubt Mode
if st.session_state.mode == "doubt":
    st.header("💬 Doubt Mode (Chat)")

    user_input = st.chat_input("Ask a doubt about your uploaded PDF...")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = st.session_state.rag_chain.invoke(user_input)["result"]
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            st.write(response)

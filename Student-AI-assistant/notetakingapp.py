import streamlit as st
import os
from openai import OpenAI
import pymupdf as fitz  # PyMuPDF for reading PDF files
from docx import Document  # python-docx for reading Word files
import time

# Initialize OpenAI API key
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# CSS for custom styling
st.markdown("""
    <style>
    body {
        background-color: #f7f7f7;
        font-family: 'Arial', sans-serif;
    }
    .app-background {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 800px;
        margin: auto;
    }
    .stButton>button {
        background-color: #007BFF; /* Blue */
        border: none;
        color: white;
        padding: 12px 25px;
        text-align: center;
        font-size: 16px;
        border-radius: 5px;
        transition: background-color 0.3s, transform 0.2s;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: scale(1.05);
    }
    .title {
        font-size: 36px;
        color: #ffffff;  /* Title color changed to white */
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 18px;
        color: #666666;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        background-color: #f7f7f7;
        border: 1px solid #cccccc;
        border-radius: 5px;
        color: #333333;  /* Text color changed to black for readability */
    }
    .note-container {
        margin-bottom: 20px;
    }
    .note-container label {
        font-weight: bold;
        color: #333366;
    }
    </style>
    """, unsafe_allow_html=True)

# Functions for file processing and AI calls

# Function to extract text from PDF file
def extract_text_from_pdf(uploaded_file):
    pdf_text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf_doc:
        for page_num in range(pdf_doc.page_count):
            pdf_text += pdf_doc[page_num].get_text()
    return pdf_text

# Function to extract text from Word file
def extract_text_from_word(uploaded_file):
    doc = Document(uploaded_file)
    doc_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return doc_text

# Function to generate a summary from the uploaded note
def generate_summary(note_text):
    response = client.chat.completions.create(
        model="gpt-4",  # Use a suitable model like "gpt-3.5-turbo"
        messages=[{"role": "system", "content": f"Please summarize the following text:\n\n{note_text}"}],
        max_tokens=300,
        temperature=0.5
    )
    summary = response.choices[0].message.content.strip()
    return summary

# Function to generate Q&A based on the uploaded note
def generate_qa(note_text):
    response = client.chat.completions.create(
        model="gpt-4",  # Use a suitable model like "gpt-3.5-turbo"
        messages=[{"role": "system", "content": f"Please generate Questions and Answers based on the following text:\n\n{note_text}"}],
        max_tokens=1000,
        temperature=0.5
    )
    q_and_a = response.choices[0].message.content.strip()
    return q_and_a

# Function to answer questions based on the uploaded notes
def answer_question(note_text, question):
    response = client.chat.completions.create(
        model="gpt-4",  # Use a suitable model like "gpt-3.5-turbo"
        messages=[{"role": "system", "content": f"Based on the following note, answer the question:\n\nNote:{note_text}\n\nQuestion: {question}"}],
        max_tokens=200,
        temperature=0.5
    )
    answer = response.choices[0].message.content.strip()
    return answer

# Function to download a text as a file
def download_file(content, filename):
    st.download_button(
        label="Download Summary",
        data=content,
        file_name=filename,
        mime="text/plain"
    )

# Streamlit app interface

st.markdown('<p class="title">📝 Note Summarizer & Q&A App</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your notes and interact with AI to get summaries, Q&A, and answers to your questions!</p>', unsafe_allow_html=True)

# Upload note section
uploaded_file = st.file_uploader("Upload your lecture note (Text, PDF, or Word file)", type=["txt", "pdf", "docx"])

note_text = ""
if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == "pdf":
        note_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        note_text = extract_text_from_word(uploaded_file)
    else:
        note_text = uploaded_file.read().decode("utf-8")
    st.text_area("Uploaded Note:", note_text, height=300)

# Tabs for functionality
tab1, tab2, tab3 = st.tabs(["Generate Summary", "Generate Q&A", "Answer a Question"])

with tab1:
    st.header("Generate Summary")
    if st.button("📄 Generate Summary"):
        with st.spinner('Running... Please wait a moment!'):
            time.sleep(2)  # Simulate processing time
            summary = generate_summary(note_text)
            st.write("### Summary:")
            st.write(summary)
            # Add download button for the summary
            download_file(summary, "summary.txt")

with tab2:
    st.header("Generate Q&A")
    if st.button("❓ Generate Q&A"):
        with st.spinner('Running... Please wait a moment!'):
            time.sleep(2)  # Simulate processing time
            q_and_a = generate_qa(note_text)
            st.write("### Q&A based on the Note:")
            st.write(q_and_a)

with tab3:
    st.header("Answer a Question")
    question = st.text_input("Enter your question here:")
    if st.button("💡 Get Answer"):
        if question:
            with st.spinner('Running... Please wait a moment!'):
                time.sleep(2)  # Simulate processing time
                answer = answer_question(note_text, question)
                st.write("### Answer:")
                st.write(answer)
        else:
            st.warning("Please enter a question to get an answer.")

st.markdown("</div>", unsafe_allow_html=True)

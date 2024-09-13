# document_parser.py
import os
from openai import AsyncOpenAI
from PyPDF2 import PdfReader
import docx2txt

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

async def extract_text_from_docx(file_path):
    text = docx2txt.process(file_path)
    return text

async def extract_tasks(text):
    prompt = f"""
    Extract the tasks, timelines, and data requirements from the following project scope:

    {text}

    Provide the output in JSON format with keys 'tasks' (list of tasks), 'timelines' (list of timelines), and 'data_requirements' (list of data requirements).
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0
    )
    content = response.choices[0].message.content
    return content

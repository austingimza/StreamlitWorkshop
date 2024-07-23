# Necessary imports
import streamlit as st
from openai import OpenAI
import os
import json
from docx import Document
from pdfminer.high_level import extract_text

st.set_page_config(page_title='Resume Comparer', page_icon=':globe_with_meridians:')

# Set API key and prompt
api_key = os.getenv('OPENAI_KEY')
prompt = """Act as a career mentor. Your job is to help candidates determine how qualified they are for the positions and identify areas of improvement. The user will give you their resume along with the posted job description. Your job is to identify the key skills and qualifications required for the position based on the job description, then determine how qualified the candidate is for the job by comparing these skills and qualifications to their resume. Your response will ONLY contain how qualified a candidate is by a percentage, and if the candidate is not 100% qualified you will return a list of missing skills and qualifications and a summary of which skills they should focus on improving to become a better candidate. Your output should ONLY contain a Python dictionary containing the requested information, do not add any additional text or explanation to your response. Here is an example of a sample output: {"qualification_percent" : 80, "missing_skills_and_qualifications" : ['2 years of data analysis experience', 'Python for data analysis', 'Strong communication skills'], "summary" : 'While you process experience with SQL, I recommend you focus on learning to use Python for data analysis. I also recommend trying to find an entry-level data analyst position to gain additional experience and refine your communication skills'}"""

def read_docx(file):
    """Takes in .docx file, returns text."""
    doc = Document(file)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def model_response(text,job, prompt=prompt):
    """Takes in resume and job description, returns model response."""
    if not api_key:
        st.error("OpenAI API key is not set. Please add it to environment variables")
        return
        
    client = OpenAI(api_key=api_key)
    model = "gpt-3.5-turbo" 

    messages = [
      {"role": "system", "content": prompt},
      {"role": "user", "content": f"Resume:\n{text}\nJob Description:\n{job}"}
        ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0  
        )
    
    return response.choices[0].message.content

def read_file(file):
    """Determines if the filetype is supported and returns the text of supported files.""" 
    if file.name.lower().endswith('.pdf'):
            model_input = extract_text(upload)

    elif file.name.lower().endswith('.docx'):
            model_input = read_docx(upload)

    else:
        st.write('Invalid file type. Please use .pdf and .docx files only.')
    
    return model_input
             
def analyze_resume(job=None, text=None, upload=None):
    """Determines which input methods are being used and outputs the model response."""
    # Logic to determine which method of inputs the user is using
    if text and job:
        model_input = text
    
    elif upload and job:
        model_input = read_file(upload)
    
    else:
        st.write('Please fill both fields or upload a resume.')
    
    # Calling the model and outputting the response
    try:
        with st.spinner(text="In progress"):
            response = json.loads(model_response(model_input,job))

        st.markdown(f"## You are a {response['qualification_percent']}% match for this job.")
        st.markdown('### Missing Skills and Qualifications:')

        for item in response['missing_skills_and_qualifications']:
            st.write(f"- {item}")
        st.markdown(f"\n{response['summary']}")
    
    # Remove a repeat error message, error handled in input logic
    except NameError:
        pass


st.html("""<head>
<style>
h1 {text-align: center;}
p {text-align: center;}
</style>
</head>
<body>

<h1>How Qualified are you?</h1>
<p>Let's find out!</p>

</body>
</html>""")

col1, col2 = st.columns([0.5,0.5])

# Taking user input
with col1:
    text = st.text_area('Input your resume here')
    upload = st.file_uploader('Or Upload your Resume', type=['docx','pdf'])
with col2:
    job = st.text_area('Input the job description here')

if st.button('Compare!'):
    analyze_resume(job,text,upload)

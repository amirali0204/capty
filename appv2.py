import os
import openai
import pandas as pd
from flask import Flask, render_template, request

# OpenAI API key 
openai.api_key = os.getenv("OPENAI_API_KEY")

# initialize Flask App
app = Flask(__name__)

# Flask route configurations...
# route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Function to estimate token count
def estimate_token_count(text):
    return len(text.split())

# Function to handle OpenAI requests
def ask_openai(prompt):
    estimated_prompt_tokens = estimate_token_count(prompt)
    max_response_tokens = max(1, 4096 - estimated_prompt_tokens)

    response = openai.ChatCompletion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=max_response_tokens
    )
    return response.choices[0].text.strip()

# ask openai to rewrite the combined generated content
def rewrite_content_with_instructions(content, instructions):
    prompt = f"Original Content: {content}\nInstructions: {instructions}\nRewrite:"
    
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1500
    )
    
    return response.choices[0].text.strip()

# Function to process each row of the DataFrame
def process_row(row):
    combined_results = []
    for i in range(1, 21):
        question_col = f'Question {i}'
        answer_col = f'Answer {i}'

        # Check if the question column is not empty
        if pd.notna(row[question_col]):
            question = row[question_col]
            result = ask_openai(question)
            combined_results.append(result)

            # Update the row with the result
            row[answer_col] = result

    # Combine OpenAI results
    combined_content = ' '.join(combined_results)

    # Rewrite combined content
    rewritten_content = rewrite_content_with_instructions(combined_content, row['Rewrite instructions'])

    # Update row with combined and rewritten content
    row['Combined_Content'] = combined_content
    row['Rewritten_Content'] = rewritten_content

    return row

# Flask route for file upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    # File upload handling...
    if 'file' not in request.files:
        return render_template('error.html', error='No selected file')
    
    file = request.files['file']

    # Read the input file
    df = pd.read_excel(file)

    # Process each row
    df = df.apply(process_row, axis=1)

    # Save the output Excel file
    output_file_path = 'static/flask_output_file_v2.xlsx'
    df.to_excel(output_file_path, index=False)

    # Flask render_template or return response...

# Other Flask routes and functions...

if __name__ == '__main__':
    app.run(debug=True)

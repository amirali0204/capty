import os
import openai
import pandas as pd
from flask import Flask, render_template, request

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask App
app = Flask(__name__)

# Function to process each row using ChatCompletion API
def process_row(row):
    messages = []
    combined_results = []

    for i in range(1, 21):  # Assuming 20 questions per row
        question_col = f'Question {i}'
        answer_col = f'Answer {i}'

        # Check if the question column is not empty
        if pd.notna(row[question_col]):
            question = row[question_col]
            messages.append({"role": "user", "content": question})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            answer = response.choices[0].message['content']
            combined_results.append(answer)

            # Update the chat history
            messages.append({"role": "assistant", "content": answer})

            # Update the row with the result
            row[answer_col] = answer

    # Combine OpenAI results
    combined_content = ' '.join(combined_results)
    row['Combined_Content'] = combined_content

    # Rewrite combined content if instructions are provided
    if pd.notna(row.get('Rewrite instructions')):
        rewritten_content = rewrite_content_with_instructions(combined_content, row['Rewrite instructions'])
        row['Rewritten_Content'] = rewritten_content

    return row

# Function to rewrite content with instructions using Completion API
def rewrite_content_with_instructions(content, instructions):
    # Function to estimate token count
    def estimate_token_count(text):
        return len(text.split())

    # Construct the prompt
    prompt = f"Original Content: {content}\nInstructions: {instructions}\nRewrite:"
    
    # Estimate the token count of the prompt
    estimated_prompt_tokens = estimate_token_count(prompt)
    
    # Adjust the max tokens for the response
    max_response_tokens = 4096 - estimated_prompt_tokens
    max_response_tokens = max(50, min(max_response_tokens, 1500))  # Ensuring it's a positive number and not too large

    # Check if we need to split the content
    if estimated_prompt_tokens >= 4096:
        # Handle long content (splitting or summarization logic goes here)
        # For now, let's just truncate the content to fit the limit
        prompt = prompt[:4096]

    # Call the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=max_response_tokens
    )
    
    return response.choices[0].text.strip()

# Flask route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Flask route for file upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('error.html', error='No selected file')
    
    file = request.files['file']

    if file:
        # Read the input file
        df = pd.read_excel(file)

        # Process each row
        df = df.apply(process_row, axis=1)

        # Save the output Excel file
        output_file_path = 'static/flask_output_file_v3.xlsx'
        df.to_excel(output_file_path, index=False)

        return render_template('index.html', result_file=output_file_path)

if __name__ == '__main__':
    app.run(debug=True)

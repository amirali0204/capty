import os
import openai
import pandas as pd

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# import environ

# env= environ.Env()
# environ.Env.read_env()

# OpenAI API key 
openai.api_key = os.getenv("OPENAI_API_KEY")

# initialize Flask App
app = Flask(__name__)

# route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# route fot handling file upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('error.html', error='No selected file')
    
    file = request.files['file']

    if file:
        # read the input file
        df = pd.read_excel(file)

        # Columns to store OpenAI results
        for i in range(1, 21):
            question_col = f'Question {i}'
            answer_col = f'Answer {i}'
            df[answer_col] = ''

        df['Combined_Content'] = ''
        df['Rewritten_Content'] = ''

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            combined_results = []
            for i in range(1, 21):
                question_col = f'Question {i}'
                answer_col = f'Answer {i}'

                # Check if the question column is not empty
                if pd.notna(row[question_col]):
                    question = row[question_col]
                    result = ask_openai(question)
                    combined_results.append(result)

                    # Update DataFrame with the result
                    df.at[index, answer_col] = result

            # Combine OpenAI results
            combined_content = ' '.join(combined_results)

            # Rewrite combined content
            rewritten_content = rewrite_content_with_instructions(combined_content, row['Rewrite instructions'])

            print(row['Rewrite instructions'])

            # Update DataFrame with combined and rewritten content
            df.at[index, 'Combined_Content'] = combined_content
            df.at[index, 'Rewritten_Content'] = rewritten_content

        # Save the output Excel file
        output_file_path = 'static/flask_output_file.xlsx'
        df.to_excel(output_file_path, index=False)

        print(f"Script executed successfully. Results saved to {output_file_path}")
        print(df['Rewritten_Content'])

        return render_template('index.html', result_file=output_file_path, content = df["Rewritten_Content"])

# ask openai for content generation
def ask_openai(prompt):
    response = openai.Completion.create(
        engine = "text-davinci-002",
        prompt = prompt,
        max_tokens = 1500
    )
    return response.choices[0].text.strip()

def rewrite_content_with_instructions(content, instructions):
    prompt = f"Original Content: {content}\nInstructions: {instructions}\nRewrite:"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1500
    )
    
    return response.choices[0].text.strip()
    
if __name__ == '__main__':
    app.run(debug=True)


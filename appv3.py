import openai
import openpyxl
from flask import Flask, render_template, request
import pandas as pd

# Set your OpenAI API key here
openai.api_key = 'OPENAI_API_KEY'

app = Flask(__name__)

def generate_content(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def process_excel(file):
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
                rewrite_ccol = f'Rewrite instructions'

                # Check if the question column is not empty
                if pd.notna(row[question_col]):
                    question = row[question_col]
                    result = generate_content(question)
                    combined_results.append(result)

                    # Update DataFrame with the result
                    df.at[index, answer_col] = result

            # Combine OpenAI results
            combined_content = ' '.join(combined_results)

            # Rewrite combined content
            rewrite_prompt = f"Original Content: {combined_content}\nInstructions: {row[rewrite_ccol]}\nRewrite:"
            rewritten_content = generate_content(rewrite_prompt)

            print(row['Rewrite instructions'])

            # Update DataFrame with combined and rewritten content
            df.at[index, 'Combined_Content'] = combined_content
            df.at[index, 'Rewritten_Content'] = rewritten_content

        # Save the output Excel file
        output_file_path = 'static/flask_output_file.xlsx'
        df.to_excel(output_file_path, index=False)

        content = df["Rewritten_Content"]

        return output_file_path, content

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            input_file = file.filename
            file.save(input_file)
            output_file, content = process_excel(input_file)
            return render_template('index.html', output_file=output_file, content=content)

if __name__ == '__main__':
    app.run(debug=True)
import pandas as pd
import openai
from langchain.chains import OpenAIChain

# Load the Excel file
file_path = '../data/research_data.xlsx'  # Change this to your file path
df = pd.read_excel(file_path)

# Initialize OpenAI
openai.api_key = 'OPENAI_API_KEY'  # Replace with your OpenAI API key
chain = OpenAIChain()

# Process each row in the DataFrame
for index, row in df.iterrows():
    combined_content = ""
    for i in range(1, 21):
        question_col = f'Question {i}'
        answer_col = f'Answer {i}'
        if question_col in df.columns and pd.notna(row[question_col]):
            # Generate response using OpenAI
            response = chain.complete(row[question_col])
            df.at[index, answer_col] = response
            combined_content += f"{response} "

    # Add combined content
    df.at[index, 'Combined Content'] = combined_content.strip()

    # Rewrite the combined content
    rewritten_content = chain.rewrite(combined_content)
    df.at[index, 'Rewritten Content'] = rewritten_content

# Save the updated DataFrame to a new Excel file
df.to_excel('updated_content.xlsx', index=False)
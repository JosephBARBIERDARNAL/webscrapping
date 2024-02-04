import sys
import os
from openai import OpenAI


def call_openai_api(prompt, model="gpt-3.5-turbo"):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    messages = [{"role": "system", "content": "Write a cover letter for the following job"},
                {"role": "user", "content": prompt}]
    completion = client.chat.completions.create(model=model, messages=messages)
    
    return completion.choices[0].message.content

def main():
    if len(sys.argv) != 3:
        print("Usage: python call_openai.py 'resume' 'job_description'")
        sys.exit(1)

    # get arguments for gpt
    resume = sys.argv[1]
    job_description = sys.argv[2]
    
    prompt = f"{resume}\n\n{job_description}"
    print('Prompt sent: ', prompt)
    result = call_openai_api(prompt)
    
    with open("response.txt", "w") as file:
        file.write(result)

if __name__ == "__main__":
    main()

from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from pyswip import Prolog


#loads environment vairables from .env file (you may have to creaet one for yourself)
load_dotenv()

#Intializing OPENAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def natural_language_to_prolog(client, query):
    """
    This function takes a NL query and converts it to Prolog code
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a natural language to Prolog converter. Only return valid Prolog code with no explanations, no comments, and no markdown formatting. Do not include ``` or any descriptive text. Always include a query line starting with '?-' at the end."},
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content

def run_prolog(instructions):
    """
    This function takes Prolog code and compiles it
    """
    prolog = Prolog()
    lines = instructions.strip().split("\n")

    query_result = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("%"):  # Skip empty lines or comments
            continue
        if line.startswith("?-"):
            query = line[2:].strip().rstrip(".")
            query_result = list(prolog.query(query))
        else:
            code_line = line.rstrip(".")
            if ":-" in code_line and code_line.strip().endswith(":-"):
                print(f"Skipping incomplete rule: {code_line}")
                continue
            prolog.assertz(code_line)


    return query_result

def write_into_file(filename,  data):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def main():
    user_input = "Who is the ancestor of jim if john is the parent of mary and mary is the parent of jim?"
    gpt_instructions = natural_language_to_prolog(client, user_input)
    instructions = gpt_instructions.replace("```prolog", "").replace("```", "").strip()
    result = run_prolog(instructions)

    output_file = {
        "user_query": user_input,
        "prolog_code": instructions,
        "result": result
    }

    print("writing...")

    write_into_file("output_results.json", output_file)

    print("Done writing into file")

if __name__ == "__main__":
    main()

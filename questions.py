from utils import load_json
import random
from connection import connect_wxai
from ibm_watsonx_ai import APIClient
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures as cf
import pandas as pd
import re

def gen_questions(input, deployment_id="83a87832-3d6c-412b-be91-6f3a76a535c0"):
    client = input[0]
    doc = input[1]
    ruling = doc['output']
    ref = doc['id']
    params_dict ={ "prompt_variables": { 
        "ruling": ruling
        } 
        } 
    response = client.deployments.generate_text(
        params=params_dict,
        deployment_id=deployment_id)
    
    return response, ref


if __name__ == "__main__":
    raw_data = load_json('../ibm_pr_clean.json')
    ref_docs = random.sample(raw_data, 100)
    wxai_cred = connect_wxai()
    
    wx_client = APIClient(wxai_cred)
    wxai_space_id = "62a4dc39-5e54-463d-acb1-70f079094bcc"
    wx_client.set.default_space(wxai_space_id)
    questions_set=[]
    output_questions = '../aili_genai_questions.csv'
    # try:
    with ThreadPoolExecutor(max_workers=8) as executer:
            format_bulk_ingest = {executer.submit(gen_questions, [wx_client, doc]): doc for doc in ref_docs}
                
            for format_future in cf.as_completed(format_bulk_ingest):
                response =format_future.result()
                questions = response[0]
                questions = re.sub(r'Member of the Public:\n', '', questions)
                ref = response[1]
                split_questions = re.split(r'\d+\.\s*', questions)
                print(split_questions)
                questions_set.extend([{ "question": q.strip(), "persona": 'tax professional', "reference": ref } for q in split_questions[:3]])
                questions_set.extend([{ "question": q.strip(), "persona": 'public', "reference": ref } for q in split_questions[3:]])

    # except Exception as e:
    #     print(e)
    #     dfoutput = pd.DataFrame(questions_set)
    #     dfoutput.to_csv(output_questions, index=False)
                
    dfoutput = pd.DataFrame(questions_set)
    dfoutput.to_csv(output_questions, index=False)

import requests
import json
import re
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
import pandas as pd
import concurrent.futures
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

## WA apikey and endpoint, Only need to setup these if you wish to get the answer through WA API of your deployed assistant
wa_apikey = "xxx" 
wa_endpoint = "xxx"

## watsonx API key, you can get that from you ibm cloud account
wx_apikey = "xxx"

## Elatic Search endpoints and credentials, you can get that from you elastic search instance
elastic_url = "xxx"
username = "xxx"
password = "xxx"
index_name = 'test_elser_index_5' 

## Please setup the input and output path for csv sheet.
input_csv_file_path = 'input/Assistant_Utterance_Testing.csv'
output_csv_file_path = 'output/Assistant_Utterance_Testing.csv'

def watson_assistant_api(query):
    authenticator = IAMAuthenticator(wa_apikey)
    assistant = AssistantV2(
        version='2021-06-14',
        authenticator = authenticator
    )

    assistant.set_service_url(wa_endpoint)

    try:
        response = assistant.message_stateless(
            assistant_id='c93f88f0-4dca-4f34-b013-4019024ccde9',
            input={
                'message_type': 'text',
                'text': query
            }
        ).get_result()
        return response["output"]["generic"][0]["text"]
    except Exception as e:
        return "ERROR: WA API FAIL"

def auth_watsonx(wx_apikey):

    url = "https://iam.cloud.ibm.com/identity/token"

    payload = f'grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey&apikey={wx_apikey}'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        access_token = response.json().get("access_token")
        return access_token
    except RequestException as e:
        print(f"Failed to authenticate with Watsonx: {e}")
        return ""

def invoke_watsonx_deployment(access_token, service_name, deployment_input):
    url = f"https://us-south.ml.cloud.ibm.com/ml/v1/deployments/{service_name}/text/generation?version=2021-05-01"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f"Bearer {access_token}",
    }
    try:
        response = requests.post(url, headers=headers, json=deployment_input)
        response.raise_for_status()
        return response.json().get("results")[0].get("generated_text")
    except RequestException as e:
        print(f"Failed to invoke Watson deployment: {e}")
        return "WX DEPLOYMENT ERROR"

def get_query_summary(access_token, query):
    ## please change the service_name if you wish use other deployed prompt template for rewriting query
    service_name = "rewrite_llama"
    deployment_input = {
        "parameters": {
            "prompt_variables": {
            "conversation_history": f"\"a\":\"Welcome, how can I assist you?\"\n\"u\":\"{query}\",",
            "query": query
            }
        }
    }
    generated_text = invoke_watsonx_deployment(access_token, service_name, deployment_input)
    
    rewriten_query_match = re.search(r'<Query>(.*?)</Query>', generated_text)
    summary_match = re.search(r'<Summary>(.*?)</Summary>', generated_text)
    rewriten_query = rewriten_query_match.group(1) if rewriten_query_match else "ERROR: No Query Extraction"
    summary = summary_match.group(1) if summary_match else "ERROR: No Summary Extraction"

    return {"raw_generation": generated_text, "rewriten_query": rewriten_query, "summary": summary}

def generation_anwser(access_token, query, documents, summary):
    ## please change the service_name if you wish use other deployed prompt template for generating final answer
    service_name = "answer_w_history_student_mixtral_m2"
    deployment_input = {
        "parameters": {
            "prompt_variables": {
                "documents": documents,
                "history_summary": summary,
                "query": query
            }
        }
    }
    generated_text = invoke_watsonx_deployment(access_token, service_name, deployment_input)
    return generated_text


def invoke_es(query, query_size):
    url = f"{elastic_url}/{index_name}/_search"
    
    ## Elatic Search Request body please change here  
    request_body = {
        "size": query_size,
        "query": {
            "text_expansion": {
                "web_text_embedding": {
                    "model_id": ".elser_model_2",
                    "model_text": query
                }
            }
        },
        "knn":{
            "field":"web_text_dense",
            "query_vector_builder": {
            "text_embedding": {
                "model_id": "sentence-transformers__all-minilm-l12-v2",
                "model_text": query,
                    }
                },
            "k": 10,
            "num_candidates": 50
        },
        "rank" : {"rrf": {"window_size": 50,
                    "rank_constant": 20}}
    }
    try:
        response = requests.post(url, json=request_body, auth=HTTPBasicAuth(username, password), verify=False)
        response.raise_for_status()
        return response.json().get("hits", {}).get("hits", [])
    except requests.exceptions.RequestException as e:
        print(f"Failed to make request to Elasticsearch: {e}")
        return []

def parse_es_results(query, query_size):
    context = get_query_summary(auth_watsonx(wx_apikey), query)

    es_response = invoke_es(context["rewriten_query"],query_size)

    results = []
    for result in es_response:
        source = result.get("_source", {})
        results.append({
            "_score": result.get("_score", 0),
            "heading": source.get("heading", "ERROR_ES_SEARCH"),
            "text": source.get("text", "ERROR_ES_SEARCH"),
            "id": source.get("id", "ERROR_ES_SEARCH"),
            "url": source.get("url", "ERROR_ES_SEARCH")
        })
    return {"context": context, "results": results}

def main():

    df = pd.read_csv(input_csv_file_path)

    def process_row(row):
        print(f"Processing row {row.name + 1}")
        query = row['Utterance']
        context_results = parse_es_results(query, 3)
        context = context_results["context"]
        retrieval_results_list = context_results["results"]
        retrieval_docs = '\n'.join([f"[Document]\n{result['text']}[End]" for result in retrieval_results_list])
        summary = context["summary"]
        url_list = [result["url"] for result in retrieval_results_list]
        # classic_answer = watson_assistant_api(query) 
        genai_answer = generation_anwser(auth_watsonx(wx_apikey), query, retrieval_docs, summary)
        # return genai_answer, context["raw_generation"], '\n'.join(url_list), classic_answer
        return genai_answer, context["raw_generation"], '\n'.join(url_list)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_row = {executor.submit(process_row, row): row for index, row in df.iterrows()}
        for future in concurrent.futures.as_completed(future_to_row):
            row = future_to_row[future]
            try:
                # genai_answer, raw_generation, url_list, classic_answer = future.result()
                # df.at[row.name, 'classic_answer'] = classic_answer
                genai_answer, raw_generation, url_list = future.result()
                df.at[row.name, 'genai_answer'] = genai_answer
                df.at[row.name, 'rewriten_generation_raw'] = raw_generation
                df.at[row.name, 'es_url_list'] = url_list  
                # print(f"CLASSIC ANSWER:\n{classic_answer}\n------\nGENAI ANSWER:\n{genai_answer}")
                print(f"------Row {row.name + 1}------\nGENAI ANSWER:\n{genai_answer}")
            except Exception as e:
                print(f">>>>>>Row {row.name + 1}<<<<<<\nHad an exception: {e}")

    df.to_csv(output_csv_file_path, index=False)

if __name__ == "__main__":
    main()
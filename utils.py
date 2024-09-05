import csv,json
import sys
import re, string
import numpy as np
from connection import connect_wxai
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
import concurrent.futures as cf
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
from sentence_transformers import SentenceTransformer


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def save_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


# def get_url_length_reciprocal(url):
#     url_length =url.count('/')
#     url_length_rep = np.divide(1, url_length)
#     return url_length_rep


# def url2keywords(url):
#     url_text = url.split('.html')[0]
#     words = url_text.split("/")
#     def fil_ignore(w):
#         if w in ['en', 'app', 'detail', 'https:'] or "." in w or w.isdigit() or len(w)<2:
#             return False
#         else:
#             return True
#     filtered = [" ".join(w.split("-")) for w in words if fil_ignore(w)]
#     return ", ".join(filtered)



# def expand_query_with_synonyms(query):
#     words = query.split()
#     expanded_query = []

#     synonyms = [
#         # ["special consideration", "compassionate consideration", "Aegrotat"],
#         ["AELR","Academic English Language Requirement"],
#         ["DELNA","Diagnostic English Language Needs Assessment"],
#         ["SSO","Student Services Online"],
#         ["Shads","Shadows Bar"],
#         ["MBBS", "MBChB"],
#         ["GPA","Grade Point Average"],
#         ["GPE","Grade Point Equivalent"],
#         ["SRS", "summer research scholarship"],
#         ["ug","undergraduate"],
#         ["oweek", "orientation week"],
#         ["ats", "application to study"]
#     ]
#     translator = str.maketrans('', '', string.punctuation)
#     def w_in_r_list(w,r_l):
#         return any([w.translate(translator).lower() == r.lower() for r in r_l])


#     for word in words:
#         similar_words = [syn_set for syn_set in synonyms if w_in_r_list(word, syn_set)]
#         if similar_words:
#             similar_set = set(similar_words[0])
#             similar_set.discard(word)
#             if similar_set:
#                 expanded_query.append(f"{word} ({', '.join(similar_set)})")
#             else:
#                 expanded_query.append(word)
#         else:
#             expanded_query.append(word)

#     print(" ".join(expanded_query))
#     return " ".join(expanded_query)


# def clean_answers(input_text):
#     text = re.sub(r'[\n\t ]{2,}', '\n', input_text)
#     if 'src=' in text:
#         text = text.split('src=')[0]
#         print(text)
#     return text


# def csv_to_json(csv_file_path, json_file_path):
#     csv.field_size_limit(sys.maxsize)
#     with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         data = [row for row in csv_reader]

#     for entry in data:
#         if 'Answer' in entry:
#             entry['Answer'] = clean_answers(entry['Answer'])

#     with open(json_file_path, mode='w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, indent=4)

#     print(
#         f"CSV data has been successfully converted to JSON and saved to {json_file_path}.")

def part_json(file_path,output_folder_path):
    chuncked_data = load_json(file_path)
    print(len(chuncked_data))
    size = 5000
    chuncked_data_json_files = [chuncked_data[x:x + size] for x in
                                range(0, len(chuncked_data), size)]
    print(len(chuncked_data_json_files))
    i = 0
    for chuncked_data_json_file in chuncked_data_json_files:
        save_json(chuncked_data_json_file,
                  output_folder_path + '/part-' + str(i) + ".json")
        i = i + size

# def rewrite_query_with_wxai(user_query_list):
#     user_query = user_query_list[0]
#     id= user_query_list[1]
#     wxai_cred = connect_wxai()
#     project_id = "60b4758c-17c0-410b-b13a-ed28a776656d"
#     space_id =None
    

#     parameters = {
#         GenParams.DECODING_METHOD: "greedy",
#         GenParams.MAX_NEW_TOKENS: 20,
#         GenParams.MIN_NEW_TOKENS:0,
#         GenParams.STOP_SEQUENCES: ["**"],
#         GenParams.REPETITION_PENALTY:1
#     }
    
    
#     model = ModelInference(
#         model_id="meta-llama/llama-3-70b-instruct",
#         credentials=wxai_cred,
#         params=parameters,
#         project_id=project_id,
#         space_id=space_id,
#     )
#     prompt_txt =f"""Provide a better search query for a university enterprise search engine to answer the given question. Do not add new information. Do not remove any important information or university lingo from the question. If the given question is ambiguous, output a general search query. If the question is a good search query do not change it. End the query with ’**’.
#     Question: what is summer school
#     Search query:  what is summer school**
#     Question: campus card won't give me access to buildings
#     Search query: campus card won't give me access to buildings
#     Question: Hi when will my certificate arrive?
#     Search query: When will I receive my certificate If graduated in absentia**
#     Question: after 31st july can we apply
#     Search query: Application deadlines and dates?**
#     Question: Application queries
#     Search query: How to contact the university of Auckland?**
#     Question:Can I go there for studying ?
#     Search query: What are the entry requirements for studying in UoA?**
#     Question: how to change my timetable
#     Search query: How to change my course enrollment?**
#     Question: Help with my studies
#     Search query: How to get student support?**
#     Question: I need to replace a document I uploaded as part of my admission application
#     Search query:  I need to submit the documents required for my admission**
#     Question:{user_query}
#     Search query:"""
    
#     generated_response = model.generate(prompt=prompt_txt)

#     # print("Output from generate() method:")
#     # print(json.dumps(generated_response, indent=2))
#     answer = generated_response['results'][0]['generated_text']
#     return [answer, id]
    
    
# def rewrite_goldref_queries():
    
#     df_golden_set = pd.read_csv('./data/uoa-prod-benchmark-results_numbers.csv')

#     queries = df_golden_set[['query', 'id']]
#     search_results_list=[]
#     # try:
#     with ThreadPoolExecutor(max_workers=8) as executer:
#             format_bulk_ingest = {executer.submit(rewrite_query_with_wxai, [row['query'], row['id']]): row for index, row in queries.iterrows()}
                
#             for format_future in cf.as_completed(format_bulk_ingest):
#                 response =format_future.result()
#                 print(response)
#                 result_dict={"id":response[1],
#                              "rewrite_query":response[0].replace('?**','').lstrip()
#                              }
#                 search_results_list.append(result_dict)
                
#     pd_rewritten_queries = pd.DataFrame(search_results_list)
#     pd_output = df_golden_set.merge(pd_rewritten_queries, on=['id'])
#     pd_output.to_csv('./data/uoa-prod-benchmark-results_numbers_rewritten_query.csv')
# # except Exception as e:
# #     print(e)
# #     dfoutput = pd.DataFrame(search_results_list)
# #     dfoutput.to_csv(output_file_name, index=False)

# def get_dense_encoding(query):
#     model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
#     embeddings = model.encode(query)
#     # print(embeddings)
#     return embeddings

def clean_text(text):

    # Remove \r
    text = re.sub(r'[\r]', ' ', text)
    # Remove any Unicode characters
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    # Remove specific Unicode sequence \u00e2\u20ac\u00a2
    pattern_to_remove = r'\\u00e2\\u20ac\\u00a2'
    # Remove the escaped Unicode string using regex
    text = re.sub(pattern_to_remove, '', text)
    # Optionally, remove any additional unwanted sequences
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with a single space
    return text
    
# def remove_chars(file_name):
#     data = load_json(file_name)
#     print(clean_text(data[0]['web_text']))

if __name__ == "__main__":
    part_json('../legal_chunked.json','../legal_chunks')
    

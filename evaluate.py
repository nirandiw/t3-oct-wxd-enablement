import numpy as np
from connection import connect_wxd
import pandas as pd
import concurrent.futures as cf
from concurrent.futures import ThreadPoolExecutor
from queries import *

es_client=connect_wxd()

def wxd_search(q_input):
    query = q_input[0]
    print("Query: ",query)
    golden_url = q_input[1]
    id=q_input[2]
    indeces = ['ibm-ce-aili-hybrid-nw']
    response = es_client.search(
        index=indeces,
        size=5,
        query=get_query(query),
        # knn=get_knn(query),
        # rank= get_rank(),
    )
    # print(response)
    return [query, golden_url, response, id]

 
ref_set = pd.read_excel('../pb-13x3-qas.xlsx')
ref_set['ID'] = ref_set.index
queries = ref_set[['Question', 'ID', 'Document ID']]

print(queries['ID'])
search_results_list = []
max_top_hits = 5
output_file_name="../evaluation-sparse-top"+str(max_top_hits)+"-v1.csv" 
true_count=0

try:
    with ThreadPoolExecutor(max_workers=8) as executer:
            format_bulk_ingest = {executer.submit(wxd_search, [row["Question"], row['Document ID'], row['ID']]): row for index, row in queries.iterrows()}
                
            for format_future in cf.as_completed(format_bulk_ingest):
                response =format_future.result()
                # print(response)
                top_hits_urls=[]
                top_hits=[]
                for hit in response[2]["hits"]["hits"]:
                
                    if hit["_source"]["document_id"] not in top_hits_urls:
                        top_hits.append({"hit_doc_id":hit["_source"]["document_id"], "hit_score":hit["_score"]})
                is_match = True if response[1] in [hit['hit_doc_id'] for hit in top_hits[:max_top_hits]] else False
                true_count += 1 if is_match else 0
                # Create the dictionary with the required values
                result_dict = {
                    "id":response[3],
                    "query": response[0],
                    "golden_document_id": response[1],
                    "is_match": is_match,
                    "top_hit_elser_1_url": top_hits[0]["hit_doc_id"],
                    "top_hit_elser_1_score": top_hits[0]["hit_score"],
                    "top_hit_elser_2_url": top_hits[1]["hit_doc_id"],
                    "top_hit_elser_2_score": top_hits[1]["hit_score"],
                    "top_hit_elser_3_url": top_hits[2]["hit_doc_id"],
                    "top_hit_elser_3_score": top_hits[2]["hit_score"],
                    "top_hit_elser_4_url": top_hits[3]["hit_doc_id"],
                    "top_hit_elser_4_score": top_hits[3]["hit_score"],
                    "top_hit_elser_5_url": top_hits[4]["hit_doc_id"],
                    "top_hit_elser_5_score": top_hits[4]["hit_score"],
                }
                search_results_list.append(result_dict)
except Exception as e:
    print(e)
    dfoutput = pd.DataFrame(search_results_list)
    dfoutput.to_csv(output_file_name, index=False)
            
dfoutput = pd.DataFrame(search_results_list)
dfoutput.to_csv(output_file_name, index=False)
print(output_file_name, ':', np.divide(true_count, 39.0))




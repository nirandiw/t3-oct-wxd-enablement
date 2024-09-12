import time
from connection import connect_wxd
from queries import get_knn, get_query, get_rank


def wxd_search(q_input):
    es_client = q_input[3] 
    query = q_input[0]
    print("Query: ",query)
    golden_url = q_input[1] 
    id=q_input[2]
    indeces = ['aili-hybrid-bge']
    response = es_client.search(
        index=indeces,
        size=10,
        query=get_query(query),
        knn=get_knn(query),
        rank= get_rank(),
    )
    return [query, golden_url, response, id]

def wxd_search_basic(client, query, index):
    response = client.search(
        index=index,
        size=30,
        query=get_query(query),
        knn=get_knn(query),
        rank=get_rank(),
    )
    return response

if __name__ == "__main__":
    client = connect_wxd()
    index_names = ["aili-hybrid-bge"]
    user_query = "in Australia, under section 160WA, how should a liquidator notify the relevant shareholders?"
    start_t = time.time()

    response = wxd_search_basic(client,user_query, index_names )

    print("== Search took: ", time.time() - start_t, " seconds ==")
    for i, hit in enumerate(response["hits"]["hits"]):
        # print(hit)
        doc_id = hit["_id"]
        score = hit["_score"]
        # url = hit["_source"]["url"]
        web_text = hit["_source"]["web_text"]
        # heading = hit["_source"]["heading"]
        print(f"----- rank {i} ------")
        print(f"Id: {doc_id}\n")
        # print(f"Score: {score}\nURL: {url}\n")
        # print(f"Heading: {heading}")
        print(f"Web Text: {web_text}")

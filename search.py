import time
from connection import connect_wxd
from queries import get_knn, get_query, get_rank
client = connect_wxd()

def wxd_search(q_input):
    es_client = q_input[3]
    query = q_input[0]
    print("Query: ",query)
    golden_url = q_input[1]
    id=q_input[2]
    indeces = ['aili-hybrid-bge']#['ibm-ce-aili-hybrid-nw']
    response = es_client.search(
        index=indeces,
        size=5,
        query=get_query(query),
        knn=get_knn(query),
        rank= get_rank(),
    )
    # print(response)
    return [query, golden_url, response, id]

if __name__ == "__main__":

    index_names = ['aili-hybrid-emb3-local']
    user_query = "in Australia, under section 160WA, how should a liquidator notify the relevant shareholders?"
    start_t = time.time()

    response = client.search(
        index=index_names,
        size=30,
        # query=get_query(user_query),
        knn=get_knn(user_query),
        # rank=get_rank(),
    )


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

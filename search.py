import time
from connection import connect_wxd
from utils import expand_query_with_synonyms
from queries import get_knn, get_query, get_rank
client = connect_wxd()



# index_names = ["sherry-scholarships","sherry-askauckland", "sherry-main", "sherry-courseoutlines", "sherry-studyoptions"]
index_names = ['uoa-student-boosted']
# index_names = ['test_elser_index_5']

# index_names = ["x86-staff-kb"]
# index_names = "sherry-complete-hybrid"

user_query = "How to apply for a programme"
start_t = time.time()

response = client.search(
    index=index_names,
    size=30,
    query=get_query(user_query),
    # knn=get_knn(user_query),
    # rank=get_rank()
    collapse= {"field": "url.keyword"}

)


print("== Search took: ", time.time() - start_t, " seconds ==")
for i, hit in enumerate(response["hits"]["hits"]):
    # print(hit)
    doc_id = hit["_id"]
    score = hit["_score"]
    url = hit["_source"]["url"]
    web_text = hit["_source"]["text"]
    heading = hit["_source"]["heading"]
    print(f"----- rank {i} ------")
    print(f"Score: {score}\nURL: {url}\n")
    print(f"Heading: {heading}")
    print(f"Web Text: {web_text}")

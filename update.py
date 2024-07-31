from connection import connect_wxd
from elasticsearch import helpers
import pprint

client = connect_wxd()
# resp = client.update(
#     index="x86-askauckland-hybrid",
#     id="Z4WxqI8BKTZon0ebR50p",
#     body={"script": "ctx._source.scope = 'askauckland'"},
# )
# print(resp)

# resp = client.indices.put_mapping(
#     index="uoa-student-with-title",
#     body={
#         "properties":
#               {
#                   "heading_embedding": {"type": "sparse_vector"}
#               }
#           },
# )
# print(resp)
#
# resp = client.ingest.put_pipeline(
#     id="add-heading-elser",
#     body={
#         "description": "add elser for heading fields",
#         "processors": [
#             {
#                 "inference": {
#                     "model_id": ".elser_model_2",
#                     "input_output": [
#                         {"input_field": "heading",
#                          "output_field": "heading_embedding"}
#                     ],
#                 }
#             }
#         ],
#     },
# )
# print(resp)

# resp = client.update_by_query(
#     index="x86-askauckland-hybrid",
#     pipeline="set-scope",
# )

q = {
     "script": {
        "source": "ctx._source.pagerank=100",
        "lang": "painless"
     },
   #   "query": {
   #      "match": {
   #          "id": "input1184_1"
   #      }
   #   }
}
# resp = client.update_by_query(
#     index="my-index-000001",
#     conflicts="proceed",
#     body={"query": {"term": {"user.id": "kimchy"}}},
# )
# print(resp)

# client.update_by_query(body=q, index='student-pagerank-hybrid',conflicts="proceed", _id="input1184_1")



client.update(
   index='student-pagerank-hybrid-update',
   id='input406_0',
   body={
      "script": {
        "source": "ctx._source.pagerank=100",
        "lang": "painless"
     }
   }
)

# print(resp)

# resp = client.indices.get_settings(index="test_elser_index_5")
#
# print.pprint(resp.body)
# #
# resp = client.indices.get_mapping(index="uoa-student-with-title-emb")

# pprint.pprint(resp.body)

# # resp = client.synonyms.get_synonym(id = 'synonym_test')
# # pprint.pprint(resp.body)
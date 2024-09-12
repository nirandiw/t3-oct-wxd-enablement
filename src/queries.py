def get_query(query, model=".elser_model_2"):
    

    # QUERY_BASIC_ELSER={
    #         "text_expansion": {
    #         "web_text_embedding":{
    #                 "model_id": model,
    #                 "model_text": query,
    #             }
    #         },
    #     }
    
    QUERY_BM25_ELSER = {
    "bool": { 
      "should": [
        {
          "text_expansion": {
            "web_text_embedding":{
              "model_text": query,
              "model_id": ".elser_model_2"
            }
          }
        },
        {
            "match":{
                "text":{"query":query,
                         }
            }
        }
      ]
    }
    }
    
    # QUERY_BM25 = {
    #     "match":{
    #             "web_text":{"query":query,
    #                     #  "boost":1.5
    #                      }
    #         }
    # }
    
    return QUERY_BM25_ELSER

def get_all():
    QUERY_MATCH_ALL ={
        "match_all" : {} 
    }
    return QUERY_MATCH_ALL

def doc_exists(id):
    QUERY_DOC_CHECK ={
        "match" : {"id":id} 
    }
    return QUERY_DOC_CHECK

def get_knn(query):

    KNN_BGE={
        #"field":"web_text_dense",
        "field":"web_text_sentence_bge_embedding",
        "query_vector_builder": {
        "text_embedding": {
            "model_id": "baai__bge-large-en-v1.5",
            "model_text": query,
        }
    },
    "k": 10,
    "num_candidates": 100
    }
    
    KNN_MINILM={
        #"field":"web_text_dense",
        "field":"web_text_sentence_minllm_embedding",
        "query_vector_builder": {
        "text_embedding": {
            "model_id": "sentence-transformers__all-minilm-l12-v2",
            "model_text": query,
        }
    },
    "k": 10,
    "num_candidates": 50
    }
    
    
    return KNN_BGE

def get_rank():
    RANK_BASIC={"rrf": { "window_size": 30,
            "rank_constant": 20}}
    return RANK_BASIC


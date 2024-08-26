def get_query(query, model=".elser_model_2"):
    
    elser_embedding = "web_text_sparse_embedding"#

    QUERY_BASIC_ELSER={
            "text_expansion": {
                elser_embedding: {
                    "model_id": model,
                    "model_text": query,
                }
            },
        }
    
    QUERY_BM25_ELSER = {
    "bool": { 
      "should": [
        {
          "text_expansion": {
            "web_text_sparse_embedding": {
              "model_text": query,
              "model_id": ".elser_model_2"
            }
          }
        },
        {
        #   "query_string": {
        #     "query": query,
        #     "default_field": "web_text"
        #   }
            "match":{
                "text":{"query":query,
                        #  "boost":1.5
                         }
            }
        }
      ]
    }
    }
    
    QUERY_BM25 = {
        "match":{
                "web_text":{"query":query,
                        #  "boost":1.5
                         }
            }
    }
    
    return QUERY_BM25_ELSER


def get_knn(query):

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
    return KNN_MINILM

def get_rank():
    RANK_BASIC={"rrf": { "window_size": 30,
            "rank_constant": 20}}
    return RANK_BASIC




    
if __name__ == "__main__":

    rewrite_query_with_wxai("I want contact UoA")

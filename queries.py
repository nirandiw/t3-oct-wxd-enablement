from utils import get_dense_encoding
def get_query(query, model=".elser_model_2"):
    
    # elser_embedding = "web_text_embedding" 
    elser_embedding = "web_text_elser_embedding"#
    dense_embedding = "web_text_sentence_embedding"

    QUERY_TITLE_BOOST =  {
    "boosting":{
        "positive":{
            "bool":{
                "must":[{
                    "text_expansion": {
                        "web_text_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": query,
                        }
                    }
                }],
                 "should":[{
                        "bool":{
                            "must":[{
                                "multi_match": {
                                    "query": query,
                                    "fields": ["heading"],
                                    }
                            }],
                            "boost":1.5
                        }
                    }],
            #     "must": [{
            #         "match": {
            #             "text": query
            #         }
            #         }],
            # "should": [
            #     {
            #     "match": {
            #         "heading": query
            #     }
            #     }
            # ],
            # "minimum_should_match": 0 
                
            }
            
            
            },
        "negative":{
            "regexp": {
                        "url": {
                        "value": ".*\\.custhelp.*"
                        }
                    }
            },
        "negative_boost":0.9
    },
}
    
    
    
    QUERY_AA_NEG_CONTACT_US_GENERAL_POSTIVE_BOOST ={
        
    }

    QUERY_AA_NEGATIVE_CONTACT_US_POSTIVE_BOOST = {
        
        "boosting":{
            "positive":{
                "bool":{
                    "must":[{
                        
                        "text_expansion": {
                            "web_text_embedding": {
                                "model_id": ".elser_model_2",
                                "model_text": query,
                            }
                        }
                    }],
                    "should":[{
                        "bool":{
                            "must":[{
                                "regexp": {
                                    "url": {
                                    "value": ".*\\.contact-us*"
                                    }
                                }
                            }],
                            "boost":2
                        }
                    }],
                    "minimum_should_match": 1
        }
                },
            "negative":{
                "regexp": {
                            "url": {
                            "value": ".*\\.custhelp.*"
                            }
                        }
                },
            "negative_boost":0.9
        }
    }
    
    QUERY_AA_NEGATIVE_BOOST= {
        "boosting":{
            "positive":{
                "text_expansion": {
                    "web_text_embedding": {
                        "model_id": ".elser_model_2",
                        "model_text": query,
                    }
                }
                },
            "negative":{
                "regexp": {
                            "url": {
                            "value": ".*\\.custhelp.*"
                            }
                        }
                },
            "negative_boost":0.9 #TODO we  need to see if this number  an be improved
        }
        
    }
    
    QUERY_NO_AA_BOOST = {
        "bool":{
            "must":[{
                
                "text_expansion": {
                    elser_embedding: {
                        "model_id": ".elser_model_2",
                        "model_text": query,
                    }
                }
            }],
            "should":[{
                "bool":{
                    "must_not":[{
                        "regexp": {
                            "url": {
                            "value": ".*\\.custhelp.*"
                            }
                        }
                    }],
                    "boost":2
                }
            }],
            "minimum_should_match": 1
        }
        
    }

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
            "web_text_embedding": {
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
                "title":{"query":query,
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
    
    
    QUERY_AA_NEGATIVE_CONTACT_US_POSTIVE_BOOST_TITE_BM25_MATCH = {
        "boosting":{
            "positive":{
                "bool":{
                    "must":[{
                        "text_expansion": {
                            elser_embedding: {
                                "model_id": ".elser_model_2",
                                "model_text": query,
                            }
                        }
                    }],
                    "should":[{
                        "bool":{
                            "must":[{
                                "regexp": {
                                    "url": {
                                    "value": ".*\\.contact-us*"
                                    }
                                },
                            }],
                            "boost":2
                        },
                       
                    },{
                          "match":{
                                "heading":{"query":query,
                                #   "boost":5
                                    }
                                }
                    }],
                }
                },
            "negative":{
                "regexp": {
                            "url": {
                            "value": ".*\\.custhelp.*"
                            }
                        }
                },
            "negative_boost":0.9
        }
    }
    
    QUERY_PAGERANK = {
    "bool": {
      "should": [
          {"match":{
                "url":{"query":query,
                    "boost":1.5
                    }
                }
           },
          {
          "text_expansion": {
            "web_text_elser_embedding": {
              "model_id": ".elser_model_2",
              "model_text": query
            }
          }
        },
        {
          "rank_feature": {
            "field": "url_length",
            "boost": 5
          }
        }
      ]
    }
    }
    
    QUERY_TITLE_EMBEDDING={
    "boosting": {
        "positive": {
            "bool": {
                "should": [{
                    "text_expansion": {
                        "web_text_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": query,
                            "boost": 1,
                        }
                    }
                },
                    {
                        "text_expansion": {
                            "heading_embedding": {
                                "model_id": ".elser_model_2",
                                "model_text": query,
                                "boost": 1.5,
                            }
                        }
                    },
                    {
          "rank_feature": {
            "field": "url_length",
            "boost": 2,
            # "linear":{}
          }  
        },
                    {"rank_feature": {
            "field": "pagerank",
            "boost": 10
          }}
                ]
            }
        },
        "negative": {
            "regexp": {
                "url": {
                    "value": ".*\\.custhelp.*|.*\\.calendar.auckland.ac.nz.*|.*\\.courseoutline.*"
                }
            }
        },
        "negative_boost": 0.5
    },
}
    
    QUERY_PAGERANK_WITH_BOOSTING = {
    "boosting": {
        "positive": {
            "bool": {
                "should": [{
                    "text_expansion": {
                        "web_text_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": query,
                            "boost": 1,
                        }
                    }
                },
                {
                    "text_expansion": {
                        "heading_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": query,
                            "boost": 1.5,
                        }
                    }
                },
                {
                    "regexp": {
                        "url": {
                            "value": ".*\\www.auckland.ac.nz*",
                            "boost": 5,
                        }
                    }
                },
                {
                    "rank_feature": {
                        "field": "pagerank",
                        "boost": 10
                    }
                },
                ]
            }
        },
        "negative": {
            "bool":{
                "should":[
                    {
                        "regexp": {
                            "url": {
                                "value": ".*\\.custhelp.*"
                            }
                        }
                    },
                    # {
                    #     "rank_feature": {
                    #         "field": "url_length",
                    #         "boost": 500,
                    #         "saturation": {"pivot": 6}
                    #     }
                    # },
            ]
            }
        },
        "negative_boost": 0.5
    },
}
    
    QUERY_KNN_COLLAPSE = {
    "boosting": {
        "positive": {
            "bool": {
                "should": [{
                    "text_expansion": {
                        "web_text_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": query,
                            "boost": 1,
                        }
                    }
                },
                {
                    "text_expansion": {
                        "heading_embedding": {
                            "model_id": ".elser_model_2",
                            "model_text": query,
                            "boost": 1.5,
                        }
                    }
                },
                {
                    "regexp": {
                        "url": {
                            "value": ".*\\www.auckland.ac.nz*",
                            "boost": 5,
                        }
                    }
                },
                {
                    "rank_feature": {
                        "field": "pagerank",
                        "boost": 10
                    }
                },
                {
                     "knn": {
            "field": dense_embedding,
            "query_vector": get_dense_encoding(query),
            "num_candidates": 10,
            "boost": 2
                }
                }
                
                ]
            }
        },
        "negative": {
            "bool":{
                "should":[
                    {
                        "regexp": {
                            "url": {
                                "value": ".*\\.custhelp.*"
                            }
                        }
                    },
                    # {
                    #     "rank_feature": {
                    #         "field": "url_length",
                    #         "boost": 500,
                    #         "saturation": {"pivot": 6}
                    #     }
                    # },
            ]
            }
        },
        "negative_boost": 0.5
    },
}

    
    return QUERY_PAGERANK_WITH_BOOSTING


def get_knn(query):
    # dense_embedding = "web_text_dense" 
    dense_embedding = "web_text_sentence_embedding"

    KNN_BASIC={
        #"field":"web_text_dense",
        "field":dense_embedding,
        "query_vector_builder": {
        "text_embedding": {
            "model_id": "sentence-transformers__all-minilm-l12-v2",
            "model_text": query,
        }
    },
    "k": 10,
    "num_candidates": 50
    }
    return KNN_BASIC

def get_rank():
    RANK_BASIC={"rrf": { "window_size": 30,
            "rank_constant": 20}}
    return RANK_BASIC




    
if __name__ == "__main__":

    rewrite_query_with_wxai("I want contact UoA")

import os, time
from elasticsearch import helpers
from connection import connect_wxd
from utils import load_json
import os
from queries import doc_exists

def create_hybrid_pipeline(ingest_pipeline_id, client):
    #TODO if pipeline exists return with message
    # client.ingest.delete_pipeline(id=ingest_pipeline_id)
    client.ingest.put_pipeline(
        id=ingest_pipeline_id,
        description="Ingest pipeline for Elser encoding and dense encoding",
        processors=[
            {
                "inference": {
                    "model_id": ".elser_model_2",
                    "input_output": 
                        {"input_field": "web_text",
                         "output_field": "web_text_embedding"}
                    
                },
            },
            # {
            #     "inference": {
            #         "model_id": "sentence-transformers__all-minilm-l12-v2",
            #         "input_output": {
            #             "input_field": "web_text",
            #             "output_field": "web_text_sentence_embedding",
            #         },
            #     }
            # },
            {
                "inference": {
                    "model_id": "baai__bge-large-en-v1.5",
                    "input_output": {
                        "input_field": "web_text",
                        "output_field": "web_text_sentence_bge_embedding",
                    },
                }
            },
        ],
    )


def create_hybrid_index(index_name, client):
    if client.indices.exists(index=index_name):
        print("Index exists!!! Index is NOT created. Using the existing index ", index_name)
        return
    # Create a new index
    # client.indices.delete(index=index_name, ignore_unavailable=True)
    client.indices.create(
        index=index_name,
        mappings={
            "properties": {
                "web_text": {"type": "text"},
                "web_text_embedding": {"type": "sparse_vector"},
                # "web_text_sentence_embedding": {
                #     "type": "dense_vector",
                #     "dims": 384,
                #     "similarity": "cosine",
                # },
                 "web_text_sentence_bge_embedding": {
                    "type": "dense_vector",
                    "dims": 1024,
                    "similarity": "cosine",
                },
            }
        },
    )


def ingest_parallel_bulk(client, documents_gen, chunk_size):
    start_ingest_t = time.time()
    for success, info in helpers.parallel_bulk(client, documents_gen,
                                               thread_count=8,
                                               chunk_size=chunk_size,
                                               request_timeout=5000):
        if not success:
            print('A document failed:', info)

    print(f"Ingestion completed: {time.time() - start_ingest_t}s")


def gen_processed(f, index_name, ingest_pipeline_id):
    docs = load_json(f)
    print(len(docs), "documents loaded in", f)
    for d in docs:
        print(d['id'])
        yield {
            "_index": index_name,
            "_id": d["id"],
            'pipeline': ingest_pipeline_id,
            "_source": d
        }

    
if __name__ == "__main__":

    client = connect_wxd()
    index_name = "aili-hybrid-bge"
    ingest_pipeline_id = "aili-ingest-pipeline-hybrid-bge"

    create_hybrid_pipeline(ingest_pipeline_id, client)
    
    create_hybrid_index(index_name, client)
    
    chunks_folder = '../data/chunks'
    file_names = os.listdir(chunks_folder)

    t_start_all = time.time()
    for file_name in file_names:
        # print(file_name)
        # if file_name in ['part-75000.json']:
        chunks_gen = gen_processed(chunks_folder+'/'+file_name,
                                index_name,
                                ingest_pipeline_id)
        ingest_parallel_bulk(client, chunks_gen, chunk_size=200)

    print(f"Total Ingestion time: {time.time() - t_start_all}" )
    



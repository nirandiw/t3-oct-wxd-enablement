import os, time
from elasticsearch import helpers
from connection import connect_wxd
from utils import load_json, save_json

elser_model_name = ".elser_model_2"


def create_hybrid_pipeline(ingest_pipeline_id, client):
    # client.ingest.delete_pipeline(ingest_pipeline_id)
    client.ingest.put_pipeline(
        id=ingest_pipeline_id,
        description="Ingest pipeline for Elser encoding and dense encoding",
        processors=[
            {
                "inference": {
                    "model_id": elser_model_name,
                    "input_output": [
                        {"input_field": "web_text",
                         "output_field": "web_text_embedding"}
                    ],
                },
            },
            {
                "inference": {
                    "model_id": "sentence-transformers__all-minilm-l12-v2",
                    "input_output": {
                        "input_field": "web_text",
                        "output_field": "web_text_sentence_embedding",
                    },
                }
            },
            # {
            #     "inference": {
            #         "model_id": elser_model_name,
            #         "input_output": {
            #             "input_field": "heading",
            #             "output_field": "heading_embedding",
            #         },
            #     }
            # }
        ],
    )


def create_hybrid_index(index_name, ingest_pipeline_id, client):
    # Create a new index
    client.indices.delete(index=index_name, ignore_unavailable=True)
    client.indices.create(
        index=index_name,
        # settings={"index": {"default_pipeline": ingest_pipeline_id}},
        mappings={
            "properties": {
                "web_text": {"type": "text"},
                "web_text_embedding": {"type": "sparse_vector"},
                # "heading_embedding": {"type": "sparse_vector"},
                "web_text_sentence_embedding": {
                    "type": "dense_vector",
                    "dims": 384,
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
    # f = "data/student_chunked.json"
    docs = load_json(f)
    print(len(docs), "documents loaded")
    for d in docs:
        yield {
            "_index": index_name,
            "_id": d["id"],
            'pipeline': ingest_pipeline_id,
            "_source": d
        }


if __name__ == "__main__":

    client = connect_wxd()
    index_name = "ibm-ce-aili-hybrid"
    ingest_pipeline_id = "ibm-ce-ingest-pipeline-hybrid-v1"

    create_hybrid_pipeline(ingest_pipeline_id, client)
    #
    # create_elser_pipeline(ingest_pipeline_id, client)
    # if not client.indices.exists(index=index_name):
    create_hybrid_index(index_name, ingest_pipeline_id, client)


    t_start_all = time.time()


    # parts_folder = '../student_chunked_pagerank_parts/'
    # wd_jsons = os.listdir(parts_folder)
    # wd_jsons = sorted(wd_jsons)
    # print(wd_jsons)
    # print(f"ingesting {wd_jsons}")

    # for f in wd_jsons[:1]:
        # print(f)
    chunks_gen = gen_processed("../legal_chunked.json",
                            index_name,
                            ingest_pipeline_id)
    ingest_parallel_bulk(client, chunks_gen, chunk_size=200)


    # for d in d_paths:
    #     d_start = time.time()
    #     chunks_gen = gen_chunks(d, index_name, ingest_pipeline_id)
    #     ingest_parallel_bulk(client, chunks_gen, chunk_size=50)
    #     print(f"Ingestion time for {d}: {time.time() - d_start}" )
    # ingest_parallel_bulk(client, chunks, chunk_size=50)
    print(f"Total Ingestion time: {time.time() - t_start_all}" )



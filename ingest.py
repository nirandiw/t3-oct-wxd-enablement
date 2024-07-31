import os, time
from elasticsearch import helpers
from connection import connect_wxd
from utils import load_json, save_json
from chunk import gen_processed

elser_model_name = ".elser_model_2"
# elser_model_name = ".elser_model_2_linux-x86_64"

def create_elser_pipeline(ingest_pipeline_id, client):
    # client.delete_pipeline(ingest_pipeline_id)
    client.ingest.put_pipeline(
        id=ingest_pipeline_id,
        description="Ingest pipeline for ELSER",
        processors=[
            {
                "inference": {
                    "model_id": elser_model_name,
                    "input_output": [
                        {"input_field": "web_text",
                         "output_field": "web_text_embedding"}
                    ],
                }
            }
        ],
    )


def create_index(index_name, ingest_pipeline_id, client):
    # Create a new index
    client.indices.delete(index=index_name, ignore_unavailable=True)
    client.indices.create(
        index=index_name,
        settings={"index": {"default_pipeline": ingest_pipeline_id}},
        mappings={
            "properties": {
                "web_text": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "web_text_embedding": {"type": "sparse_vector"},
            }
        },
    )


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
            {
                "inference": {
                    "model_id": elser_model_name,
                    "input_output": {
                        "input_field": "heading",
                        "output_field": "heading_embedding",
                    },
                }
            }
        ],
    )


def create_hybrd_index(index_name, ingest_pipeline_id, client):
    # Create a new index
    client.indices.delete(index=index_name, ignore_unavailable=True)
    client.indices.create(
        index=index_name,
        # settings={"index": {"default_pipeline": ingest_pipeline_id}},
        mappings={
            "properties": {
                "web_text": {"type": "text"},
                "web_text_embedding": {"type": "sparse_vector"},
                "heading_embedding": {"type": "sparse_vector"},
                "web_text_sentence_embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "similarity": "cosine",
                },
                # pagerank only
                "pagerank": {
                    "type": "rank_feature"
                },
                "url_length": {
                    "type": "rank_feature",
                    "positive_score_impact": False
                }
            }
        },
    )


def load_documents(filename, index_name, ingest_pipeline_id, save_copy = True):
    # Load documents into an array
    docs = load_json(filename)
    documents = []
    for i, s in enumerate(docs):
        if "text" not in s.keys():
            continue
        t = s["title"][0] + " " + s["text"][0]
        url = s["url"]
        documents.append(
            {
                "_index": index_name,
                'pipeline': ingest_pipeline_id,
                "_source": {"id": i, "web_text": t, "url": url},
            }
        )
    print(f"{len(documents)} documents loaded!")
    if save_copy:
        save_json(documents, "data/documents.json")
    return documents


def gen_docs(filename, index_name, ingest_pipeline_id):
    docs = load_json(filename)
    print(f"{len(docs)} documents loaded!")
    for i, s in enumerate(docs):
        if "text" not in s.keys():
            continue
        t = s["title"][0] + " " + s["text"][0]
        url = s["url"]
        doc = {
            "_index": index_name,
            'pipeline': ingest_pipeline_id,
            "_source": {"id": i, "web_text": t, "url": url}
        }
        yield doc


def ingest_parallel_bulk(client, documents_gen, chunk_size):
    start_ingest_t = time.time()
    for success, info in helpers.parallel_bulk(client, documents_gen,
                                               thread_count=8,
                                               chunk_size=chunk_size,
                                               request_timeout=5000):
        if not success:
            print('A document failed:', info)

    print(f"Ingestion completed: {time.time() - start_ingest_t}s")


if __name__ == "__main__":

    client = connect_wxd()
    index_name = "student-pagerank-hybrid-update"
    ingest_pipeline_id = "ingest-pipeline-pagerank-hybrid-v2"

    # create_hybrid_pipeline(ingest_pipeline_id, client)
    #
    # create_elser_pipeline(ingest_pipeline_id, client)
    # if not client.indices.exists(index=index_name):
    create_hybrd_index(index_name, ingest_pipeline_id, client)

    # document_path = "data/askauckland.json"
    # d_paths = ["data/askauckland.json",
    #            "data/courseoutlines.json",
    #            "data/main.json",
    #            "data/scholarships.json",
    #            "data/studyoptions.json"]
    # documents_gen = gen_docs(document_path,index_name,ingest_pipeline_id)
    t_start_all = time.time()
    # chunks = gen_processed('data/staff_STC_chunked.json',
    #                        index_name, ingest_pipeline_id)
    # ingest_parallel_bulk(client, chunks, chunk_size=100)

    parts_folder = 'data/student_chunked_pagerank_parts/'
    wd_jsons = os.listdir(parts_folder)
    wd_jsons = sorted(wd_jsons)
    print(wd_jsons)
    print(f"ingesting {wd_jsons}")

    for f in wd_jsons[:1]:
        print(f)
        chunks_gen = gen_processed(parts_folder+f,
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



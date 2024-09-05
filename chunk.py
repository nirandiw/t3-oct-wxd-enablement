import json
from utils import load_json, clean_text
from llama_index.core.node_parser import SentenceSplitter


def gen_chunk_js():
    d_paths = ["../ibm_pr_clean.json"]

    text_parser = SentenceSplitter(
        chunk_size=200,
        chunk_overlap=10,
    )
    print(d_paths)
    for d in d_paths:
        docs = load_json(d)
        print(len(docs)) #TODO add the document we deleted
        for doc in docs:
            doc_id= doc['id']
            doc_text = doc['output']
            doc_heading = "" #TODO extract the title
            text_chunks = text_parser.split_text(doc_text)
            for i_c, chunk in enumerate(text_chunks):
                doc = {
                    "id": doc_id + "_" + str(i_c),
                    "document_id": doc_id,
                    "web_text": doc_heading + "\n" + clean_text(chunk),
                    "text": clean_text(chunk),
                    "heading": doc_heading
                }
                yield doc
            


def write_chunks_to_file(gen, output_name):
   
    with open(output_name, 'w') as f:
        json_objects = [json.dumps(obj) for obj in gen]
        f.write("[\n" + ",\n".join(json_objects) + "\n]")



if __name__ == "__main__":
    # chunks = gen_chunks_staff()
    chunks = gen_chunk_js()
    write_chunks_to_file(chunks, "../legal_chunked_clean.json")
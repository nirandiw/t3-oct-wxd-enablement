import json
from utils import load_json, get_url_length_reciprocal, url2keywords
from llama_index.core.node_parser import SentenceSplitter


def get_scope(str_input):
    if "https://www.auckland.ac.nz/en/news/" in str_input:
        return "News"
    else:
        return "Not Defined"


def gen_chunk_js():
    d_paths = ["data/input/askauckland.json",
               "data/input/courseoutlines.json",
               "data/input/main.json",
               "data/input/scholarships.json",
               "data/input/studyoptions.json"
               ]

    text_parser = SentenceSplitter(
        chunk_size=200,
        chunk_overlap=10,
    )
    page_rank_docs = load_json('data/pageranks_multipled.json')

    for d in d_paths:
        docs = load_json(d)
        idf = d.split("/")[1].split(".")[0]
        for i, s in enumerate(docs):
            if "text" not in s.keys():
                continue
            if "description" not in s.keys():
                s["description"] = " "
            url = s["url"]
            pagerank = page_rank_docs[url]
            heading = s["title"][0]
            if heading is None or url2keywords(url) is None:
                print("heading: ", heading, url2keywords(url))
            for t in s["text"]:
                text_chunks = text_parser.split_text(t)
                for i_c, chunk in enumerate(text_chunks):
                    doc = {
                        "id": idf + str(i) + "_" + str(i_c),
                        "document_id": idf + str(i),
                        "web_text": heading + "\n" + chunk,
                        "text": chunk,
                        "heading": heading + ", "+ url2keywords(url),
                        "url": url,
                        "description": s["description"],
                        "collection_id": s["result_metadata"]["collection_id"],
                        "url_length": get_url_length_reciprocal(url),
                        "pagerank": pagerank
                    }
                    yield doc


def gen_chunks_staff():
    d_paths = ["data/Staff KB Answers - Published Public.json"]

    text_parser = SentenceSplitter(
        chunk_size=200,
        chunk_overlap=10,
        # separator=" ",
    )

    for d in d_paths:
        docs = load_json(d)
        for i, s in enumerate(docs):
            title = s["Summary"]
            answer = s["Answer"]
            id = s["Answer ID  "]
            if s["Assigned Group"] == "Shared Transaction Centre (STC)":
                print(s["Assigned Group"])
                text_chunks = text_parser.split_text(answer)
                for i_c, chunk in enumerate(text_chunks):
                    doc = {
                        "id": title + "_" + str(i_c),
                        "web_text": title + "\n" + chunk,
                        "text": chunk,
                        "heading": title,
                        "assigned_group": s["Assigned Group"],
                        "url": "https://superuoa.custhelp.com/app/answers/detail/a_id/" + id,
                    }
                    yield doc


def gen_chunks(filename, index_name, ingest_pipeline_id):
    docs = load_json(filename)
    idf = filename.split("/")[1].split(".")[0]

    text_parser = SentenceSplitter(
        chunk_size=200,
        chunk_overlap=10,
        # separator=" ",
    )

    for i, s in enumerate(docs):
        if "text" not in s.keys():
            continue
        url = s["url"]
        for t in s["text"]:
            text_chunks = text_parser.split_text(t)
            for i_c, chunk in enumerate(text_chunks):
                doc = {
                    "_index": index_name,
                    'pipeline': ingest_pipeline_id,
                    "_source": {"id": idf + str(i)+"_"+str(i_c),
                                "document_id": idf+str(i),
                                "web_text": chunk,
                                "url": url}
                }
                # print(doc)
                yield doc

def write_chunks_to_file(gen, output_name):
    # with open(output_name, 'w') as f:
    #     for c in gen:
    #         json.dump(c, f)
    #         f.write('\n')  # Write a newline after each JSON object
    with open(output_name, 'w') as f:
        json_objects = [json.dumps(obj) for obj in gen]
        f.write("[\n" + ",\n".join(json_objects) + "\n]")


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
    # chunks = gen_chunks_staff()
    chunks = gen_chunk_js()
    write_chunks_to_file(chunks, "data/student_chunked_pagerank.json")
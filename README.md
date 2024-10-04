### Smarter Search and Answer generation

This code implements this architecture for smarter search and answer generation.
![aili](https://github.com/nirandiw/t3-oct-wxd-enablement/blob/main/arch.png)

Following services are hosted in the IBM Cloud.
1. IBM Watsonx Discovery 
2. watsonx.ai service 
You must have access to this account. 

### Step 1:
Code was developed using a `Python 3.11` environment.
Other packages needed are listed in the `requirements.txt` file. 
Run  `pip install requirements.txt`. 

### Step 2:
Create a `.env` file and add the following detail. Save the file in the `src` folder. 

    ES_ENDPOINT = <login to your ibm cloud and find the elasticsearch url under service credentials>
    ES_CERT_PATH = <download the elasticsearch certificate and save it in your local machine as ca.crt. Provide the path>
    ES_USERNAME = <elasticsearch username>
    ES_PWD = <elsticsearch password>
    WXAI_URL = "https://us-south.ml.cloud.ibm.com"
    WXAI_APIKEY = <watsonx.ai api key>
    WXAI_PROJECT= <watsonx.ai project id>

Sections below describe the components in our architecture.
### Establish connection using `connection.py`
Run `python connection.py` and ensure your Watsonx Discovery credentials are working. 

### Upload data. 
Upload the data file `data.json` in to the data folder. 
### Chunk the data using `chunk.py`
1. Create the folder `./data/chunks`.
2. Go the to `src` folder in the terminal.
3. Run `python chunk.py` to chunk the raw data and safe chunks in the folder folder.  
4. You can change the `chunk size` and `chunck overlap` values for different experiments. 

### Ingest the chunked documents using `ingest.py`
1. Set `index_name`. Provide a name for your index.
2. Set `ingest_pipeline_id` Provide a name for your pipeline.
3. Run `python ingest.py` and it will ingest the documents to your index. The code creates a elasticsearch pipeline and generates embeddings using the BGE model and elserv2 model in Watsonx Discovery. 

(Optional) Additional setup: If you want to use another embedding bring your own embedding model as describred here [BYOM.md](https://github.com/nirandiw/t3-oct-wxd-enablement/blob/main/src/byom.md) in to elastic search and change the index mapping and the pipeline accordinly in the `ingest.py` code with the correct model names. 

Note: Sometimes bulk ingest fails. Restart the script excluding the files that were successful. Re-upload partially uploaded json files will not create duplicates. 

### Search using `search.py`
1. Note your index. The index IBM CE created for AILI is `aili-hybrid-bge`. You can reuse it for searching. 
2. Change the `user_query` to your question. 
3. Run `python search.py`. 
4. You can see the results returned from Watsonx Discovery. 

### Queries formatted in `queries.py`

We used a hybrid search approach for AILI.

`querires.py` contains example queries.

The final elasticsearch query that gave the best result is 

    query = QUERY_BM25_ELSER
    knn = KNN_BGE
    rank = RANK_BASIC

Variables are defined in `queries.py`. 

### Evaluate search results using `evaluate.py`
1. Upload the questions you want to evaluate to the `./data/` folder.  
2. Set `ref_set = pd.read_excel('../data/<your questions.xlsx>')` 
3. Run `python evaluate.py`. Script fetches relevant documents from Watsonx Discovery and checks if it matches with the golden reference document ID. 
4. Evalaution results are saved in the `output` folder. 

We ignore any duplicate documents retrieved and returns the total match on the deduplicated retrieved results.

### Generate LLM answers using `answer.py`
`answer.py` follows a simple RAG implementation of AILI, using Watsonx Discovery and watsonx.ai and stores the answers in a outputfile. 

1. Get your `deployment id` and `space id` from watsonx.ai for the answe-generation prompt (i.e., `aili_answer`).  
  1.2 Pass your deployment id in the function `gen_answer()`  
  1.3 Set the space id in the `main()` function. 
2. Set `ref_set = pd.read_excel('../<your questions>.xlsx')` to your question set. 
3. Run `python answer.py`
4. Answers generated are saved in the `output` folder. 

### Generate new questions using `questions.py`

Generates AILI simulated questions for two personas (1) Public and (2) Tax professional. Because we only had access to limited number of questions we simulated possible questions using this script. 

The question generation process is (1) Sample `100` documents (2) For each document generate `3` questions for each persona. 

1. Get your `deployment id` and `space id` from the watsonx.ai for your question-generation prompt (i.e., `aili_questions_llama`)  
  1.2 Pass your deploymentid in the function `gen_questions()`
  1.3 Set the space id in the `main()` function. 
2. Run `python questions.py` 
3. Generated questions are saved in the `output` folder. 

### `update.py`

To be completed

### Common functions in `utils.py` 

1. `load_json(filename)` : loads a file as a json string
2. `save_json(data, filename)`: save the data in a json file
3. `part_json(file_path,output_folder_path)` : seperaetes a long list of json strings to seperate files for each ingestion. 
4. `clean_text(text)` : cleans text before ingesting to watsonx disocvery. 

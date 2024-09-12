### AILI Smarter Search and Answer generation
This reposity maintains the code used in the IBM CE-ATO AILI project.

This code implements this architecture for AILI smarter search and answer generation.
![aili](https://github.ibm.com/anz-tech-garage/ce-ato-aili/blob/main/AILI_architecture.png)

Following services are hosted in the IBM Cloud - Australian Taxanation Office (2791946) acount.
1. IBM Watsonx Discovery 
2. watsonx.ai service 
You must have access to this account. 

### Step 1:
Code was developed using a `Python 3.11` environment.
Other packages needed are listed in the `requirements.txt` file. 
Run  `pip install requirements.txt`. 

### Step 2:
Create a `.env` file and add the following detail. Save the file in the `src` folder. 
`
ES_ENDPOINT = <login to your ibm cloud and find the elasticsearch url under service credentials>
ES_CERT_PATH = <download the elasticsearch certificate and save it in your local machine as ca.crt. Provide the path>
ES_USERNAME = <elasticsearch username>
ES_PWD = <elsticsearch password>
WXAI_URL = "https://us-south.ml.cloud.ibm.com"
WXAI_APIKEY = <watsonx.ai api key>
WXAI_PROJECT= <watsonx.ai project id>
`

### Step 2: Upload data. 

Upload the data file `ibm_pr_clean.json` in to the data folder. [Link to the data] (https://govteams.sharepoint.com/:x:/r/sites/atoibm/Shared%20Documents/06.%20Data/pb-13x3-qas.xlsx?d=w4372d7af65d644388bf54fc72de1858e&csf=1&web=1&e=HOeRGw)

### Step 2: Chunk the data using `chunk.py`

Create the folder `./data/chunks`.
Go the to `src` folder in the terminal.
Run `python chunk.py` to chunk the raw data and safe chunks in the folder folder.  
You can change the `chunk size` and `chunck overlap` values for different experiments. 

### Step 3: Ingest the chunked documents using `ingest.py`
Set `index_name`. Provide a name for your index.
Set `ingest_pipeline_id` Provide a name for your pipeline.
Run `python ingest.py` and it will ingest the documents to your index. The code creates a elasticsearch pipeline and generates embeddings using the BGE model and elserv2 model in Watsonx Discovery. 

(Optional) Additional setup: If you want to use another embedding bring your own embedding model as describred here <byom doc link> and change the index mapping and the pipeline accordinly in the `ingest.py` code. 




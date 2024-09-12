import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch


def connect_wxd():
    load_dotenv()
    wxd_endpoint = os.environ["ES_ENDPOINT"]
    wxd_username = os.environ["ES_USERNAME"]
    wxd_pwd = os.environ["ES_PWD"]
    wxd_ca = os.environ["ES_CERT_PATH"]

    client = Elasticsearch(
        wxd_endpoint,
        ca_certs=wxd_ca,
        basic_auth=(wxd_username, wxd_pwd)
    )

    print(client.info())
    return client


def check_model_status(model_id, client):
    status = client.ml.get_trained_models(
        model_id=model_id, include="definition_status"
    )
    return status

def connect_wxai():
    load_dotenv()
   
    credentials = {
        "url" :os.environ["WXAI_URL"],
        "apikey" :os.environ["WXAI_APIKEY"],
    }
    return credentials
    

    
if __name__ == "__main__":
    client = connect_wxd()

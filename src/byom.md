# t3


Python version = 3.11

Required Python packages:
```
pip install elasticsearch python-dotenv elasticsearch eland sentence_transformers
```

Create a .env file
```
WXD_ENDPOINT=https://$USER_NAME:$PWD@https://5159d144-1c73-4165-b2c8-5c274274acbc.br37s45d0p54n73ffbr0.databases.appdomain.cloud:31794
```

Get the cert file, save as `.crt`:
https://github.ibm.com/watsonx-apac/get-started-with-elastic-techzone


To load a Huggingface model into Elastic:
```
docker run -it --network host docker.elastic.co/eland/eland:8.9.0
```
After the container started, used `docker ps` to find out the docker ID. Copy your SSL cert file into the container
```
docker cp ca.crt DOCKER_ID:/eland/ca.crt
```
To import and start a Huggingface model, eg. sentence-transformers/all-MiniLM-L12-v2, run the following from the container:
```
eland_import_hub_model --url WXD_URL -u USENAME -p PWD --ca-certs ca.crt --hub-model-id sentence-transformers/all-MiniLM-L12-v2 --task-type text_embedding --start
```

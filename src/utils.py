import csv,json
import sys
import re, string
import numpy as np
from connection import connect_wxai
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
import concurrent.futures as cf
from concurrent.futures import ThreadPoolExecutor
import json
import pandas as pd
from sentence_transformers import SentenceTransformer


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def save_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


def part_json(file_path,output_folder_path):
    chuncked_data = load_json(file_path)
    print(len(chuncked_data))
    size = 5000
    chuncked_data_json_files = [chuncked_data[x:x + size] for x in
                                range(0, len(chuncked_data), size)]
    print(len(chuncked_data_json_files))
    i = 0
    for chuncked_data_json_file in chuncked_data_json_files:
        save_json(chuncked_data_json_file,
                  output_folder_path + '/part-' + str(i) + ".json")
        i = i + size
        
def clean_text(text):

    # Remove \r
    text = re.sub(r'[\r]', ' ', text)
    # Remove any Unicode characters
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    # Remove specific Unicode sequence \u00e2\u20ac\u00a2
    pattern_to_remove = r'\\u00e2\\u20ac\\u00a2'
    # Remove the escaped Unicode string using regex
    text = re.sub(pattern_to_remove, '', text)
    # Optionally, remove any additional unwanted sequences
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with a single space
    return text
    

if __name__ == "__main__":
    part_json('../legal_chunked.json','../legal_chunks')
    

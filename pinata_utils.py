import requests
import os
import streamlit as st

# Define your Pinata API keys and endpoint here or import them from a secure place
PINATA_API_KEY = '213d8bedb3fdbbee29d9'
PINATA_API_SECRET = '678bb5c15321ad807c3065ffcad1a72f42cc84a35e352ab39669c2d0f47c02a1'
PINATA_API_URL = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJlNDFhZGIyMi1lMzA4LTRkZWYtOWQ3OS04N2FjZWU2N2ZkY2EiLCJlbWFpbCI6ImthcnRoaWtleWFuc3J1dGlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjIxM2Q4YmVkYjNmZGJiZWUyOWQ5Iiwic2NvcGVkS2V5U2VjcmV0IjoiNjc4YmI1YzE1MzIxYWQ4MDdjMzA2NWZmY2FkMWE3MmY0MmNjODRhMzVlMzUyYWIzOTY2OWMyZDBmNDdjMDJhMSIsImV4cCI6MTc2MzM4MjIwMn0.HL8rjcAFHz7wL1BTBOCbESsYvuMe2nbkd2IuK8Aap0s'


import requests

def upload_to_pinata(file_path, pinata_api_key, pinata_secret_api_key):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": str(pinata_api_key),  # Ensure the keys are strings
        "pinata_secret_api_key": str(pinata_secret_api_key)
    }
    
    try:
        with open(file_path, "rb") as file:
            files = {
                "file": file
            }
            response = requests.post(url, files=files, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text, "status_code": response.status_code}
    except Exception as e:
        return {"error": str(e)}

    
def download_file_from_ipfs(ipfs_hash, download_path):
    """
    Download a file from IPFS using the provided IPFS hash.
    :param ipfs_hash: The hash of the file on IPFS.
    :param download_path: The local path to save the downloaded file.
    :return: None
    """
    url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(download_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully to {download_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download file from IPFS. Error: {e}")

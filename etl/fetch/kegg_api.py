# Ingest from KEGG API
# KEGG API documentation: https://www.kegg.jp/kegg/rest/keggapi.html
import requests

def fetch_kegg_data(endpoint: str, dbentries: str) -> str:
    """
    Fetch data from the KEGG API.

    Args:
        endpoint (str): The KEGG API endpoint to fetch data from.

    Returns:
        str: The raw response text from the KEGG API.
    """
    base_url = "https://rest.kegg.jp"
    url = f"{base_url}/{endpoint}/{dbentries}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from KEGG API: {e}")
        return ""
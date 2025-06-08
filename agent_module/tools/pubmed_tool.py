import os, time, textwrap, requests, xml.etree.ElementTree as ET
from typing import List, Dict, Any
from dotenv import load_dotenv
import csv
import io

load_dotenv()

def _qp(base: Dict[str, Any]) -> Dict[str, Any]:
    """Inject api_key only when present."""
    return {**base, **({"api_key": get_ncbi_api_key()} if get_ncbi_api_key() else {})}


def _strip(elem: ET.Element | None) -> str:
    """Flatten nested XML text, return '' if elem is None."""
    return "".join(elem.itertext()).strip() if elem is not None else ""


def _first_n_words(txt: str, n: int = 250) -> str:
    return " ".join(txt.split()[:n])


def pubmed_to_pmc_full_text_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
   
    """
    Search biomedical literature on PubMed using a keyword query, returning up to `max_results` articles with metadata and abstracts.

    For each article, return:
      - title: Article title (str)
      - authors: Up to 3 author names (list of str)
      - journal: Journal name (str)
      - published_date: Date of publication (str, may be partial)
      - summary: Abstract text if available (str)
      - url: Link to article on PubMed (str)

    Args:
        query (str): Search term for PubMed (can use keywords, phrases, MeSH, Boolean, etc).
        max_results (int): Maximum number of articles to return (default: 10).

    Returns:
        List[dict]: Each dict contains:
            - title (str)
            - authors (list of str)
            - journal (str)
            - published_date (str)
            - summary (str)
            - url (str)

    Notes:
        - Uses the NCBI E-utilities API with your NCBI API key if provided.
        - Handles no-result and error cases gracefully (returns empty list).
        - For best results, use precise queries, e.g. 'diabetes mellitus[mesh] AND genetics[mesh]'.
        - Abstracts may be missing for some articles.
    
    Example:
        articles = pubmed_to_pmc_full_text_search("cancer immunotherapy", max_results=5)

    This function is suitable for LLMs, tools, or agents that need to retrieve recent PubMed literature with summaries and structured metadata.
    """
    try:
        api_key = os.getenv("NCBI_API_KEY")
    except ValueError:
        print("No NCBI API key found. Proceeding without key (rate limits apply).")
        api_key = None

    # Step 1: Search PubMed
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    if api_key:
        search_params["api_key"] = api_key

    try:
        # Get article IDs
        search_resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params=search_params,
            timeout=30
        )
        search_resp.raise_for_status()
        pmids = search_resp.json().get("esearchresult", {}).get("idlist", [])

        if not pmids:
            print(f"No results found for query: {query}")
            print("Try using MeSH terms, e.g.: 'cancer[mesh] AND treatment[mesh]'")
            return []

        # Step 2: Get article details
        summary_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "json"
        }
        if api_key:
            summary_params["api_key"] = api_key

        summary_resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params=summary_params,
            timeout=10
        )
        summary_resp.raise_for_status()
        articles_data = summary_resp.json()["result"]

        # Step 3: Get abstracts
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        if api_key:
            fetch_params["api_key"] = api_key

        fetch_resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params=fetch_params,
            timeout=10
        )
        fetch_resp.raise_for_status()

        # Parse XML for abstracts
        root = ET.fromstring(fetch_resp.text)
        abstracts = {}
        for article in root.findall(".//PubmedArticle"):
            pmid = article.find(".//PMID")
            abstract = article.find(".//Abstract/AbstractText")
            if pmid is not None and abstract is not None:
                abstracts[pmid.text] = abstract.text

        # Format results
        results = []
        for pmid in pmids:
            article = articles_data[pmid]
            results.append({
                "title": article.get("title", "").rstrip("."),
                "authors": [a.get("name", "") for a in article.get("authors", [])[:3]],
                "journal": article.get("source", ""),
                "published_date": article.get("pubdate", ""),
                "summary": abstracts.get(pmid, "No abstract available"),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to PubMed: {e}")
        return []
    except Exception as e:
        print(f"Error processing results: {e}")
        return []

def articles_to_csv(articles: List[Dict[str, Any]]) -> str:
    """
    Convert a list of article dicts to a CSV string.
    """
    if not articles:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["title", "authors", "journal", "published_date", "summary", "url"],
        extrasaction='ignore'
    )
    writer.writeheader()
    for article in articles:
        row = article.copy()
        row["authors"] = ", ".join(row.get("authors", []))
        writer.writerow(row)
    return output.getvalue()


def save_csv_file(articles: List[Dict[str, Any]], filename: str = "search_results.csv") -> str:
    """
    Save articles as a CSV file and return the file path.
    """
    csv_content = articles_to_csv(articles)
    with open(filename, "w", encoding="utf-8", newline='') as f:
        f.write(csv_content)
    return os.path.abspath(filename)
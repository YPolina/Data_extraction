import os
import json
import requests
from tqdm import tqdm
from Bio import Entrez
from src.utils.file_io import recreate_dir


def search_pubmed(query, retmax=10, free_full_text=True):
    if free_full_text:
        query = f"{query} AND free full text[filter]"
    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
    record = Entrez.read(handle)
    return record["IdList"]


def fetch_metadata(pmids):
    handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="xml")
    records = Entrez.read(handle)
    articles = []
    for article in records["PubmedArticle"]:
        medline = article["MedlineCitation"]
        article_data = medline["Article"]

        info = {
            "PMID": str(medline["PMID"]),
            "Title": article_data.get("ArticleTitle", ""),
            "Abstract": " ".join(article_data.get("Abstract", {}).get("AbstractText", [])),
            "Journal": article_data["Journal"]["Title"],
            "Authors": [a.get("LastName","")+" "+a.get("ForeName","")
                        for a in article_data.get("AuthorList", []) if "LastName" in a][:3],
            "DOI": None,
        }

        # DOI
        ids = article["PubmedData"]["ArticleIdList"]
        for aid in ids:
            if aid.attributes.get("IdType") == "doi":
                info["DOI"] = str(aid)

        articles.append(info)
    return articles


def get_unpaywall_pdf(doi, email):
    if not doi:
        return None
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if data.get("best_oa_location") and data["best_oa_location"].get("url_for_pdf"):
                return data["best_oa_location"]["url_for_pdf"]
    except Exception as e:
        print(f"Unpaywall error for {doi}: {e}")
    return None


def download_pdf(pdf_url, pmid, output_dir):
    if not pdf_url:
        return False
    try:
        r = requests.get(pdf_url, stream=True, timeout=20)
        if r.status_code == 200 and "pdf" in r.headers.get("content-type","").lower():
            out_path = os.path.join(output_dir, f"{pmid}.pdf")
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading PDF for PMID {pmid}: {e}")
    return False


def article_collection(query, email, output_dir = './data/raw_data', retmax=20):
    Entrez.email = email
    pmids = search_pubmed(query, retmax=retmax)
    articles = fetch_metadata(pmids)
    recreate_dir(output_dir)

    success = 0
    downloaded_metadata = []

    for art in tqdm(articles, desc="Downloading PDFs"):
        pdf_url = None
        if art["DOI"]:
            pdf_url = get_unpaywall_pdf(art["DOI"], email)

        if download_pdf(pdf_url, art["PMID"], output_dir):
            success += 1
            art["pdf_url"] = pdf_url
            downloaded_metadata.append(art)

    json_path = output_dir / "metadata.json"
    if downloaded_metadata:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(downloaded_metadata, f, ensure_ascii=False, indent=2)

    print(f"\nDownloaded {success}/{len(articles)} PDFs")
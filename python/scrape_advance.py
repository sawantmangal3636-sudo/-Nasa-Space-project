#!/usr/bin/env python3
#
import os
import re
import time
import random
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------- CONFIG -----------------
GITHUB_CSV = "https://raw.githubusercontent.com/jgalazka/SB_publications/refs/heads/main/SB_publication_PMC.csv"  # raw GitHub CSV URL (or leave empty for local fallback)
LOCAL_CANDIDATES = [
    "data/SB_publication_PMC.csv",
    "SB_publication_PMC.csv"
]
OUTPUT_CSV = "pmc_cleaned_data.csv"
CONCURRENCY = 4
MIN_DELAY = 0.5
MAX_DELAY = 1.5
REQUEST_TIMEOUT = 20
EMAIL = "sawantmangal9393@gmail.com"  # replace with your email
RETRY_TOTAL = 3
RETRY_BACKOFF = 1
SAVE_ENCODING = "utf-8-sig"
# -----------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

HEADERS = {"User-Agent": f"PMC-Scraper/1.0 (mailto:{EMAIL}) Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

lock = Lock()
seen_titles = set()
session = None

def create_session():
    s = requests.Session()
    try:
        retries = Retry(
            total=RETRY_TOTAL,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST"])
        )
    except TypeError:
        retries = Retry(
            total=RETRY_TOTAL,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=frozenset(["GET", "POST"])
        )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update(HEADERS)
    return s

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', str(text)).replace("\xa0", " ").strip()

def normalize_date(date_str):
    if not date_str:
        return None
    date_str = clean_text(date_str)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y")
        except:
            continue
    return None

def get_meta_one(soup, name):
    tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
    if tag and tag.get("content"):
        return clean_text(tag.get("content"))
    return None

def get_meta_all(soup, name):
    tags = soup.find_all("meta", attrs={"name": name})
    return [clean_text(t.get("content") or "") for t in tags if t.get("content")]

def pmcid_from_url(url):
    m = re.search(r'(PMC\d+)', url, re.I)
    return m.group(1) if m else None

def scrape_publication(link, idx):
    try:
        resp = session.get(link, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            logging.warning("[%d] Failed %s (status %s)", idx, link, resp.status_code)
            return None
        soup = BeautifulSoup(resp.text, "html.parser")

        title = get_meta_one(soup, "citation_title") or ""
        authors = get_meta_all(soup, "citation_author")
        authors_str = "; ".join(authors)
        journal = get_meta_one(soup, "citation_journal_title") or ""
        date_raw = get_meta_one(soup, "citation_publication_date") or ""
        year = normalize_date(date_raw)
        keywords_list = get_meta_all(soup, "citation_keywords")
        keywords = ", ".join(keywords_list)
        abstract = get_meta_one(soup, "DC.Description") or ""
        if not abstract:
            abs_tag = soup.find("div", class_="abstract") or soup.find("section", id="abstract")
            if abs_tag:
                abstract = clean_text(abs_tag.get_text(separator=" "))

        pmc_id = pmcid_from_url(link)

        record = {
            "title": title,
            "authors": authors_str,
            "journal": journal,
            "year": year,
            "keywords": keywords,
            "abstract": abstract,
            "url": link,
            "pmcid": pmc_id
        }

        return record
    except Exception as e:
        logging.exception("[%d] Exception scraping %s: %s", idx, link, e)
        return None

def load_input_dataframe():
    if GITHUB_CSV:
        try:
            df = pd.read_csv(GITHUB_CSV)
            logging.info("Loaded input CSV from GitHub (rows=%d).", len(df))
            return df
        except Exception as e:
            logging.warning("Failed to load from GitHub URL: %s", e)
    for p in LOCAL_CANDIDATES:
        if os.path.exists(p):
            logging.info("Loading local CSV: %s", p)
            return pd.read_csv(p)
    raise FileNotFoundError("Input CSV not found.")

def find_link_column(df):
    for c in df.columns:
        if "link" in c.lower() or "url" in c.lower():
            return c
    raise ValueError("Could not find a link column in CSV.")

def append_record_to_csv(record):
    if not record or not record.get("title"):
        return False
    with lock:
        title = record.get("title")
        if title in seen_titles:
            return False
        df_row = pd.DataFrame([record])
        header_needed = not os.path.exists(OUTPUT_CSV)
        df_row.to_csv(OUTPUT_CSV, mode="a", header=header_needed, index=False, encoding=SAVE_ENCODING)
        seen_titles.add(title)
        return True

def worker(link, idx):
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    rec = scrape_publication(link, idx)
    if rec:
        append_record_to_csv(rec)

def main():
    global session
    session = create_session()
    df_in = load_input_dataframe()
    link_col = find_link_column(df_in)
    links = list(dict.fromkeys(df_in[link_col].dropna().astype(str).map(str.strip)))

    if os.path.exists(OUTPUT_CSV):
        existing = pd.read_csv(OUTPUT_CSV)
        existing_titles = set(existing.get("title", pd.Series([])).dropna().astype(str).tolist())
        seen_titles.update(existing_titles)

    logging.info("Found %d links to scrape.", len(links))
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = [ex.submit(worker, lnk, i) for i, lnk in enumerate(links, 1)]
        for _ in as_completed(futures):
            pass
    logging.info("Scraping completed. Output saved to %s", os.path.abspath(OUTPUT_CSV))

if __name__ == "__main__":
    main()

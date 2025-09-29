# import os
# import re
# import json
# import time
# import requests
# import pandas as pd
# from bs4 import BeautifulSoup
# from datetime import datetime

# # ========= CONFIG ==========
# INPUT_CSV = "SB_publication_PMC.csv"
# OUTPUT_DIR = "data"
# ALL_JSON = "all_publications.json"
# WAIT_TIME = 2   # seconds between requests (be nice to servers!)
# # ===========================

# # --- Utility: clean text ---
# def clean_text(text):
#     if not text:
#         return ""
#     # Remove extra spaces and control chars
#     text = re.sub(r'\s+', ' ', text)
#     text = text.replace("\xa0", " ").strip()
#     return text

# # --- Normalize date ---
# def normalize_date(date_str):
#     if not date_str:
#         return None
#     date_str = clean_text(date_str)
#     for fmt in ["%B %d, %Y", "%Y-%m-%d", "%Y %b %d", "%Y %B %d"]:
#         try:
#             return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
#         except:
#             continue
#     return date_str  # fallback (raw if unknown format)

# # --- Clean authors ---
# def clean_authors(author_list):
#     cleaned = []
#     for a in author_list:
#         a = clean_text(a)
#         # Normalize like "Lastname, Firstname"
#         parts = a.split()
#         if len(parts) >= 2:
#             last = parts[-1]
#             first = " ".join(parts[:-1])
#             cleaned.append(f"{last}, {first}")
#         else:
#             cleaned.append(a)
#     return list(dict.fromkeys(cleaned))  # remove duplicates, keep order

# # --- Normalize section names ---
# def normalize_section_name(name):
#     if not name:
#         return None
#     name = name.lower()
#     section_map = {
#         "introduction": "Introduction",
#         "methods": "Methods",
#         "materials and methods": "Methods",
#         "results": "Results",
#         "discussion": "Discussion",
#         "results and discussion": "Results & Discussion",
#         "conclusion": "Conclusion",
#         "acknowledgement": "Acknowledgements",
#         "funding": "Funding",
#         "references": "References",
#     }
#     for k, v in section_map.items():
#         if k in name:
#             return v
#     return name.title()

# # --- Scrape one publication ---
# def scrape_publication(link):
#     try:
#         r = requests.get(link, timeout=20)
#         if r.status_code != 200:
#             print(f"⚠️ Failed {link}")
#             return None
#         soup = BeautifulSoup(r.text, "html.parser")

#         # Title
#         title = clean_text(soup.find("h1").text if soup.find("h1") else "")

#         # Date
#         date_tag = soup.find("span", class_="cit")
#         date = normalize_date(date_tag.text if date_tag else "")

#         # Authors
#         authors = []
#         author_tags = soup.find_all("a", class_="full-name")
#         for a in author_tags:
#             authors.append(a.text)
#         authors = clean_authors(authors)

#         # Abstract
#         abstract = ""
#         abs_tag = soup.find("div", class_="abstract")
#         if abs_tag:
#             abstract = clean_text(abs_tag.text)

#         # Sections
#         sections = {}
#         for sec in soup.find_all("div", class_="tsec sec"):
#             sec_title = normalize_section_name(sec.find("h2").text if sec.find("h2") else "")
#             sec_text = clean_text(sec.get_text(separator=" "))
#             if sec_title:
#                 sections[sec_title] = sec_text

#         # Build record
#         record = {
#             "title": title,
#             "link": link,
#             "date": date,
#             "authors": authors,
#             "n_authors": len(authors),
#             "abstract": abstract,
#             "sections": sections,
#         }
#         return record
#     except Exception as e:
#         print(f"❌ Error scraping {link}: {e}")
#         return None

# # --- Main run ---
# def main():
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     df = pd.read_csv(INPUT_CSV)
#     links = df["Link"].dropna().tolist()

#     all_records = []
#     seen_titles = set()

#     for i, link in enumerate(links, 1):
#         print(f"[{i}/{len(links)}] Scraping {link}")
#         rec = scrape_publication(link)
#         if rec:
#             if rec["title"] not in seen_titles:  # remove duplicates by title
#                 seen_titles.add(rec["title"])
#                 all_records.append(rec)
#                 # Save individual JSON
#                 fname = os.path.join(OUTPUT_DIR, f"pub_{i}.json")
#                 with open(fname, "w", encoding="utf-8") as f:
#                     json.dump(rec, f, indent=2, ensure_ascii=False)
#         time.sleep(WAIT_TIME)

#     # Save all together
#     with open(ALL_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_records, f, indent=2, ensure_ascii=False)

#     print(f"✅ Done! Saved {len(all_records)} publications.")

# if __name__ == "__main__":
#     main()
# import os
# import re
# import json
# import time
# import requests
# import pandas as pd
# from bs4 import BeautifulSoup
# from datetime import datetime

# # ========= CONFIG ==========
# INPUT_CSV = "SB_publication_PMC.csv"
# OUTPUT_DIR = "data"
# ALL_JSON = "all_publications.json"
# WAIT_TIME = 2   # seconds between requests (be nice to servers!)
# GITHUB_CSV_URL = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
# # ===========================

# # --- Download CSV if missing or empty ---
# def download_csv_if_missing(path):
#     if not os.path.exists(path) or os.path.getsize(path) == 0:
#         print("📥 CSV missing or empty — downloading from GitHub...")
#         r = requests.get(GITHUB_CSV_URL, timeout=20)
#         if r.status_code == 200 and r.text.strip():
#             with open(path, "w", encoding="utf-8") as f:
#                 f.write(r.text)
#             print("✅ Downloaded CSV successfully.")
#         else:
#             raise RuntimeError("❌ Failed to download CSV from GitHub.")

# # --- Utility: clean text ---
# def clean_text(text):
#     if not text:
#         return ""
#     text = re.sub(r'\s+', ' ', text)
#     text = text.replace("\xa0", " ").strip()
#     return text

# # --- Normalize date ---
# def normalize_date(date_str):
#     if not date_str:
#         return None
#     date_str = clean_text(date_str)
#     for fmt in ["%B %d, %Y", "%Y-%m-%d", "%Y %b %d", "%Y %B %d"]:
#         try:
#             return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
#         except:
#             continue
#     return date_str  # fallback if unknown

# # --- Clean authors ---
# def clean_authors(author_list):
#     cleaned = []
#     for a in author_list:
#         a = clean_text(a)
#         if not a:
#             continue
#         # Try to standardize "Lastname, Firstname"
#         parts = a.split()
#         if len(parts) >= 2:
#             last = parts[-1]
#             first = " ".join(parts[:-1])
#             cleaned.append(f"{last}, {first}")
#         else:
#             cleaned.append(a)
#     return list(dict.fromkeys(cleaned))  # remove duplicates, keep order

# # --- Normalize section names ---
# def normalize_section_name(name):
#     if not name:
#         return None
#     name = name.lower()
#     section_map = {
#         "introduction": "Introduction",
#         "methods": "Methods",
#         "materials and methods": "Methods",
#         "results": "Results",
#         "discussion": "Discussion",
#         "results and discussion": "Results & Discussion",
#         "conclusion": "Conclusion",
#         "acknowledgement": "Acknowledgements",
#         "funding": "Funding",
#         "references": "References",
#     }
#     for k, v in section_map.items():
#         if k in name:
#             return v
#     return name.title()

# # --- Scrape one publication ---
# def scrape_publication(link):
#     try:
#         r = requests.get(link, timeout=20)
#         if r.status_code != 200:
#             print(f"⚠️ Failed {link}")
#             return None
#         soup = BeautifulSoup(r.text, "html.parser")

#         # Title
#         title = clean_text(soup.find("h1").text if soup.find("h1") else "")

#         # Date
#         date_tag = soup.find("span", class_="cit")
#         date = normalize_date(date_tag.text if date_tag else "")

#         # Authors
#         authors = []
#         author_tags = soup.find_all("a", class_="full-name")
#         for a in author_tags:
#             authors.append(a.text)
#         authors = clean_authors(authors)

#         # Abstract
#         abstract = ""
#         abs_tag = soup.find("div", class_="abstract")
#         if abs_tag:
#             abstract = clean_text(abs_tag.text)

#         # Sections
#         sections = {}
#         for sec in soup.find_all("div", class_="tsec sec"):
#             sec_title = normalize_section_name(sec.find("h2").text if sec.find("h2") else "")
#             sec_text = clean_text(sec.get_text(separator=" "))
#             if sec_title:
#                 sections[sec_title] = sec_text

#         record = {
#             "title": title,
#             "link": link,
#             "date": date,
#             "authors": authors,
#             "n_authors": len(authors),
#             "abstract": abstract,
#             "sections": sections,
#         }
#         return record
#     except Exception as e:
#         print(f"❌ Error scraping {link}: {e}")
#         return None

# # --- Main run ---
# def main():
#     os.makedirs(OUTPUT_DIR, exist_ok=True)

#     # Ensure CSV exists
#     download_csv_if_missing(INPUT_CSV)

#     df = pd.read_csv(INPUT_CSV)
#     links = df["Link"].dropna().tolist()

#     all_records = []
#     seen_titles = set()

#     for i, link in enumerate(links, 1):
#         print(f"[{i}/{len(links)}] Scraping {link}")
#         rec = scrape_publication(link)
#         if rec:
#             if rec["title"] not in seen_titles:  # remove duplicates by title
#                 seen_titles.add(rec["title"])
#                 all_records.append(rec)
#                 # Save individual JSON
#                 fname = os.path.join(OUTPUT_DIR, f"pub_{i}.json")
#                 with open(fname, "w", encoding="utf-8") as f:
#                     json.dump(rec, f, indent=2, ensure_ascii=False)
#         time.sleep(WAIT_TIME)

#     # Save all together
#     with open(ALL_JSON, "w", encoding="utf-8") as f:
#         json.dump(all_records, f, indent=2, ensure_ascii=False)

#     print(f"✅ Done! Saved {len(all_records)} publications.")

# if __name__ == "__main__":
#     main()

# import os
# import re
# import time
# import requests
# import pandas as pd
# from bs4 import BeautifulSoup
# from datetime import datetime

# # ========= CONFIG ==========
# INPUT_CSV = "data/SB_publication_PMC.csv"       # input file
# OUTPUT_CSV = "data/cleaned_publications.csv"    # output file
# WAIT_TIME = 2   # seconds between requests
# # ===========================

# # --- Utility: clean text ---
# def clean_text(text):
#     if not text:
#         return ""
#     return re.sub(r'\s+', ' ', text).replace("\xa0", " ").strip()

# # --- Normalize date ---
# def normalize_date(date_str):
#     if not date_str:
#         return None
#     date_str = clean_text(date_str)
#     for fmt in ["%B %d, %Y", "%Y-%m-%d", "%Y %b %d", "%Y %B %d"]:
#         try:
#             return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
#         except:
#             continue
#     return date_str

# # --- Normalize section names ---
# def normalize_section_name(name):
#     if not name:
#         return None
#     name = name.lower()
#     mapping = {
#         "introduction": "Introduction",
#         "methods": "Methods",
#         "materials and methods": "Methods",
#         "results": "Results",
#         "discussion": "Discussion",
#         "results and discussion": "Results & Discussion",
#         "conclusion": "Conclusion",
#         "acknowledgement": "Acknowledgements",
#         "funding": "Funding",
#         "references": "References",
#     }
#     for k, v in mapping.items():
#         if k in name:
#             return v
#     return name.title()

# # --- Scrape one publication ---
# def scrape_publication(link):
#     try:
#         r = requests.get(link, timeout=20)
#         if r.status_code != 200:
#             print(f"⚠️ Failed {link}")
#             return None
#         soup = BeautifulSoup(r.text, "html.parser")

#         # Title
#         title = clean_text(soup.find("h1").text if soup.find("h1") else "")

#         # Date
#         date_tag = soup.find("span", class_="cit")
#         date = normalize_date(date_tag.text if date_tag else "")

#         # Authors
#         authors = [clean_text(a.text) for a in soup.find_all("a", class_="full-name")]
#         authors_str = "; ".join(authors)

#         # Abstract
#         abstract = ""
#         abs_tag = soup.find("div", class_="abstract")
#         if abs_tag:
#             abstract = clean_text(abs_tag.text)

#         # Sections
#         sections = {}
#         for sec in soup.find_all("div", class_="tsec sec"):
#             sec_title = normalize_section_name(sec.find("h2").text if sec.find("h2") else "")
#             sec_text = clean_text(sec.get_text(separator=" "))
#             if sec_title:
#                 sections[sec_title] = sec_text

#         record = {
#             "title": title,
#             "link": link,
#             "date": date,
#             "authors": authors_str,
#             "n_authors": len(authors),
#             "abstract": abstract
#         }
#         # Merge sections into record
#         record.update(sections)

#         return record
#     except Exception as e:
#         print(f"❌ Error scraping {link}: {e}")
#         return None

# # --- Main run ---
# def main():
#     if not os.path.exists(INPUT_CSV):
#         raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

#     df = pd.read_csv(INPUT_CSV)
#     links = df["Link"].dropna().tolist()

#     all_records = []
#     seen_titles = set()

#     for i, link in enumerate(links, 1):
#         print(f"[{i}/{len(links)}] Scraping {link}")
#         rec = scrape_publication(link)
#         if rec:
#             if rec["title"] not in seen_titles:
#                 seen_titles.add(rec["title"])
#                 all_records.append(rec)
#         time.sleep(WAIT_TIME)

#     if all_records:
#         out_df = pd.DataFrame(all_records)
#         out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
#         print(f"✅ Done! Saved {len(all_records)} publications to {OUTPUT_CSV}")
#     else:
#         print("⚠️ No records scraped!")

# if __name__ == "__main__":
#     main()
import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# ========= CONFIG ==========
# GitHub raw CSV link (replace with your repo link)
GITHUB_CSV = "https://raw.githubusercontent.com/jgalazka/SB_publications/refs/heads/main/SB_publication_PMC.csv"

OUTPUT_CSV = "pmc_cleaned_data.csv"   # final file for dashboard
WAIT_TIME = 2  # seconds between requests
# ===========================

# --- Utility: clean text ---
def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).replace("\xa0", " ").strip()

# --- Normalize date ---
def normalize_date(date_str):
    if not date_str:
        return None
    date_str = clean_text(date_str)
    for fmt in ["%B %d, %Y", "%Y-%m-%d", "%Y %b %d", "%Y %B %d"]:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except:
            continue
    return date_str

# --- Normalize section names ---
def normalize_section_name(name):
    if not name:
        return None
    name = name.lower()
    mapping = {
        "introduction": "Introduction",
        "methods": "Methods",
        "materials and methods": "Methods",
        "results": "Results",
        "discussion": "Discussion",
        "results and discussion": "Results & Discussion",
        "conclusion": "Conclusion",
        "acknowledgement": "Acknowledgements",
        "funding": "Funding",
        "references": "References",
    }
    for k, v in mapping.items():
        if k in name:
            return v
    return name.title()

# --- Scrape one publication ---
def scrape_publication(link):
    try:
        r = requests.get(link, timeout=20)
        if r.status_code != 200:
            print(f"⚠️ Failed {link}")
            return None
        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        title = clean_text(soup.find("h1").text if soup.find("h1") else "")

        # Date
        date_tag = soup.find("span", class_="cit")
        date = normalize_date(date_tag.text if date_tag else "")

        # Authors
        authors = [clean_text(a.text) for a in soup.find_all("a", class_="full-name")]
        authors_str = "; ".join(authors)

        # Abstract
        abstract = ""
        abs_tag = soup.find("div", class_="abstract")
        if abs_tag:
            abstract = clean_text(abs_tag.text)

        # Sections
        sections = {}
        for sec in soup.find_all("div", class_="tsec sec"):
            sec_title = normalize_section_name(sec.find("h2").text if sec.find("h2") else "")
            sec_text = clean_text(sec.get_text(separator=" "))
            if sec_title:
                sections[sec_title] = sec_text

        record = {
            "title": title,
            "link": link,
            "date": date,
            "authors": authors_str,
            "n_authors": len(authors),
            "abstract": abstract
        }
        # Merge sections into record
        record.update(sections)

        return record
    except Exception as e:
        print(f"❌ Error scraping {link}: {e}")
        return None

# --- Main run ---
def main():
    print("📥 Downloading input CSV from GitHub...")
    df = pd.read_csv(GITHUB_CSV)
    links = df["Link"].dropna().tolist()

    all_records = []
    seen_titles = set()

    for i, link in enumerate(links, 1):
        print(f"[{i}/{len(links)}] Scraping {link}")
        rec = scrape_publication(link)
        if rec:
            if rec["title"] not in seen_titles:
                seen_titles.add(rec["title"])
                all_records.append(rec)
        time.sleep(WAIT_TIME)

    if all_records:
        out_df = pd.DataFrame(all_records)
        out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        print(f"✅ Done! Saved {len(all_records)} publications to {OUTPUT_CSV}")
    else:
        print("⚠️ No records scraped!")

if __name__ == "__main__":
    main()

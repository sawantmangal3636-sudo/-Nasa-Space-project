# import pandas as pd
# import requests
# from bs4 import BeautifulSoup
# import re
# import time
# from collections import Counter
# import matplotlib.pyplot as plt
# import seaborn as sns

# # --- STEP 1: Load the CSV ---
# url = "https://raw.githubusercontent.com/jgalazka/SB_publications/refs/heads/main/SB_publication_PMC.csv"
# df = pd.read_csv(url)

# # Clean columns
# df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
# df.drop_duplicates(inplace=True)

# # Extract PMC IDs
# def pmcid_from_url(url):
#     m = re.search(r'(PMC\d+)', url)
#     return m.group(1) if m else None

# df['pmcid'] = df['link'].apply(pmcid_from_url)

# # --- STEP 2: Scraper function ---
# def scrape_pmc(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#                       "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
#     }

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code != 200:
#             print(f"Failed to fetch: {url}")
#             return None

#         soup = BeautifulSoup(response.content, "html.parser")

#         # Title
#         title_tag = soup.find('h1', class_='content-title')
#         title = title_tag.text.strip() if title_tag else None

#         # Abstract
#         abstract_tag = soup.find('div', class_='abstract')
#         abstract = abstract_tag.text.strip() if abstract_tag else None

#         # Authors
#         authors = []
#         for author_tag in soup.select("div.authors-list span.authors__name"):
#             authors.append(author_tag.text.strip())

#         # Publication date
#         pub_date_tag = soup.find('span', class_='cit')
#         pub_date = pub_date_tag.text.strip() if pub_date_tag else None

#         # Journal Name
#         journal_tag = soup.find('button', class_='journal-actions-trigger')
#         journal = journal_tag.text.strip() if journal_tag else None

#         # Keywords
#         keywords = []
#         keywords_tag = soup.find('div', class_='keywords-section')
#         if keywords_tag:
#             for kw in keywords_tag.find_all('span', class_='kwd-text'):
#                 keywords.append(kw.text.strip())

#         return {
#             "title": title,
#             "abstract": abstract,
#             "authors": ", ".join(authors),
#             "publication_date": pub_date,
#             "journal": journal,
#             "keywords": ", ".join(keywords)
#         }

#     except Exception as e:
#         print(f"Error fetching {url}: {e}")
#         return None

# # --- STEP 3: Loop through links and scrape ---
# results = []
# for idx, row in df.iterrows():
#     print(f"Scraping {idx+1}/{len(df)}: {row['link']}")
#     data = scrape_pmc(row['link'])
#     if data:
#         data['pmcid'] = row['pmcid']
#         data['link'] = row['link']
#         results.append(data)
#     time.sleep(1)  # polite scraping

# # --- STEP 4: Save scraped data ---
# result_df = pd.DataFrame(results)

# # --- STEP 5: Data Cleaning ---
# def clean_text(text):
#     if pd.isna(text):
#         return text
#     text = re.sub(r'\s+', ' ', text)  # remove extra spaces/newlines
#     text = text.strip()
#     return text

# for col in ['title', 'abstract', 'authors', 'journal', 'keywords', 'publication_date']:
#     result_df[col] = result_df[col].apply(clean_text)

# # --- STEP 6: Exploratory Data Analysis ---
# print("\n--- Dataset Overview ---")
# print(result_df.info())
# print("\nMissing values per column:\n", result_df.isna().sum())

# # Most frequent authors
# all_authors = [author.strip() for authors in result_df['authors'].dropna() for author in authors.split(',')]
# author_counts = Counter(all_authors)
# top_authors = author_counts.most_common(10)
# print("\nTop 10 Authors:")
# for author, count in top_authors:
#     print(f"{author}: {count} articles")

# # Most common keywords
# all_keywords = [kw.strip() for keywords in result_df['keywords'].dropna() for kw in keywords.split(',')]
# keyword_counts = Counter(all_keywords)
# top_keywords = keyword_counts.most_common(10)
# print("\nTop 10 Keywords:")
# for kw, count in top_keywords:
#     print(f"{kw}: {count} times")

# # Articles per year (extract year from publication_date)
# def extract_year(date_str):
#     if pd.isna(date_str):
#         return None
#     m = re.search(r'\b(19|20)\d{2}\b', date_str)
#     return int(m.group()) if m else None

# result_df['year'] = result_df['publication_date'].apply(extract_year)
# year_counts = result_df['year'].value_counts().sort_index()
# print("\nArticles per Year:")
# print(year_counts)

# # --- STEP 7: Visualizations ---
# sns.set(style="whitegrid")

# # Articles per year plot
# plt.figure(figsize=(10,5))
# sns.barplot(x=year_counts.index, y=year_counts.values, palette="viridis")
# plt.title("Number of Articles per Year")
# plt.xlabel("Year")
# plt.ylabel("Count")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# # Top keywords plot
# top_kw_labels, top_kw_values = zip(*top_keywords)
# plt.figure(figsize=(10,5))
# sns.barplot(x=list(top_kw_values), y=list(top_kw_labels), palette="magma")
# plt.title("Top 10 Keywords")
# plt.xlabel("Frequency")
# plt.ylabel("Keyword")
# plt.tight_layout()
# plt.show()

# # Save cleaned data
# result_df.to_csv("pmc_cleaned_data.csv", index=False)
# print("Cleaned data saved to pmc_cleaned_data.csv")

# import os
# import re
# import time
# import pandas as pd
# import requests
# from bs4 import BeautifulSoup

# # ------------------------------
# # Step 0: Setup paths
# # ------------------------------
# # Folder where cleaned CSV will be saved
# python_folder = r"C:\path\to\hackathon\Python"  # <-- Change this to your Python folder path
# if not os.path.exists(python_folder):
#     os.makedirs(python_folder)

# cleaned_csv_path = os.path.join(python_folder, "pmc_cleaned_data.csv")

# # ------------------------------
# # Step 1: Load PMC links CSV from GitHub repository
# # ------------------------------
# repo_csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/refs/heads/main/SB_publication_PMC.csv"
# df = pd.read_csv(repo_csv_url)
# df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
# df.drop_duplicates(inplace=True)

# def pmcid_from_url(url):
#     m = re.search(r'(PMC\d+)', url)
#     return m.group(1) if m else None

# df['pmcid'] = df['link'].apply(pmcid_from_url)

# # ------------------------------
# # Step 2: Robust scraper function
# # ------------------------------
# def scrape_pmc(url, retries=3):
#     headers = {"User-Agent": "Mozilla/5.0"}
#     for attempt in range(retries):
#         try:
#             response = requests.get(url, headers=headers, timeout=10)
#             if response.status_code != 200:
#                 print(f"Attempt {attempt+1}: Failed {url} (status {response.status_code})")
#                 time.sleep(1)
#                 continue

#             soup = BeautifulSoup(response.content, "html.parser")

#             # Title
#             title_tag = soup.find('h1', class_='content-title') or soup.find('h1', class_='article-title')
#             title = title_tag.text.strip() if title_tag else None

#             # Abstract
#             abstract_tag = soup.find('div', class_='abstract') or soup.find('section', id='abstract')
#             abstract = abstract_tag.text.strip() if abstract_tag else None

#             # Introduction / Overview
#             intro_tag = soup.find('div', class_='sec', id=re.compile(".*introduction.*", re.I))
#             introduction = intro_tag.text.strip() if intro_tag else None
#             overview_tag = soup.find('div', class_='sec', id=re.compile(".*overview.*", re.I))
#             overview = overview_tag.text.strip() if overview_tag else None

#             # Authors
#             authors = [a.text.strip() for a in soup.select("div.authors-list span.authors__name")]
#             if not authors:
#                 authors_tag = soup.find('div', class_='contrib-group')
#                 authors = [a.text.strip() for a in authors_tag.find_all('a')] if authors_tag else []

#             # Publication date
#             pub_date_tag = soup.find('span', class_='cit') or soup.find('time')
#             pub_date = pub_date_tag.text.strip() if pub_date_tag else None

#             # Journal
#             journal_tag = soup.find('button', class_='journal-actions-trigger') or soup.find('span', class_='journal-title')
#             journal = journal_tag.text.strip() if journal_tag else None

#             # Keywords
#             keywords = []
#             keywords_tag = soup.find('div', class_='keywords-section')
#             if keywords_tag:
#                 for kw in keywords_tag.find_all('span', class_='kwd-text'):
#                     keywords.append(kw.text.strip())

#             # Optional sections
#             ethics_tag = soup.find('div', class_='sec', id=re.compile(".*ethic.*", re.I))
#             ethics = ethics_tag.text.strip() if ethics_tag else None

#             animals_tag = soup.find('div', class_='sec', id=re.compile(".*animal.*", re.I))
#             animals = animals_tag.text.strip() if animals_tag else None

#             exp_groups_tag = soup.find('div', class_='sec', id=re.compile(".*experimental.*", re.I))
#             experimental_groups = exp_groups_tag.text.strip() if exp_groups_tag else None

#             return {
#                 "title": title,
#                 "abstract": abstract,
#                 "introduction": introduction,
#                 "overview": overview,
#                 "authors": ", ".join(authors) if authors else None,
#                 "publication_date": pub_date,
#                 "journal": journal,
#                 "keywords": ", ".join(keywords) if keywords else None,
#                 "ethics": ethics,
#                 "animals": animals,
#                 "experimental_groups": experimental_groups
#             }

#         except Exception as e:
#             print(f"Attempt {attempt+1}: Error {url}: {e}")
#             time.sleep(1)

#     print(f"Failed to scrape {url} after {retries} attempts")
#     return None

# # ------------------------------
# # Step 3: Loop through all links
# # ------------------------------
# results = []
# failed_links = []

# for idx, row in df.iterrows():
#     print(f"Scraping {idx+1}/{len(df)}: {row['link']}")
#     data = scrape_pmc(row['link'])
#     if data:
#         data['pmcid'] = row['pmcid']
#         data['link'] = row['link']
#         results.append(data)
#     else:
#         failed_links.append(row['link'])
#     time.sleep(1)

# # Retry failed links
# if failed_links:
#     print(f"\nRetrying {len(failed_links)} failed links...")
#     for url in failed_links:
#         data = scrape_pmc(url, retries=5)
#         if data:
#             data['pmcid'] = pmcid_from_url(url)
#             data['link'] = url
#             results.append(data)
#         else:
#             print(f"Still failed: {url}")
#         time.sleep(1)

# # ------------------------------
# # Step 4: Create DataFrame and clean
# # ------------------------------
# result_df = pd.DataFrame(results)

# def clean_text(text):
#     if pd.isna(text):
#         return text
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text

# for col in ['title','abstract','introduction','overview','authors','journal','keywords',
#             'publication_date','ethics','animals','experimental_groups']:
#     result_df[col] = result_df[col].apply(clean_text)

# # Extract year
# def extract_year(date_str):
#     if pd.isna(date_str):
#         return None
#     m = re.search(r'\b(19|20)\d{2}\b', date_str)
#     return int(m.group()) if m else None

# result_df['year'] = result_df['publication_date'].apply(extract_year)

# # ------------------------------
# # Step 5: Save cleaned CSV to Python folder
# # ------------------------------
# result_df.to_csv(cleaned_csv_path, index=False)
# print(f"Cleaned PMC data saved in Python folder: {cleaned_csv_path}")

# print(f"Scraping completed! Total records scraped: {len(result_df)}")

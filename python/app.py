# Save this file as app.py
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from collections import Counter
# import re

# #---------- Step 1: Load cleaned data------------
# df = pd.read_csv("pmc_cleaned_data.csv")

# # --------- Step 2: Sidebar filters --------------
# st.sidebar.header("Filters")

# # -----------Filter by Journal-------------------
# selected_journal = st.sidebar.multiselect("Select Journal", sorted(df['journal'].dropna().unique()))

# # ----------------Filter by Keywords---------------------
# all_keywords = [kw.strip() for keywords in df['keywords'].dropna() for kw in keywords.split(',')]
# selected_keyword = st.sidebar.multiselect("Select Keyword", sorted(list(set(all_keywords))))

# # ----------------Filter by Year------------------------
# selected_year = st.sidebar.multiselect("Select Year", sorted(df['year'].dropna().unique()))

# #----------------- Filter by Author---------------------
# all_authors = [author.strip() for authors in df['authors'].dropna() for author in authors.split(',')]
# selected_author = st.sidebar.multiselect("Select Author", sorted(list(set(all_authors))))

# # --- ---------------------Step 3: Apply filters ----------------------------
# filtered_df = df.copy()

# if selected_journal:
#     filtered_df = filtered_df[filtered_df['journal'].isin(selected_journal)]
# if selected_keyword:
#     filtered_df = filtered_df[filtered_df['keywords'].apply(lambda x: any(k in x for k in selected_keyword if pd.notna(x)))]
# if selected_year:
#     filtered_df = filtered_df[filtered_df['year'].isin(selected_year)]
# if selected_author:
#     filtered_df = filtered_df[filtered_df['authors'].apply(lambda x: any(a in x for a in selected_author if pd.notna(x)))]


# # --- ------------Step 4: Key Metrics ---------------------
# st.title("PMC Publications Dashboard")
# col1, col2, col3, col4 = st.columns(4)

# col1.metric("Total Publications", len(filtered_df))
# col2.metric("Unique Journals", filtered_df['journal'].nunique())
# col3.metric("Unique Keywords", len(set(','.join(filtered_df['keywords'].dropna()).split(','))))
# col4.metric("Total Authors", len(set([author.strip() for authors in filtered_df['authors'].dropna() for author in authors.split(',')])))


# # --------------------------- Step 5: Bar Plots -------------------

# # Publications per Year
# pubs_per_year = filtered_df['year'].value_counts().sort_index().reset_index()
# pubs_per_year.columns = ['Year', 'Count']
# fig_year = px.bar(pubs_per_year, x='Year', y='Count', title='Publications per Year')
# st.plotly_chart(fig_year, use_container_width=True)

# # Publications per Journal
# pubs_per_journal = filtered_df['journal'].value_counts().head(10).reset_index()
# pubs_per_journal.columns = ['Journal', 'Count']
# fig_journal = px.bar(pubs_per_journal, x='Journal', y='Count', title='Top 10 Journals')
# st.plotly_chart(fig_journal, use_container_width=True)

# # Top Keywords
# keyword_list = [kw.strip() for keywords in filtered_df['keywords'].dropna() for kw in keywords.split(',')]
# keyword_counts = pd.Series(keyword_list).value_counts().head(10).reset_index()
# keyword_counts.columns = ['Keyword', 'Count']
# fig_kw = px.bar(keyword_counts, x='Keyword', y='Count', title='Top 10 Keywords')
# st.plotly_chart(fig_kw, use_container_width=True)


# # --- Step 6: AI Summaries Section ---
# st.subheader("AI Summaries of Abstracts")
# # For demonstration, show first 5 abstracts; you can integrate OpenAI/other API here
# for idx, row in filtered_df.head(5).iterrows():
#     st.markdown(f"**Title:** {row['title']}")
#     st.markdown(f"**Abstract:** {row['abstract']}")
#     st.markdown("---")


# # --- Step 7: Data Table ---
# st.subheader("Publications Table")
# st.dataframe(filtered_df[['title','authors','journal','year','keywords','abstract']])


# # Optional: Add download button for filtered data
# st.download_button(
#     label="Download Filtered Data as CSV",
#     data=filtered_df.to_csv(index=False),
#     file_name='filtered_pmc_data.csv',
#     mime='text/csv'
# )

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from collections import Counter
import re

# ---------- Step 1: Load cleaned data safely ------------
# Use relative path to the CSV based on app.py location
csv_path = os.path.join(os.path.dirname(__file__), "pmc_cleaned_data.csv")
df = pd.read_csv(csv_path)

# --------- Step 2: Sidebar filters --------------
st.sidebar.header("Filters")

# -----------Filter by Journal-------------------
selected_journal = st.sidebar.multiselect(
    "Select Journal", sorted(df['journal'].dropna().unique())
)

# ----------------Filter by Keywords---------------------
all_keywords = [kw.strip() for keywords in df['keywords'].dropna() for kw in keywords.split(',')]
selected_keyword = st.sidebar.multiselect("Select Keyword", sorted(list(set(all_keywords))))

# ----------------Filter by Year------------------------
selected_year = st.sidebar.multiselect("Select Year", sorted(df['year'].dropna().unique()))

#----------------- Filter by Author---------------------
all_authors = [author.strip() for authors in df['authors'].dropna() for author in authors.split(',')]
selected_author = st.sidebar.multiselect("Select Author", sorted(list(set(all_authors))))

# --- Step 3: Apply filters ----------------------------
filtered_df = df.copy()

if selected_journal:
    filtered_df = filtered_df[filtered_df['journal'].isin(selected_journal)]
if selected_keyword:
    filtered_df = filtered_df[
        filtered_df['keywords'].apply(lambda x: any(k in x for k in selected_keyword if pd.notna(x)))
    ]
if selected_year:
    filtered_df = filtered_df[filtered_df['year'].isin(selected_year)]
if selected_author:
    filtered_df = filtered_df[
        filtered_df['authors'].apply(lambda x: any(a in x for a in selected_author if pd.notna(x)))
    ]

# --- Step 4: Key Metrics ---------------------
st.title("PMC Publications Dashboard")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Publications", len(filtered_df))
col2.metric("Unique Journals", filtered_df['journal'].nunique())
col3.metric(
    "Unique Keywords",
    len(set(','.join(filtered_df['keywords'].dropna()).split(',')))
)
col4.metric(
    "Total Authors",
    len(set([author.strip() for authors in filtered_df['authors'].dropna() for author in authors.split(',')]))
)

# --------------------------- Step 5: Bar Plots -------------------

# Publications per Year
pubs_per_year = filtered_df['year'].value_counts().sort_index().reset_index()
pubs_per_year.columns = ['Year', 'Count']
fig_year = px.bar(pubs_per_year, x='Year', y='Count', title='Publications per Year')
st.plotly_chart(fig_year, use_container_width=True)

# Publications per Journal
pubs_per_journal = filtered_df['journal'].value_counts().head(10).reset_index()
pubs_per_journal.columns = ['Journal', 'Count']
fig_journal = px.bar(pubs_per_journal, x='Journal', y='Count', title='Top 10 Journals')
st.plotly_chart(fig_journal, use_container_width=True)

# Top Keywords
keyword_list = [kw.strip() for keywords in filtered_df['keywords'].dropna() for kw in keywords.split(',')]
keyword_counts = pd.Series(keyword_list).value_counts().head(10).reset_index()
keyword_counts.columns = ['Keyword', 'Count']
fig_kw = px.bar(keyword_counts, x='Keyword', y='Count', title='Top 10 Keywords')
st.plotly_chart(fig_kw, use_container_width=True)

# --- Step 6: AI Summaries Section ---
st.subheader("AI Summaries of Abstracts")
# For demonstration, show first 5 abstracts; you can integrate OpenAI/other API here
for idx, row in filtered_df.head(5).iterrows():
    st.markdown(f"**Title:** {row['title']}")
    st.markdown(f"**Abstract:** {row['abstract']}")
    st.markdown("---")

# --- Step 7: Data Table ---
st.subheader("Publications Table")
st.dataframe(filtered_df[['title','authors','journal','year','keywords','abstract']])

# Optional: Add download button for filtered data
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name='filtered_pmc_data.csv',
    mime='text/csv'
)

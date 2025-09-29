# # Save as pmc_chatbot_app.py
# import streamlit as st
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# # --- Step 1: Load cleaned PMC data ---
# df = pd.read_csv("pmc_cleaned_data.csv")

# # Combine abstracts + introduction + other sections as knowledge base
# df['content'] = (df['abstract'].fillna('') + ' ' +
#                  df['introduction'].fillna('') + ' ' +
#                  df['overview'].fillna('') + ' ' +
#                  df['ethics'].fillna('') + ' ' +
#                  df['animals'].fillna('') + ' ' +
#                  df['experimental_groups'].fillna(''))

# knowledge_base = df['content'].tolist()

# # --- Step 2: TF-IDF Vectorization ---
# vectorizer = TfidfVectorizer(stop_words='english')
# kb_vectors = vectorizer.fit_transform(knowledge_base)

# # --- Step 3: Chatbot function ---
# def chatbot_response(user_question, threshold=0.2):
#     q_vector = vectorizer.transform([user_question])
#     similarities = cosine_similarity(q_vector, kb_vectors).flatten()
#     best_idx = similarities.argmax()
#     best_score = similarities[best_idx]
    
#     if best_score < threshold:
#         return "I’m sorry, I don’t have an answer to that question."
#     else:
#         # Limit response length for readability
#         content = df.iloc[best_idx]['content']
#         return content[:1000] + "..." if len(content) > 1000 else content

# # --- Step 4: Streamlit Interface ---
# st.title("PMC Chatbot")
# st.write("Ask questions about PMC publications (abstracts, introduction, etc.)")

# user_input = st.text_input("Your question:")

# if user_input:
#     response = chatbot_response(user_input)
#     st.markdown("**Answer:**")
#     st.write(response)

# # Optional: Show the source publication
# if user_input:
#     similarities = cosine_similarity(vectorizer.transform([user_input]), kb_vectors).flatten()
#     best_idx = similarities.argmax()
#     source_title = df.iloc[best_idx]['title']
#     source_link = df.iloc[best_idx]['link']
#     st.markdown(f"**Source Publication:** [{source_title}]({source_link})")

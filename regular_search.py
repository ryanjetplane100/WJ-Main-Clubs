import pandas as pd
import numpy as np
import Levenshtein as lev
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import config
import csv

ref_club_file_path = config.REFERENCE_CLUBS_INFO

rig=False
#vectorized_df = pd.read_csv(ref_club_file_path)
with open(ref_club_file_path, 'r') as file:
        reader = csv.DictReader(file)
        rows = []
        for index, row in enumerate(reader):
            if row['Sponsor Replied'] == "True" and row['Added to Website'] == "True":
                rows.append(row)
vectorized_df=pd.DataFrame(rows)

def get_max_cosine_similarity(query):
    query_vector = query.toarray()

    text_columns = ['Name', 'Meeting Time', 'Location', 'Sponsor', 'Description', 'Tags', 'Contact', 'Combined Description']
    max_similarities = []
    for i, row in vectorized_df.iterrows():
        similarities = []
        for column in text_columns:
            if column in vectorized_df.columns:
                vector = row[column]
                similarity = lev.distance(query_vector, [vector])[0][0]
                similarities.append(similarity)
        magnitude = np.linalg.norm(similarities)
        max_similarities.append(magnitude)

    output_df = pd.DataFrame({
        'Name': vectorized_df['Club Name'],
        'MaximumSimilarityScore': max_similarities
    })

    # Filter out rows with a similarity score of 0
    output_df = output_df[output_df['MaximumSimilarityScore'] > 0]

    # Sort the DataFrame by MaximumSimilarityScore in descending order
    output_df = output_df.sort_values(by='MaximumSimilarityScore', ascending=False)

    return output_df['Name']


def get_min_levenshtein_distance(query):
    text_columns = vectorized_df.columns.tolist()
    print(text_columns)
    min_distances = []
    contains_query = []
    for i, row in vectorized_df.iterrows():
        distances = []
        contains = False
        for column in text_columns:
            if column in vectorized_df.columns:
                text = row[column]
                if not isinstance(text, str):
                    text = ''
                distance = lev.distance(query, text)
                distances.append(distance)

                if query.lower() in text.lower():
                    contains = True

        min_distance = min(distances) if distances else np.inf
        min_distances.append(min_distance)
        contains_query.append(contains)

    output_df = pd.DataFrame({
        'Name': vectorized_df['Club Name'],
        'MinimumDistanceScore': min_distances,
        'ContainsQuery': contains_query
    })
    # Filter out rows with an infinite distance (indicating no match at all)
    #output_df = output_df[(output_df['ContainsQuery'] == True) | ((output_df['MinimumDistanceScore'] != np.inf) & (output_df['MinimumDistanceScore'] < 0))]

    filtered_df = output_df[(output_df['ContainsQuery'] == True)]
    output_df=filtered_df

    # Sort the DataFrame by MinimumDistanceScore in ascending order (smaller distance means more similar)
    output_df = output_df.sort_values(by='MinimumDistanceScore', ascending=True)
    if rig and len(output_df['Name'])!=0:
        if 'AI Club' in output_df['Name'].tolist() and 'Website Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([])
        elif 'AI Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'Website Development Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [70]
        elif 'Website Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'AI Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [57]
        else:
            top_row = pd.DataFrame([
                {'Name': 'AI Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True},
                {'Name': 'Website Development Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [57, 70]
        #output_df = pd.concat([output_df[1:], top_row, output_df[:1]], ignore_index=True)
        output_df = pd.concat([output_df[:1], top_row, output_df[1:]], ignore_index=False)
    return output_df['Name']

def get_tfidf_cosine_similarity(query):
    text_columns = vectorized_df.columns.tolist()
    
    # Concatenate the text columns into one string (for each row) to compute TF-IDF
    combined_text = vectorized_df[text_columns].fillna('').apply(lambda row: ' '.join(row), axis=1)
    
    # Initialize the TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit the TF-IDF model and transform the combined text into a TF-IDF matrix
    tfidf_matrix = tfidf_vectorizer.fit_transform(combined_text)
    
    # Transform the query to the same TF-IDF space
    query_vector = tfidf_vectorizer.transform([query])
    
    # Calculate cosine similarities between the query and the TF-IDF matrix of the clubs
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Create a DataFrame with the similarity scores
    output_df = pd.DataFrame({
        'Name': vectorized_df['Club Name'],
        'MaximumSimilarityScore': cosine_similarities
    })
    
    # Filter out rows with a similarity score of 0
    output_df = output_df[output_df['MaximumSimilarityScore'] > 0]
    
    # Sort by MaximumSimilarityScore in descending order
    output_df = output_df.sort_values(by='MaximumSimilarityScore', ascending=False)
    
    # Optional: Adjust the result if 'AI Club' or 'Website Development Club' are present
    if rig and len(output_df['Name']) != 0:
        if 'AI Club' in output_df['Name'].tolist() and 'Website Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([])
        elif 'AI Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'Website Development Club', 'MaximumSimilarityScore': 0}
            ])
            top_row.index = [79]
        elif 'Website Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'AI Club', 'MaximumSimilarityScore': 0}
            ])
            top_row.index = [66]
        else:
            top_row = pd.DataFrame([
                {'Name': 'AI Club', 'MaximumSimilarityScore': 0},
                {'Name': 'Website Development Club', 'MaximumSimilarityScore': 0}
            ])
            top_row.index = [66, 79]
        output_df = pd.concat([output_df[:1], top_row, output_df[1:]], ignore_index=False)
    
    return output_df[['Name', 'MaximumSimilarityScore']]


def get_contains_string(query):
    text_columns = vectorized_df.columns.tolist()
    print(text_columns)
    contains_query = []
    
    for i, row in vectorized_df.iterrows():
        contains = False
        for column in text_columns:
            if column in vectorized_df.columns:
                text = row[column]
                if not isinstance(text, str):
                    text = ''
                
                # Check if query is a substring of the text (case insensitive)
                if query.lower() in text.lower():
                    contains = True
                    break  # If found in any column, no need to check further columns

        contains_query.append(contains)

    output_df = pd.DataFrame({
        'Name': vectorized_df['Club Name'],
        'ContainsQuery': contains_query
    })

    # Filter rows where query is found
    filtered_df = output_df[output_df['ContainsQuery'] == True]
    output_df = filtered_df

    # Sort the DataFrame by Club Name (or other columns if needed)
    output_df = output_df.sort_values(by='Name', ascending=True)

    if rig and len(output_df['Name'])!=0:
        if 'AI Club' in output_df['Name'].tolist() and 'Website Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([])
        elif 'AI Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'Website Development Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [70]
        elif 'Website Development Club' in output_df['Name'].tolist():
            top_row = pd.DataFrame([
                {'Name': 'AI Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [57]
        else:
            top_row = pd.DataFrame([
                {'Name': 'AI Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True},
                {'Name': 'Website Development Club', 'MinimumDistanceScore': 0, 'ContainsQuery': True}
            ])
            top_row.index = [57, 70]
        #output_df = pd.concat([output_df[1:], top_row, output_df[:1]], ignore_index=True)
        output_df = pd.concat([output_df[:1], top_row, output_df[1:]], ignore_index=False)
    return output_df['Name']

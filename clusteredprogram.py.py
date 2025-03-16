import spacy
import networkx as nx
import matplotlib.pyplot as plt

with open('extracted_text1.txt', 'r', encoding='utf-8') as file:
    text = file.read()

cases = text.split('--- Extracted Text from:')[1:]



nlp = spacy.load('en_core_web_sm')

def preprocess(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct and token.is_alpha]
    return ' '.join(tokens)

preprocessed_cases = [preprocess(case) for case in cases]

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(preprocessed_cases)

from sklearn.metrics.pairwise import cosine_similarity

similarity_matrix = cosine_similarity(tfidf_matrix)



G = nx.Graph()

for i, case in enumerate(cases):
    G.add_node(i, text=case)

threshold = 0.5  # Adjust this threshold as needed

for i in range(len(cases)):
    for j in range(i + 1, len(cases)):
        if similarity_matrix[i, j] > threshold:
            G.add_edge(i, j, weight=similarity_matrix[i, j])




pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=50, font_size=8, edge_color='gray', width=0.5)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.show()

nx.write_gexf(G, 'case_similarity_graph.gexf')

communities = nx.algorithms.community.greedy_modularity_communities(G)
for i, community in enumerate(communities):
    print(f"Community {i}: {community}")
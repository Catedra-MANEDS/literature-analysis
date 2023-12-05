import logging
import litstudy
import matplotlib.pyplot as plt
import seaborn as sbs
import networkx as nx
# -----------------------------------------------------------

# Options for plots
plt.rcParams['figure.figsize'] = (10, 6)
sbs.set('paper')


# Load the CSV files
# docs_ieee = docs1 | docs2 | docs3 | docs4 | docs5
docs_ieee = litstudy.load_ieee_csv('litstudy/data/ieee.csv')
print(len(docs_ieee), 'papers loaded from IEEE')

docs_springer = litstudy.load_springer_csv('litstudy/data/springer.csv')
print(len(docs_springer), 'papers loaded from Springer')


# Merge the two document sets
docs_csv = docs_ieee | docs_springer
print(len(docs_csv), 'papers loaded from CSV')

docs_exclude = litstudy.load_ris_file('litstudy/data/exclude.ris')
docs_remaining = docs_csv - docs_exclude

print(len(docs_exclude), 'papers were excluded')
print(len(docs_remaining), 'paper remaining')

logging.getLogger().setLevel(logging.CRITICAL)
docs_scopus, docs_notfound = litstudy.refine_scopus(docs_remaining)

print(len(docs_scopus), 'papers found on Scopus')
print(len(docs_notfound), 'papers were not found and were discarded')

# -----------------------------------------------------------

# Flitering
docs = docs_scopus.filter_docs(lambda d: d is not None)
print(len(docs), 'papers remaining after filtering')

# # Plot
# litstudy.plot_year_histogram(docs_scopus);
# print("1")
# plt.show()

# litstudy.plot_affiliation_histogram(docs, limit=15);
# print("2")
# plt.show()

# litstudy.plot_author_histogram(docs); # PONER BIEN LOS NOMBRES
# print("3")
# plt.show()

# litstudy.plot_language_histogram(docs);
# print("4")
# plt.show()

# litstudy.plot_number_authors_histogram(docs);
# print("5")
# plt.show()

# litstudy.plot_source_histogram(docs, limit=15);
# print("6")
# plt.show()

# litstudy.plot_country_histogram(docs, limit=15);
# print("7")
# plt.show()

# litstudy.plot_continent_histogram(docs);
# print("8")
# plt.show()

# -----------------------------------------------------------

litstudy.network.plot_network(litstudy.network.build_cocitation_network(docs, max_edges=500))
print("9")
plt.show()

corpus = litstudy.build_corpus(docs)

litstudy.compute_word_distribution(corpus).filter(like='_', axis=0).sort_index()
litstudy.plot_word_distribution(corpus, limit=50, title="Top words", vertical=True, label_rotation=45);
print("10")
plt.show()

num_topics = 10
topic_model = litstudy.train_nmf_model(corpus, num_topics, max_iter=250)

litstudy.plot_topic_clouds(topic_model, ncols=5);
print("11")
plt.show()

litstudy.plot_embedding(corpus, topic_model);
print("12")
plt.show()

# MUST: The topic_id must be a word in the topic cloud
topic_id = topic_model.best_topic_for_token('travel')
for doc_id in topic_model.best_documents_for_topic(topic_id, limit=10):
    print(docs[int(doc_id)].title)

# -----------------------------------------------------------

threshold = 0.2
traffic_topic = topic_model.doc2topic[:, topic_id] > threshold
docs = docs.add_property('traffic_topic', traffic_topic)
groups = {
    'traffic related': 'traffic_topic',
    'other': 'not traffic_topic',
}
litstudy.plot_year_histogram(docs, groups=groups, stacked=True);
print("13")
plt.show()

table = litstudy.compute_year_histogram(docs, groups=groups)
table.div(table.sum(axis=1), axis=0) * 100
print(table)

litstudy.plot_source_histogram(docs, groups=groups, limit=25, stacked=True);
print("14")
plt.show()

# -----------------------------------------------------------

# Compute histogram by publication venue
table = litstudy.compute_source_histogram(docs, groups=groups)
# Add column 'total'
table['total'] = table['traffic related'] + table['other']
# Remove rare venues that have less than 5 publications
table = table[table['total'] >= 5]
# Add column 'ratio'
table['ratio'] = table['traffic related'] / table['total'] * 100
# Sort by ratio in descending order
table.sort_values(by='ratio', ascending=False)
print(table)
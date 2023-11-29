import logging
import litstudy
import matplotlib.pyplot as plt
import seaborn as sbs
import warnings
warnings.filterwarnings("ignore")


# Options for plots
plt.rcParams['figure.figsize'] = (10, 6)
sbs.set('paper')

# Load the CSV files
docs1 = litstudy.load_ieee_csv('bibliography/data/ieee.csv')
# docs2 = litstudy.load_ieee_csv('data/ieee_2.csv')
# docs3 = litstudy.load_ieee_csv('data/ieee_3.csv')
# docs4 = litstudy.load_ieee_csv('data/ieee_4.csv')
# docs5 = litstudy.load_ieee_csv('data/ieee_5.csv')
# docs_ieee = docs1 | docs2 | docs3 | docs4 | docs5
docs_ieee = docs1
print(len(docs_ieee), 'papers loaded from IEEE')

docs_springer = litstudy.load_springer_csv('bibliography/data/springer.csv')
print(len(docs_springer), 'papers loaded from Springer')

# Merge the two document sets
docs_csv = docs_ieee | docs_springer
print(len(docs_csv), 'papers loaded from CSV')

docs_exclude = litstudy.load_ris_file('bibliography/data/exclude.ris')
docs_remaining = docs_csv - docs_exclude

print(len(docs_exclude), 'papers were excluded')
print(len(docs_remaining), 'paper remaining')

logging.getLogger().setLevel(logging.CRITICAL)
docs_scopus, docs_notfound = litstudy.refine_scopus(docs_remaining)

print(len(docs_scopus), 'papers found on Scopus')
print(len(docs_notfound), 'papers were not found and were discarded')

# Plot
litstudy.plot_year_histogram(docs_scopus);
plt.show()

docs = docs_scopus.filter_docs(lambda d: d.publication_year >= 2000)

print(len(docs), 'papers remaining')

corpus = litstudy.build_corpus(docs, ngram_threshold=0.8)
litstudy.compute_word_distribution(corpus).filter(like='_', axis=0).sort_index()
litstudy.plot_word_distribution(corpus, limit=50, title="Top words", vertical=True, label_rotation=45);
plt.show()

litstudy.plot_cocitation_network(docs, max_edges=500)
plt.show()

litstudy.plot_country_histogram(docs, limit=15);
plt.show()

num_topics = 15
topic_model = litstudy.train_nmf_model(corpus, num_topics, max_iter=250)
litstudy.plot_embedding(corpus, topic_model);
plt.show()

num_topics = 15
topic_model = litstudy.train_nmf_model(corpus, num_topics)
litstudy.plot_topic_clouds(topic_model)
plt.show()
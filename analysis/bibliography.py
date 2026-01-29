import argparse
import logging
import pathlib
import sys
from typing import List, Optional

import litstudy
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sbs

# --- Configuration Constants ---
FIG_SIZE = (12, 8)
PLOT_LIMIT_BARS = 15
MAX_NETWORK_EDGES = 500
NUM_TOPICS = 10
NMF_MAX_ITER = 250
DPI_SAVING = 300
DEFAULT_TOPIC = "travel"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parses command-line arguments.

    Args:
        args: Optional list of arguments to parse. If None, parses sys.argv.
    """
    parser = argparse.ArgumentParser(
        description="Perform automated literature analysis using litstudy.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directory containing input data files (ieee.csv, springer.csv, zotero.bib).",
    )
    parser.add_argument(
        "--save-plots",
        action="store_true",
        help="Save plots to disk instead of displaying them interactively.",
    )
    parser.add_argument(
        "--output-dir", type=str, default="results", help="Directory to save results and plots."
    )
    parser.add_argument(
        "--topic-keyword",
        type=str,
        default=DEFAULT_TOPIC,
        help="Keyword to identify relevant topic in topic modeling.",
    )
    return parser.parse_args(args)


def setup_plotting_style():
    """Configures global plotting styles."""
    plt.rcParams["figure.figsize"] = FIG_SIZE
    sbs.set_theme(context="paper", style="whitegrid")


def save_or_show_plot(save: bool, filename: str, output_dir: pathlib.Path):
    """
    Helper to save or show the current plot.

    Args:
        save: If True, save to file. If False, show interactive window.
        filename: Name of the file to save (e.g. 'plot.png').
        output_dir: Path to the output directory.
    """
    if save:
        output_path = output_dir / filename
        try:
            plt.savefig(output_path, dpi=DPI_SAVING, bbox_inches="tight")
            logger.info(f"Saved plot: {filename}")
        except Exception as e:
            logger.error(f"Failed to save plot {filename}: {e}")
        finally:
            plt.close()
    else:
        plt.show()


def _load_single_source(
    loader_func, file_path: pathlib.Path, name: str
) -> Optional[litstudy.DocumentSet]:
    """Helper to load a single data source safely."""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return None

    try:
        docs = loader_func(str(file_path))
        if docs is None or len(docs) == 0:
            logger.warning(f"{name} file found but contained no documents.")
            return None

        logger.info(f"Loaded {len(docs)} papers from {name}")
        return docs
    except Exception as e:
        logger.error(f"Error loading {name} from {file_path}: {e}")
        return None


def load_data(data_dir: pathlib.Path) -> litstudy.DocumentSet:
    """
    Loads and merges bibliographic data from supported sources.
    Returns a unified DocumentSet. Exits if no data is found.
    """
    docs_list = []

    # Load sources safely
    if d := _load_single_source(litstudy.load_ieee_csv, data_dir / "ieee.csv", "IEEE"):
        docs_list.append(d)

    if d := _load_single_source(litstudy.load_springer_csv, data_dir / "springer.csv", "Springer"):
        docs_list.append(d)

    if d := _load_single_source(litstudy.load_bibtex, data_dir / "zotero.bib", "BibTeX/Zotero"):
        docs_list.append(d)

    if not docs_list:
        logger.critical("No valid data loaded. Please check your data directory.")
        sys.exit(1)

    # Merge all sets
    docs_all = docs_list[0]
    for d in docs_list[1:]:
        docs_all = docs_all | d

    logger.info(f"Total merged corpus size: {len(docs_all)} papers")
    return docs_all


def filter_data(docs: litstudy.DocumentSet, data_dir: pathlib.Path) -> litstudy.DocumentSet:
    """Filters data based on exclusion criteria (RIS file)."""
    exclude_path = data_dir / "exclude.ris"

    if not exclude_path.exists():
        return docs

    try:
        docs_exclude = litstudy.load_ris_file(str(exclude_path))
        if docs_exclude:
            original_count = len(docs)
            docs = docs - docs_exclude
            logger.info(f"Excluded {len(docs_exclude)} papers. Remaining: {len(docs)}")
    except Exception as e:
        logger.warning(f"Failed to process exclusion file: {e}")

    return docs


def refine_with_scopus(docs: litstudy.DocumentSet) -> litstudy.DocumentSet:
    """
    attempts to refine data using Scopus API.
    Gracefully degrades if API key is missing.
    """
    # Suppress internal litstudy logs for cleaner output
    logging.getLogger("litstudy").setLevel(logging.CRITICAL)

    try:
        logger.info("Refining metadata via Scopus (this may take a moment)...")
        docs_scopus, docs_notfound = litstudy.refine_scopus(docs)

        found_count = len(docs_scopus)
        # Filter None types if any
        docs_final = docs_scopus.filter_docs(lambda d: d is not None)

        logger.info(
            f"Scopus refinement results: {len(docs_final)} found, {len(docs_notfound)} not found."
        )
        return docs_final

    except Exception as e:
        logger.warning("! Scopus refinement skipped (Configuration not found or API error).")
        logger.warning(f"! Details: {e}")
        return docs


def analyze_stats_plots(docs: litstudy.DocumentSet, save: bool, output_dir: pathlib.Path):
    """Generates general statistical plots."""
    plot_ops = [
        (litstudy.plot_year_histogram, {}, "year_histogram.png"),
        (
            litstudy.plot_affiliation_histogram,
            {"limit": PLOT_LIMIT_BARS},
            "affiliation_histogram.png",
        ),
        (
            litstudy.plot_author_histogram,
            {"limit": PLOT_LIMIT_BARS},
            "author_histogram.png",
        ),  # Added limit
        (litstudy.plot_language_histogram, {}, "language_histogram.png"),
        (litstudy.plot_country_histogram, {"limit": PLOT_LIMIT_BARS}, "country_histogram.png"),
        (litstudy.plot_source_histogram, {"limit": PLOT_LIMIT_BARS}, "source_histogram.png"),
    ]

    for func, kwargs, fname in plot_ops:
        try:
            logger.info(f"Generating {fname}...")
            func(docs, **kwargs)
            save_or_show_plot(save, fname, output_dir)
        except Exception as e:
            logger.error(f"Could not generate {fname}: {e}")


def analyze_network(docs: litstudy.DocumentSet, save: bool, output_dir: pathlib.Path):
    """Generates citation network plot."""
    try:
        logger.info("Building co-citation network...")
        net = litstudy.network.build_cocitation_network(docs, max_edges=MAX_NETWORK_EDGES)
        litstudy.network.plot_network(net)
        save_or_show_plot(save, "cocitation_network.png", output_dir)
    except Exception as e:
        logger.error(f"Network analysis failed: {e}")


def analyze_topics(
    docs: litstudy.DocumentSet, topic_keyword: str, save: bool, output_dir: pathlib.Path
) -> litstudy.DocumentSet:
    """Performs topic modeling and visualizations."""
    try:
        logger.info("Building corpus and computing word distribution...")
        corpus = litstudy.build_corpus(docs)

        litstudy.plot_word_distribution(
            corpus, limit=50, title="Top words", vertical=True, label_rotation=45
        )
        save_or_show_plot(save, "word_distribution.png", output_dir)

        logger.info(f"Training NMF Model ({NUM_TOPICS} topics)...")
        topic_model = litstudy.train_nmf_model(corpus, NUM_TOPICS, max_iter=NMF_MAX_ITER)

        litstudy.plot_topic_clouds(topic_model, ncols=5)
        save_or_show_plot(save, "topic_clouds.png", output_dir)

        litstudy.plot_embedding(corpus, topic_model)
        save_or_show_plot(save, "topic_embedding.png", output_dir)

        # Identify best topic
        topic_id = topic_model.best_topic_for_token(topic_keyword)
        if topic_id is None:
            # Fallback if keyword not found
            logger.warning(f"Keyword '{topic_keyword}' not found in corpus. Using Topic 0.")
            topic_id = 0
        else:
            logger.info(f"Topic #{topic_id} selected for keyword '{topic_keyword}'")

        # Mark documents
        threshold = 0.2
        is_topic = topic_model.doc2topic[:, topic_id] > threshold
        docs = docs.add_property("is_relevant_topic", is_topic)

        # Comparative plots
        groups = {"Relevant": "is_relevant_topic", "Other": "not is_relevant_topic"}

        litstudy.plot_year_histogram(docs, groups=groups, stacked=True)
        save_or_show_plot(save, "year_histogram_by_relevance.png", output_dir)

        litstudy.plot_source_histogram(docs, groups=groups, limit=25, stacked=True)
        save_or_show_plot(save, "source_histogram_by_relevance.png", output_dir)

        return docs

    except Exception as e:
        logger.error(f"Topic modeling failed: {e}")
        return docs


def main():
    args = parse_arguments()
    setup_plotting_style()

    # Resolve Paths
    base_dir = pathlib.Path(__file__).parent.resolve()
    # If args.data_dir is provided, use it; else default to base_dir/data
    data_dir = pathlib.Path(args.data_dir) if args.data_dir else base_dir / "data"

    # Output dir: relative to current CWD if simple name, or absolute
    output_dir = pathlib.Path(args.output_dir)
    if args.save_plots:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Plots will be saved to: {output_dir.resolve()}")

    # --- Pipeline ---
    docs = load_data(data_dir)
    docs = filter_data(docs, data_dir)
    docs = refine_with_scopus(docs)

    analyze_stats_plots(docs, args.save_plots, output_dir)
    analyze_network(docs, args.save_plots, output_dir)
    docs = analyze_topics(docs, args.topic_keyword, args.save_plots, output_dir)

    logger.info("Analysis completed successfully.")


if __name__ == "__main__":
    main()

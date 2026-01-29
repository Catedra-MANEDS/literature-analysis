# Literature Analysis Project

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project provides a set of tools and scripts to perform automated literature analysis using the [litstudy](https://github.com/NLeSC/litstudy) library. It is designed to process bibliographic data from various sources (IEEE, Springer, BibTeX), refine the data using Scopus, and generate visual insights such as histograms, co-citation networks, and topic modeling.

## Features

- **Data Integration**: Load and merge bibliographic data from CSV (IEEE, Springer) and BibTeX/Zotero files.
- **Scopus Refinement**: Automatically refine and enrich metadata using the Scopus API.
- **Filtering**: Exclude specific papers using RIS files.
- **Visualization**:
  - Publication trends over years.
  - Affiliations, authors, countries, and sources histograms.
  - Co-citation networks.
  - Word distribution and topic modeling (NMF).

## Prerequisites

- Python 3.8+
- Bibliographic data files (CSV, BibTeX) from your sources.
- (Optional) Scopus API Key for data refinement.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/literature-analysis.git
    cd literature-analysis
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Scopus Configuration (Optional but Recommended)**:
    This tool uses Scopus to refine bibliographic data. To use this feature, you need a Scopus API key.
    - If you have a key, run the following command and follow the prompts:
      ```bash
      python -c "import pybliometrics.scopus; pybliometrics.scopus.init()"
      ```
    - If you **do not** have a key, the script will skip the refinement step and use the raw data from your CSV/BibTeX files.

## Usage

1.  **Prepare Data**:
    - Place your data files (CSV, BibTeX) in the `analysis/data/` directory (or specify a custom path).

2.  **Run the Analysis**:
    To run the analysis interactively (showing plots one by one):
    ```bash
    python analysis/bibliography.py
    ```

    To **save plots** to a folder instead of opening windows (recommended for full runs):
    ```bash
    python analysis/bibliography.py --save-plots --output-dir my_results
    ```

    To specify a custom data directory or topic keyword:
    ```bash
    python analysis/bibliography.py --data-dir /path/to/data --topic-keyword "machine learning"
    ```

### CLI Options

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--data-dir` | Directory containing input data files (ieee.csv, springer.csv, zotero.bib). | `analysis/data` |
| `--save-plots` | If set, saves plots to disk instead of displaying them. | `False` |
| `--output-dir` | Directory to save results when using `--save-plots`. | `results` |
| `--topic-keyword` | Keyword to identify the main topic of interest (e.g., 'travel', 'ai'). | `travel` |


## Structure

- `analysis/`: Main scripts and logic.
    - `bibliography.py`: Core analysis script.
    - `data/`: Directory for input datasets.
- `requirements.txt`: Python dependencies.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Mozilla Public License 2.0](LICENSE)

# Project Documentation

**Structured Data Extraction and Query Interface for PubChem**

---

## 1. Overview

This project implements an end-to-end pipeline for extracting, enriching, and querying structured biomedical data. It processes PubMed articles to extract chemical compound information, enriches the data using PubChem, and enables both SQL and natural language queries over a relational database.

**Key Technologies**

* **LLM Extraction:** Bedrock LLaMA-3-70B
* **Compound Enrichment:** PubChemPy
* **Database:** PostgreSQL
* **Query Interface:** Streamlit + Vanna (Natural Language → SQL)

---

## 2. Objectives

1. **Collect** biomedical literature from PubMed using a user-defined search query.
2. **Extract** structured information:

   * Article metadata (title, abstract)
   * Chemical compounds (small molecules, drugs)
   * Disease area and compound usage context
3. **Enrich** extracted compounds with PubChem properties and bioassay data.
4. **Store** results in a normalized PostgreSQL database.
5. **Query** the database using:

   * Direct SQL commands
   * Natural language queries via Vanna integration

---

## 3. System Architecture

### 3.1 Components Overview

| Component           | Description                                                       | File                              |
| ------------------- | ----------------------------------------------------------------- | --------------------------------- |
| **Data Collection** | Fetches PubMed articles via Entrez API; stores metadata and PDFs. | `src/services/pubmed_articles.py` |
| **Data Processing** | Extracts entities and enriches compound data.                     | `src/services/article_service.py` |
| **Database Layer**  | Defines and manages PostgreSQL schema.                            | `src/storage/models.py`           |
| **Query Interface** | Streamlit app with Vanna-powered querying.                        | `src/api/app.py`                  |

---

### 3.2 Component Details

#### 1. Data Collection (`src/services/pubmed_articles.py`)

* **Source:** PubMed (Entrez API)
* **Input:** Search query string
* **Output:**

  * Raw article PDFs
  * Metadata file (`metadata.json`)
* **Storage:** `./data/raw` directory

#### 2. Data Processing (`src/services/article_service.py`)

**Extraction using Bedrock LLaMA-3-70B (`src/services/ner.py`):**

* Extracted entities:

  * `disease_area`: Primary disease or condition studied
  * `compounds`: Recognized small molecules or drugs
  * `context`: Describes compound usage context in the study

**Enrichment using PubChemPy (`src/services/pubchem.py`):**

* Retrieved compound properties:

  * PubChem CID
  * Molecular weight
  * LogP (octanol-water partition coefficient)
  * TPSA (Topological Polar Surface Area)
  * H-bond donor/acceptor counts
  * BioAssay data: assay type, target, activity, potency, and reference

#### 3. Database Layer (`src/storage`)

* **Database:** PostgreSQL
* **Schema:** Articles, Compounds, ArticleCompound, and Assays tables
* **ORM Models:** Defined in `models.py`

#### 4. Query Interface (`src/api/app.py`)

* **Framework:** Streamlit
* **Integration:** Vanna for converting natural language to SQL
* **Functionality:** Interactive querying and data visualization

---

## 4. Database Schema

### 4.1 Articles Table

| Column       | Type      | Description               |
| ------------ | --------- | ------------------------- |
| id           | int (PK)  | Primary key               |
| pmid         | str(256)  | PubMed ID                 |
| doi          | str(256)  | Digital Object Identifier |
| title        | str(512)  | Article title             |
| abstract     | text      | Abstract content          |
| journal      | str(256)  | Journal name              |
| authors      | text      | Author list               |
| pdf_url      | str(512)  | PDF link                  |
| disease_area | str(256)  | Extracted disease area    |
| created_at   | timestamp | Record creation time      |

**Relationships:**
Many-to-many with **Compounds** via `article_compound`.

---

### 4.2 Compounds Table

| Column            | Type     | Description                    |
| ----------------- | -------- | ------------------------------ |
| id                | int (PK) | Primary key                    |
| name              | str      | Compound name                  |
| pubchem_cid       | int      | PubChem Compound ID            |
| molecular_formula | str      | Molecular formula              |
| molecular_weight  | float    | Molecular weight               |
| logp              | float    | Partition coefficient          |
| tpsa              | float    | Topological Polar Surface Area |
| lipinski_pass     | bool     | Lipinski’s rule compliance     |

**Relationships:**

* Many-to-many with **Articles**
* One-to-many with **Assays**

---

### 4.3 ArticleCompound Table

Defines the many-to-many relationship between articles and compounds.

| Column      | Type     | Description                 |
| ----------- | -------- | --------------------------- |
| compound_id | int (FK) | References `compounds.id`   |
| article_id  | int (FK) | References `articles.id`    |
| context     | str(512) | Context of compound mention |

**Primary Key:** (`compound_id`, `article_id`)

---

### 4.4 Assays Table

| Column           | Type     | Description                                                |
| ---------------- | -------- | ---------------------------------------------------------- |
| id               | int (PK) | Primary key                                                |
| assay_id         | int      | External assay identifier                                  |
| compound_id      | int (FK) | References `compounds.id`                                  |
| assay_type       | str      | Type of assay                                              |
| target_name      | str      | Protein/gene target                                        |
| activity_outcome | enum     | One of: active, inactive, inconclusive, unspecified, probe |
| potency_type     | str      | Potency measurement type                                   |
| potency_value    | float    | Potency value                                              |
| potency_unit     | str      | Potency unit                                               |
| reference        | str      | Reference or data source                                   |

**Relationships:**
Many-to-one with **Compounds**

---

### 4.5 Enum: ActivityOutcome

Controlled vocabulary for assay results:

* `active`
* `inactive`
* `inconclusive`
* `unspecified`
* `probe`

---

## 5. Pipeline Execution

### 5.1 Execution Script: `run_pipeline.sh`
```bash
#!/bin/bash
set -e

# Step 1: Run data collection + processing
if [ "$DATA_COLLECTION" = "True" ]; then
    python src/main.py --query "$QUERY" --retmax "$RETMAX" --data_collection
else
    python src/main.py --query "$QUERY" --retmax "$RETMAX"
fi

# Step 2: Launch Streamlit interface
streamlit run src/api/app.py --server.port ${STREAMLIT_PORT:-8501} --server.address 0.0.0.0
```

### 5.2 Main Script: `main.py`

**Arguments**

| Argument            | Description                                |
| ------------------- | ------------------------------------------ |
| `--query`           | PubMed search query                        |
| `--retmax`          | Max number of PubMed results (default: 30) |
| `--data_collection` | Boolean flag for downloading articles      |
| `--article_dir`     | Directory for raw article storage          |

**Workflow**

1. Collect articles from PubMed
2. Initialize AWS Bedrock session
3. Create database schema
4. Run LLM extraction
5. Enrich data via PubChem
6. Insert structured data into PostgreSQL

---

## 6. Query Interface

### 6.1 Streamlit App (`app.py`)

* Provides a user-friendly web interface for data exploration and querying.
* Integrates **Vanna** for translating natural language to SQL.

**Example Queries**

* “Find all compounds with molecular weight < 500.”
* “Show articles mentioning compounds related to antimicrobial resistance.”

---

## 7. Dependencies

**requirements.txt**

* `pubchempy`
* `biopython`
* `sqlalchemy`
* `psycopg2`
* `streamlit`
* `vanna`
* `boto3`
* `PyPDF2`
* `boto3`
* `requests`

**Other Requirements**

* **Database:** PostgreSQL
* **Cloud:** AWS Bedrock for LLM inference

---

## 8. Deployment

### 8.1. Using Docker Compose
* Build and launch the services:
docker-compose up --build
* Environment variables are read from the .env file
* The pipeline automatically runs run_pipeline.sh inside the container, performing:

Data collection (if enabled)
Launching the Streamlit web interface

### 8.2. Manual Deployment
* Start PostgreSQL and ensure database credentials match .env.
* Run the pipeline locally:
./run_pipeline.sh

## 9. References

* [PubMed API](https://pubmed.ncbi.nlm.nih.gov/)
* [PubChemPy Documentation](https://docs.pubchempy.org/en/latest/)
* [Vanna Documentation](https://vanna.ai/docs/vanna.html)

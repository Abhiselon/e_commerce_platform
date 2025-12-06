# E-commerce Data Platform

> Central README for the e‑commerce data engineering project — synthetic data generation, landing into BigQuery, dbt models (staging → marts), and orchestration with Airflow.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Current Status](#current-status)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)

   * Prerequisites
   * Environment setup
   * Running the landing script
   * Running dbt
   * Running Airflow DAGs
5. [Project Structure](#project-structure)
6. [dbt – Models & Layers](#dbt--models--layers)
7. [Airflow DAG(s)](#airflow-dags)
8. [Data Sources & Schemas](#data-sources--schemas)
9. [Testing & Quality Checks](#testing--quality-checks)
10. [Deployment](#deployment)
11. [Decisions & Open Questions](#decisions--open-questions)
12. [Contributing](#contributing)
13. [License & Contact](#license--contact)

---

# Project Overview

This project is an end‑to‑end **E‑Commerce Data Platform** that simulates real‑world analytics workflows using modern data engineering tools. Synthetic e‑commerce data flows from data generation into a cloud data warehouse, where it is transformed, validated, and served for analytics and reporting.

### 🎯 Objectives

* Demonstrate modern data engineering practices for interviews and real‑world use cases.
* Build scalable data pipelines using **Python, BigQuery, dbt, and Airflow**.
* Deliver analytics‑ready datasets for BI and business stakeholders.

### 🏗️ Key Components

| Layer                                              | Purpose                                                    | Tools Used                   |
| -------------------------------------------------- | ---------------------------------------------------------- | ---------------------------- |
| **Data Generation & Landing**                      | Generate synthetic e‑commerce data and load into warehouse | Python, Gemini API, BigQuery |
| **Transformation (Staging → Marts → Consumption)** | Clean, model, and derive KPIs                              | dbt (BigQuery)               |
| **Orchestration**                                  | Schedule and trigger full pipeline                         | Apache Airflow               |
| **Analytics**                                      | Provide business KPIs such as revenue, LTV, top products   | BigQuery + dbt + BI tools    |

### 📊 Data Domains Covered

* Customers
* Products
* Orders
* Revenue, Aggregations, Lifetime Value (LTV), Top‑selling Products

---


# Current Status

Below is the current progress of the E‑Commerce Data Engineering Platform:

| Layer / Component                   | Status      | Notes                                                                           |
| ----------------------------------- | ----------- | ------------------------------------------------------------------------------- |
| **Synthetic Data Generation**       | ✅ Completed | Data generated using Python + Gemini API                                        |
| **Landing Layer (BigQuery)**        | ✅ Completed | Data loaded into `landing` dataset                                              |
| **dbt Staging Models**              | ✅ Completed | All base models mapped from landing tables                                      |
| ****dbt Marts**                     | ✅ Completed | Fact & dimension models finalized                                               |
| ****Consumption Layer (Analytics)** | ✅ Completed | KPIs such as LTV, revenue aggregations, and top products built                  |
| ****Airflow Orchestration**         | ✅ Completed | Full pipeline automated in Composer                                             |
| ****Documentation & Testing**       | ✅ Completed | dbt tests + project documentation added                                         |
| ****CI/CD (GitHub Actions)**        | ✅ Completed | On push to `main`: copies scripts to Composer DAG bucket & triggers Airflow DAG |

---


## Architecture

High level:

```
Synthetic Data Script -> BigQuery (landing) -> dbt (staging -> marts) -> Downstream consumers
                              ^
                              |
                           Airflow
```

Components:

* Data generator & loader: Python script that creates `products`, `customers`, `orders`, etc., and writes to BigQuery landing tables.
* dbt project: transforms landing → staging → marts, contains macros, tests, and docs.
* Orchestration: Airflow to coordinate landing script + dbt runs (and optionally downstream tasks).

## Getting Started

### Creating a Fresh Python Environment

To set up an isolated environment for dbt and project dependencies:

**Windows (PowerShell):**

```
python -m venv $env:USERPROFILE\venvs\dbt-venv
```

This creates a virtual environment at:

```
%USERPROFILE%\venvs\dbt-venv
```

### Activating the Virtual Environment

Activate the environment using PowerShell:

```
$env:USERPROFILE\venvs\dbt-venv\Scripts\activate
```

### Installing dbt-bigquery

Once the environment is active, install the BigQuery adapter:

```
pip install dbt-bigquery
```

### Initializing the dbt Project

Create a new dbt project named `e_commerce_platform`:

```
dbt init e_commerce_platform
```

This command will:

* Create the project folder structure
* Generate `dbt_project.yml`
* Create starter directories for models, tests, and macros
* Prompt for BigQuery profile configuration

### Configuring `profiles.yml` for BigQuery

Create or edit the dbt profiles file at:

* Linux/macOS: `~/.dbt/profiles.yml`
* Windows: `%USERPROFILE%/.dbt/profiles.yml`

Add a profile for this project (replace placeholders with your actual values):

```yaml
e_commerce_platform:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: your-gcp-project-id
      dataset: e_commerce_platform
      location: US
      keyfile: C:/path/to/service_account_key.json
      threads: 4
      timeout_seconds: 300
      priority: interactive
      retries: 1
```

Then verify the connection:

```bash
dbt debug --project-dir e_commerce_platform
```

For more details and alternative authentication methods, refer to the official dbt BigQuery setup guide:
[https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup](https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup)

Create a new dbt project named `e_commerce_platform`:

```
dbt init e_commerce_platform
```

This command will:

* Create the project folder structure
* Generate `dbt_project.yml`
* Create starter directories for models, tests, and macros
* Prompt for BigQuery profile configuration
  Once the environment is active, install the BigQuery adapter:

```
pip install dbt-bigquery
```

%USERPROFILE%\venvs\dbt-venv

````


### Prerequisites
- Google Cloud account with a GCP project and BigQuery enabled.
- gcloud CLI configured and authenticated.
- Python 3.8+ and virtualenv.
- dbt-core and dbt-bigquery adapter installed (version pinned in `requirements.txt`).
- Airflow (local or remote) for orchestration.

### Environment setup
1. Clone this repo.
2. Create and activate virtualenv: `python -m venv .venv && source .venv/bin/activate`.
3. Install Python deps: `pip install -r requirements.txt`.
4. Set GCP credentials: `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`.
5. Configure `profiles.yml` for dbt:
   - Location: `~/.dbt/profiles.yml` (or provide path via env var).
   - Ensure credentials point to the target GCP project and dataset.

### Running landing script (local)
- `python scripts/generate_and_load.py --config config/dev.yaml`

### Landing Layer – Synthetic Data Generation (Gemini + BigQuery)
The landing layer is populated by a Python script that calls the Gemini API to generate synthetic e-commerce data and then loads it into BigQuery.

Steps:
1. Make sure the target BigQuery dataset for the landing layer exists (configured in `config/dev.yaml`).
2. Create a Gemini API key in your Google Cloud project.
3. Expose the key to the script via an environment variable named `GEMINI_API_KEY`.
4. Run the landing script:
   ```bash
   python scripts/generate_and_load.py --config config/dev.yaml
````

### Environment Variables Used by Landing Script

The landing script requires the following environment variables:

| Variable                                  | Purpose                                             | Example                                                       |
| ----------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------- |
| `GEMINI_API_KEY`                          | Auth key to generate synthetic data via Gemini      | `export GEMINI_API_KEY="AIxxx..."`                            |
| `GOOGLE_APPLICATION_CREDENTIALS`          | Path to GCP service account key for BigQuery access | `export GOOGLE_APPLICATION_CREDENTIALS="C:/keys/gcp_sa.json"` |
| Override landing dataset from config file | `export BQ_DATASET="landing"`                       |                                                               |

> These variables can be set on local machines or inside Airflow worker environments.

This script will **automate landing layer creation**** and perform the following tasks:

* Generate synthetic `customers`, `products`, `orders`, etc.
* Write the data into the configured BigQuery landing tables (for example: `landing.customers`, `landing.products`, `landing.orders`).
* Be idempotent for development (you can safely re-run it to refresh the landing layer).

### Running dbt (local)

* `dbt deps`
* `dbt run --models +stg_*`
* `dbt test`

### Running Airflow

* Place DAG file into your Airflow `dags/` folder.
* Start scheduler & webserver (or use managed Airflow): `airflow standalone` (for local testing).

## Project Structure

```

├── models/                   # dbt models (staging, marts, consumption)
│   ├── 01_staging/           # Cleanses & standardizes landing data
│   ├── 02_marts/             # Facts & dimensions with business logic
│   └── 03_consumption/       # Final KPI/analytics models
│
├── scripts/                  # Synthetic data generator & dependencies
│   ├── generate_and_load.py  # Uses Gemini to generate & ingest data
│   └── requirements.txt       # Python dependencies for synthetic data
│
├── dags/                     # Airflow DAGs for orchestration                     # Airflow DAGs for orchestration
│   └── ecom_pipeline_dag.py  # Runs landing + dbt models end‑to‑end
│
├── tests/                    # dbt tests (schema + data quality)
│
├── config/                   # Config files for data generation or custom setups (optional)                   # Config files for dev/prod (if applicable)
│
├── requirements.txt          # Python dependencies for synthetic data scripts          # Python dependencies
├── README.md                 # Main project documentation                 # Project documentation
└── .env / environment vars   # Contains required API keys & credentials
├── dbt_project.yml          # dbt project configuration
└── profiles.yml              # Local dbt connection config for BigQuery
```

## dbt – Models & Layers

This project follows a layered dbt architecture for building clean, scalable, and analytics‑ready data models in BigQuery.

### 🌱 1) Staging Layer (`01_staging`)

📂 GitHub path: `models/01_staging/`
**Purpose:** Clean and standardize raw/landing tables.

* One‑to‑one mapping with BigQuery landing dataset tables
* Rename & cast fields (timestamps, integers, numeric types)
* Handle duplicates and missing values when needed
* Apply basic business rules (e.g., ignore negative prices)

🔎 **Examples of staging models:**

* `stg_customers.sql`
* `stg_products.sql`
* `stg_orders.sql`

📌 **Output examples:**

* `customer_id`, `full_name`, `created_at`, etc.
* `product_id`, `category`, `price`, etc.
* `order_id`, `customer_id`, `order_status`, `order_total`, `order_created_at`

---

### 🏛️ 2) Marts Layer (`02_marts`)

📂 GitHub path: `models/02_marts/`
**Purpose:** Build business‑friendly dimensional & fact models.

* Use staging models as sources
* Build **dimensions** (e.g., `dim_customers`, `dim_products`)
* Build **facts** (e.g., `fact_orders`)
* Apply business logic such as completed orders only

🔎 **Key models include:**

* `dim_customers.sql`
* `dim_products.sql`
* `fact_orders.sql`

📌 **Business logic examples:**

* Filter orders by `order_status = 'completed'`
* Calculate revenue from price * quantity
* Add derived attributes (e.g., `customer_tenure_days`)

---

### 📊 3) Consumption Layer (`03_consumption`)

📂 GitHub path: `models/03_consumption/`
**Purpose:** Create analytics/KPI models ready for BI dashboards.

* Uses marts (facts/dims) to compute metrics
* Performs rolling windows, aggregations, and rankings

🔎 **KPI model examples:**

* `customer_ltv_30d.sql` → 30‑day lifetime value
* `daily_revenue_by_date.sql` → daily business revenue
* `monthly_revenue_by_category.sql` → per‑category insights
* `top_products_90d.sql` → trending products over 90 days

📌 **Typical metrics:**

* Daily/Monthly Revenue
* 30/90 Day LTV
* Top selling SKUs
* Category revenue contribution

---

### 🧪 dbt Tests, Schema YAML & Documentation

All core models are documented and tested using dbt's `schema.yml` files.

### Schema YAML Layout

* Main schema file lives under `models/schema.yml` (or split by folder if preferred).
* Contains:

  * **Model descriptions** (what the table represents)
  * **Column descriptions** (business meaning of each field)
  * **Tests** attached to columns (e.g., `unique`, `not_null`, `relationships`)
  * **Tags** to group models by layer (e.g., `staging`, `marts`, `consumption`).

### Typical Tests Used

* `unique` – ensure primary keys like `order_id`, `customer_id` are unique.
* `not_null` – enforce mandatory fields (IDs, foreign keys, status fields).
* `relationships` – ensure referential integrity between facts and dimensions.
* Optional: `accepted_values` for enums like `order_status`.

### dbt Docs

The project uses dbt docs to visualize lineage and metadata:

```bash
dbt docs generate
dbt docs serve
```

Analysts and engineers can:

* Explore model dependencies (landing → staging → marts → consumption)
* Read descriptions for each model & column
* Inspect tests and their status.

---


## Airflow DAG

This project uses **Apache Airflow (Cloud Composer)** to orchestrate the full data pipeline:

* Fetch secrets from **Google Secret Manager**
* Generate synthetic data using **Gemini API**
* Load landing tables in **BigQuery**
* Run **dbt** transformations (staging → marts → consumption)
* Run **dbt tests** for each layer

---

### DAG Overview

* **DAG ID:** `ecom_pipeline_dag`
* **Location:** `dags/ecom_pipeline_dag.py`
* **Schedule:** Manual (`schedule_interval=None`)
* **Start Date:** `2025-01-01`
* **Retries:** `1` (3-minute retry delay)
* **Tools Used:**

  * `PythonOperator` → Fetch secrets from Secret Manager
  * `BashOperator` → Landing pipeline + dbt tasks
  * **Virtualenv** dynamically created for dbt execution

---

### 🔐 Secret Management (XCom Usage)

The DAG first fetches two secrets using `PythonOperator`:

* `gemini_api_key`
* `service_account_json` (full SA JSON string)

Stored automatically in **XCom** and accessed as:

```jinja
{{ ti.xcom_pull(task_ids='fetch_secrets')['gemini_api_key'] }}
{{ ti.xcom_pull(task_ids='fetch_secrets')['service_account_json'] }}
```

---

### 📨 Landing Data Generation

The `generate_and_load_landing` task:

* Writes the SA JSON to `/tmp/sa_key.json`
* Installs dependencies from:

  ```
  /home/airflow/gcs/dags/scripts/requirements.txt
  ```
* Runs the landing script:

  ```bash
  python generate_and_load_landing.py
  ```
* Removes the temporary SA file

Populates BigQuery landing tables:

* `landing.customers`
* `landing.products`
* `landing.orders`

---

### 🏗️ dbt Execution via Virtualenv

A temporary dbt environment is created in `/home/airflow/dbt_venv` and installs:

* `dbt-core`
* `dbt-bigquery`

Project location in Composer:

```
/home/airflow/gcs/data/ecom
```

---

### 🌱 ➜ 🏛️ ➜ 📊 dbt Model Execution (Layer-wise)

#### 1) **Staging**

```bash
dbt run -s models/01_staging/*
dbt test -s models/01_staging/*
```

#### 2) **Marts**

```bash
dbt run -s models/02_marts/*
dbt test -s models/02_marts/*
```

#### 3) **Consumption KPIs**

```bash
dbt run -s models/03_consumption/*
dbt test -s models/03_consumption/*
```

---

### 🔗 Final Task Dependency Chain

```text
fetch_secrets
    ↓
generate_and_load_landing
    ↓
create_venv
    ↓
run_dbt_staging
    ↓
run_dbt_staging_test
    ↓
run_dbt_marts
    ↓
run_dbt_marts_test
    ↓
run_dbt_consumption
    ↓
run_dbt_consumption_test
```

---

### 💡 Notes

* Secrets are removed after task execution (never stored permanently)
* Composer environment variables are configured for:

  * `GEMINI_API_KEY`
  * `GOOGLE_APPLICATION_CREDENTIALS`
* Pipeline fails if **any dbt test fails**, enforcing CI-style quality

---


## Data Sources & Schemas

This project simulates an end-to-end e‑commerce analytics platform. The data ingested into BigQuery is **synthetic**, generated using the Gemini API and stored in the **landing dataset**. These tables serve as the raw foundation for dbt transformations.

The platform models three core business entities:

* **Customers** (who purchases)
* **Products** (what they buy)
* **Orders** (transactions and revenue)

---

### 🧱 Landing Dataset (Raw Data)

The landing layer contains unprocessed data generated by the `generate_and_load_landing.py` script.

📌 **Dataset name:** `landing`

### 📍 Tables Included

| Table               | Description                                  |
| ------------------- | -------------------------------------------- |
| `landing.customers` | Basic customer details generated from Gemini |
| `landing.products`  | Product catalog with categories and prices   |
| `landing.orders`    | Transaction-level order information          |

### 📌 Example Schema Snapshots

> These schemas are generated dynamically, and sample column names are listed below.

#### 🧑‍🤝‍🧑 `landing.customers`

| Column        | Type      | Notes              |
| ------------- | --------- | ------------------ |
| `customer_id` | STRING    | Unique identifier  |
| `full_name`   | STRING    | Synthetic name     |
| `email`       | STRING    | Fake email pattern |
| `created_at`  | TIMESTAMP | Signup timestamp   |

#### 🎁 `landing.products`

| Column       | Type    | Notes              |
| ------------ | ------- | ------------------ |
| `product_id` | STRING  | Unique product ID  |
| `name`       | STRING  | Product name       |
| `category`   | STRING  | Product category   |
| `price`      | NUMERIC | Unit selling price |

#### 🧾 `landing.orders`

| Column             | Type      | Notes                               |
| ------------------ | --------- | ----------------------------------- |
| `order_id`         | STRING    | Unique order ID                     |
| `customer_id`      | STRING    | Refers to customers table           |
| `product_id`       | STRING    | Refers to products table            |
| `order_status`     | STRING    | e.g., completed, shipped, cancelled |
| `quantity`         | INT64     | Number of units ordered             |
| `order_total`      | NUMERIC   | Derived as price × quantity         |
| `order_created_at` | TIMESTAMP | Order placement timestamp           |

---

### 🗂️ Staging Schema (Standardized Layer)

The staging layer cleans and formats data loaded from landing.

📌 **Folder path:** `models/01_staging/`

Common transformations:

* Cast numeric & timestamp fields
* Standardize names and select required columns only
* Remove null/invalid records (e.g., negative quantity)

Example output columns:

* `customer_id`, `full_name`, `email`, `created_at`
* `product_id`, `category`, `price`
* `order_id`, `customer_id`, `order_status`, `order_total`, `order_created_at`

---

### 📊 Marts Schema (Facts & Dimensions)

Dimensional models created from staging tables.

📌 **Folder path:** `models/02_marts/`

Examples:

* `dim_customers` → Enrich customer information & calculate metrics
* `dim_products` → SKU‑level aggregations
* `fact_orders` → Revenue, status, and quantity metrics

Business logic applied:

* Filter orders by `order_status = 'completed'`
* Compute `revenue = price × quantity`
* Encode derivations (e.g., `customer_tenure_days`)

---

### 📈 Consumption Schema (KPIs for Analytics)

KPI models built for downstream BI usage.

📌 **Folder path:** `models/03_consumption/`

Model examples:

* `customer_ltv_30d` → Rolling 30‑day revenue per customer
* `daily_revenue_by_date` → Day‑wise GMV (Gross Merchandise Value)
* `monthly_revenue_by_category` → Category‑wise revenue
* `top_products_90d` → Best sellers from the last 90 days

---

### 🧪 Schema YAML & Data Quality Rules

Every model group has a corresponding schema YAML defining:

* Model & column descriptions
* Tests (`unique`, `not_null`, `relationships`, `accepted_values`)
* Tags by layer (`staging`, `marts`, `consumption`)

📌 Example reference:

```bash
models/schema.yml
```

These constraints ensure data reliability at every step from landing → staging → marts → consumption.

---

## Testing & Quality Checks

Data quality is enforced throughout the pipeline using **dbt tests**, **schema constraints**, and **Airflow validations**. These checks ensure the accuracy, reliability, and consistency of data from landing → staging → marts → consumption.

---

### 🧪 dbt Schema Tests

Schema-level tests are declared in `models/schema.yml` and applied to every layer.

#### 🔑 Common dbt Tests Used

| Test              | Purpose                             | Applied To                                           |
| ----------------- | ----------------------------------- | ---------------------------------------------------- |
| `unique`          | Ensure keys are unique              | `customer_id`, `order_id`, `product_id`              |
| `not_null`        | Prevent missing required values     | Primary & foreign keys, timestamps                   |
| `relationships`   | Enforce FK integrity between models | `customer_id` in orders, `product_id` in orders      |
| `accepted_values` | Validate enums                      | `order_status` (e.g., completed, shipped, cancelled) |
| `dbt_utils` tests | Additional integrity checks         | Complex joins & calculations                         |

yaml
models:

* name: stg_orders
  description: Standardized orders data from landing
  columns:

  * name: order_id
    tests:

    * unique
    * not_null
  * name: customer_id
    tests:

    * not_null
    * relationships:
      to: ref('stg_customers')
      field: customer_id
  * name: order_status
    tests:

    * accepted_values:
      values: ['completed', 'cancelled', 'shipped']


---

### 🧮 Business Logic Validations (Marts)
Fact and dimension models are validated for business consistency.

Example validations applied in marts (`models/02_marts/`):
- Orders counted only when `order_status = 'completed'`
- Revenue must be `price × quantity` and non-negative
- Ensure dimensional tables have unique business keys

These rules prevent incorrect KPI reporting downstream.

---

### 📊 Consumption KPIs Checks

KPI models (e.g., `customer_ltv_30d`, `top_products_90d`) apply strict checks:
- No negative revenue
- Window aggregations must match input totals
- Filter logic must exclude invalid orders

```sql
where order_status = 'completed'
```

These checks make analytics reports trustworthy across Power BI, Looker, Tableau, etc.

---

### 🚦 Airflow Validation & Fail-Fast Strategy

Airflow enforces pipeline integrity by **failing the DAG** if any dbt tests fail.

**Behavior:**

* If `dbt run` fails → DAG stops
* If `dbt test` fails → DAG stops
* Full failure is visible in Airflow UI logs

This build ensures:

* Bad data never propagates to marts or KPIs
* Developers fix data issues immediately
* System behaves like CI/CD for analytics

---

## Deployment

This project can be deployed both **locally** (for development and testing) and on **Google Cloud Composer** (managed Airflow) for production‑grade orchestration.

Deployment ensures:

* Synthetic data is consistently generated
* dbt transformations run reliably
* Tests enforce data quality before publishing analytics

---

### 🚀 Local Deployment

Local deployment is primarily for development, experimentation, and debugging.

### 📦 Steps

1. **Clone the repository**
2. **Install Python dependencies**

   ```bash
   pip install -r scripts/requirements.txt
   ```
3. **Prepare environment variables:**

   ```bash
   export GEMINI_API_KEY="your-key"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
   ```
4. **Generate landing data and load into BigQuery**

   ```bash
   python scripts/generate_and_load_landing.py
   ```
5. **Run dbt transformations**

   ```bash
   dbt deps
   dbt run
   dbt test
   ```

📌 *Local mode is ideal for feature development and model iteration.*

---

### ☁️ Deployment on Cloud Composer (GCP)

This production‑grade deployment uses **managed Airflow** for orchestration.

### 📂 Required Components in Composer

| Component           | Path                                        | Purpose                           |
| ------------------- | ------------------------------------------- | --------------------------------- |
| Airflow DAG         | `dags/ecom_pipeline_dag.py`                 | Orchestrates the pipeline         |
| Landing script      | `dags/scripts/generate_and_load_landing.py` | Generates & loads synthetic data  |
| Python requirements | `dags/scripts/requirements.txt`             | Gemini & BigQuery dependencies    |
| dbt project         | `data/ecom/`                                | All transformations & data models |
| `profiles.yml`      | alongside dbt project                       | Enables BigQuery connection       |

---

### 🔐 Secrets Configuration

Secrets are stored in **Google Secret Manager** and fetched dynamically by Airflow.

| Secret Key             | Purpose                                      |
| ---------------------- | -------------------------------------------- |
| `gemini_api_key`       | Authentication for synthetic data generation |
| `service_account_json` | Full JSON credentials used by Composer       |

📌 *No credentials are hardcoded or stored in the repository.*

---

### 🔄 Continuous Deployment via GitHub Actions

Whenever changes are pushed to **main branch**, GitHub Actions:

* Copies latest scripts and dbt project into Composer bucket
* Syncs DAGs, scripts, and dbt files automatically
* Triggers **manual run on Composer UI** (trigger is optional)

This ensures the environment always reflects the latest code.

📌 *CI + Composer = Dynamic, version‑controlled data pipeline.*

---

### 🏁 Final Notes

* Composer executes dbt through a **temporary virtualenv**
* All secrets are ephemeral and removed as part of each task
* Pipeline fails if **any dbt test fails**, enforcing reliability
* Designed to scale: Add new tables, layers, and KPIs with minimal impact

---
## Decisions & Open Questions

This section documents key engineering decisions made during the project and questions left open for future iterations. The goal is to make the platform transparent, extensible, and easy to maintain.

---

### 💡 Major Design Decisions

#### 1) **Synthetic Data Using Gemini API**

* Chosen instead of publicly available datasets to provide realistic, dynamic variation.
* Enables simulation of revenue spikes, customer behavior, and trending products.
* Trade-off: Harder to reproduce exactly without the same prompts & settings.

#### 2) **dbt as the Core Transformation Layer**

* dbt was selected for its declarative modeling, tested transformations, and lineage.
* Clear separation into **staging → marts → consumption** makes the pipeline scalable.
* Keeps SQL business logic in version control.

#### 3) **Cloud Composer (Managed Airflow)**

* Provides stable scheduling, monitoring, retries, and logging.
* Reduces operational overhead of maintaining Airflow infrastructure.
* Trade-off: Higher cost vs. self-hosted Airflow.

#### 4) **Secret Manager for Credentials**

* Avoids storing keys in files or environment variables.
* Credentials pulled dynamically and deleted after task execution.
* Improves compliance and security posture.

#### 5) **Virtualenv for dbt in Composer**

* Ensures dbt dependency isolation across Airflow workers.
* Temporary venv validates reproducible and fresh installs.
* Trade-off: Slightly longer runtime during DAG execution.

---

### ❓ Open Questions for Future Development

#### 🔸 Scalability

* Should synthetic data volume increase to simulate larger enterprise datasets?
* Would switching from BigQuery landing to real-time ingestion (Pub/Sub → Dataflow) add business value?

#### 🔸 Testing Strategy

* Should we implement **freshness tests** and **source tests** for landing data?
* Should SLA & alerts (Slack/Email) be mandatory for failed dbt tests?

#### 🔸 Cost Optimization

* Should venv creation and dbt installation be containerized via a custom Composer image?
* Could dbt transformations be scheduled selectively for incremental updates?

#### 🔸 BI Layer Integration

* Should this platform include exporting consumption tables into Looker/Power BI data models?
* Should semantic layers or metrics flow be introduced (dbt Semantic Layer)?

---

### 🚀 Expected Future Enhancements

| Enhancement                 | Expected Impact                           |
| --------------------------- | ----------------------------------------- |
| Incremental models in dbt   | Faster marts & KPI refresh time           |
| Data contracts for landing  | Reliability + validation before ingestion |
| Automated SLAs & monitoring | Stronger production readiness             |
| Custom Composer image       | Faster deployment + stable dependencies   |
| Cloud logging + alerts      | Reduced troubleshooting time              |

---



## Contributing

We welcome contributions that help improve functionality, documentation, data quality, and infrastructure. Whether fixing bugs, improving models, or enhancing orchestration, contributions make this project stronger and useful for the community.

---

### 🤝 How to Contribute

#### 1) Fork the Repository

* Create your own fork from the main branch.
* Work on a feature branch (e.g., `feature/add-ltv-metric`).

#### 2) Open Issues Before Major Enhancements

* Describe the feature, reasoning, expected impact.
* Share context for design or logic changes (dbt models, DAG steps, tests).

#### 3) Follow Coding Standards

* Use **SQL + Jinja best practices** for dbt models.
* Keep **schema.yml updated** with model + column descriptions.
* Ensure **dbt tests** exist for all critical fields.
* Maintain atomic, readable commit messages.

#### 4) Test Locally Before PR

* Validate landing script loads correctly into BigQuery.
* Run full dbt pipeline:

  ```bash
  dbt deps
  dbt run
  dbt test
  ```
* Confirm Airflow DAG passes all tasks locally/composer environment.

#### 5) Submit a Pull Request

* Provide a clear description of the change.
* Link related issue if applicable.
* Include screenshots or logs if impacting DAG/dbt behavior.

---

### 📌 Contribution Scope

| Area               | Examples                                          |
| ------------------ | ------------------------------------------------- |
| **dbt Models**     | New dimensions, facts, KPI models                 |
| **Airflow DAGs**   | Retry logic, alerts, parallelism                  |
| **Landing Script** | Data variety, new tables, validations             |
| **Testing**        | Freshness tests, source tests, performance checks |
| **Documentation**  | Architecture diagrams, lineage, tutorial updates  |

---

### 🧩 Code of Conduct

* Treat contributors respectfully.
* Be collaborative — review comments positively.
* No sensitive data or credentials should ever be shared.

📌 *This project encourages collaboration that improves data engineering best practices!*

## License & Contact

### 📜 License

No open-source license is currently applied to this project. **All rights are reserved by the owner.**

📌 For reuse, redistribution, or commercial use, please contact the maintainer.

---

### 📬 Contact

For questions, collaboration, or suggestions, feel free to reach out:

👤 **Maintainer:** Abhishek Kulkarni
💼 **Role:** Data Engineer
🔗 **GitHub:** [https://github.com/Abhiselon](https://github.com/Abhiselon)
🔗 **LinkedIn:** [https://www.linkedin.com/in/abhishek-kulkarni26/](https://www.linkedin.com/in/abhishek-kulkarni26/)
🎥 **YouTube:** [https://www.youtube.com/@TheDatakulkarni](https://www.youtube.com/@TheDatakulkarni)
📧 **Email:** [abhishekbkulkarni26@gmail.com](mailto:abhishekbkulkarni26@gmail.com)

---

### 🤝 Collaboration & Community

If you’d like to:

* Use this project commercially
* Integrate with BI dashboards (Looker/Power BI/Tableau)
* Expand into real-time streaming or incremental processing

👉 Open an issue or reach out directly — contributions and ideas are welcome!

---

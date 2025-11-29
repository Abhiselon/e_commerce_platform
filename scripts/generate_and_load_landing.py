#!/usr/bin/env python3
"""
generate_and_load_landing.py
Generates synthetic ecommerce landing data using Gemini + Faker,
converts types for BigQuery, and loads into BigQuery using WRITE_TRUNCATE.
"""

# ----------------------------
# STEP 0 — Imports & configuration
# ----------------------------
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List

import pandas as pd
from faker import Faker

# Google Cloud
from google import genai
from google.cloud import bigquery

# Pydantic
from pydantic import BaseModel, Field

# ----------------------------
# STEP 0a — Configuration
# ----------------------------
NUM_CUSTOMERS = 50
NUM_PRODUCTS = 30
NUM_ORDERS = 500

PROJECT_ID = "modular-ground-478409-a3"
DATASET_ID = "landing"

TWO_PLACES = Decimal("0.01")

# ----------------------------
# STEP 0b — Authentication
# ----------------------------
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
if API_KEY == "YOUR_GEMINI_API_KEY":
    print("FATAL: Please set GEMINI_API_KEY environment variable.")
    exit(1)

# ----------------------------
# STEP 1 — Initialize clients
# ----------------------------
try:
    gemini_client = genai.Client(api_key=API_KEY)
    bq_client = bigquery.Client(project=PROJECT_ID)
    print("[STEP 1] Initialized Gemini and BigQuery clients.")
except Exception as e:
    print(f"Error initializing clients: {e}")
    exit(1)

faker = Faker()

# ----------------------------
# STEP 2 — Pydantic schemas for Gemini output
# ----------------------------
class Customer(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    created_at: str

class CustomerDataset(BaseModel):
    customers: List[Customer]

class Product(BaseModel):
    product_id: str
    product_name: str
    category: str
    price: float
    created_at: str

class ProductDataset(BaseModel):
    products: List[Product]

print("\n[STEP 2] Defined Pydantic schemas.")

# ----------------------------
# STEP 3 — Helper: call Gemini and return DataFrame
# ----------------------------
def generate_gemini_data(prompt: str, schema: BaseModel) -> pd.DataFrame:
    """Generate structured data from Gemini and return DataFrame."""
    print(f"[STEP 3] Generating data for {schema.__name__}...")
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )
        data_object = response.parsed
        data_dict = data_object.model_dump()
        key = list(data_dict.keys())[0]
        df = pd.DataFrame(data_dict[key])
        print(f"  -> Generated {len(df)} records")
        return df
    except Exception as e:
        print(f"  -> Gemini generation failed for {schema.__name__}: {e}")
        return pd.DataFrame()

# Generate dimensions
customer_prompt = (
    f"Generate {NUM_CUSTOMERS} synthetic customer records. "
    f"Use sequential IDs starting from CUST-0001. "
    "Return JSON key `customers`."
)

product_prompt = (
    f"Generate {NUM_PRODUCTS} synthetic product records across Apparel, Electronics, and Home Goods. "
    "Return JSON key `products`."
)

products_df = generate_gemini_data(product_prompt, ProductDataset)
customers_df = generate_gemini_data(customer_prompt, CustomerDataset)

# ----------------------------
# STEP 4 — Generate orders using Faker
# ----------------------------
def generate_orders_data(num: int, customers_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate orders referencing customers and products.
    Each order will include product_id, quantity, unit_price, and order_total.
    """
    print(f"\n[STEP 4] Generating {num} ORDERS (with product_id) ...")
    if customers_df.empty or products_df.empty:
        print("  -> Missing dimension data. Aborting.")
        return pd.DataFrame()

    customer_ids = customers_df["customer_id"].tolist()
    # create a list of (product_id, price) tuples for sampling
    product_price_pairs = products_df[["product_id", "price"]].to_records(index=False).tolist()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    orders = []
    for i in range(1, num + 1):
        customer_id = random.choice(customer_ids)
        # pick a random product (id and price)
        product_id, unit_price_src = random.choice(product_price_pairs)
        # ensure unit_price is float to compute then convert to Decimal later
        unit_price_float = float(unit_price_src)

        quantity = random.randint(1, 5)
        order_total_float = round(unit_price_float * quantity, 2)
        order_ts = faker.date_time_between(start_date=start_date, end_date=end_date)

        orders.append({
            "order_id": f"ORD-{i}-{faker.uuid4()[:8]}",
            "customer_id": customer_id,
            "product_id": product_id,                     # <-- new
            "quantity": quantity,                         # <-- new
            "unit_price": round(unit_price_float, 2),     # <-- new
            "order_total": order_total_float,
            "order_status": random.choice(["SHIPPED", "DELIVERED", "PROCESSING"]),
            "order_ts": order_ts.isoformat(),
            "created_at": datetime.now().isoformat(),
        })

    df = pd.DataFrame(orders)
    print(f"  -> Generated {len(df)} orders")
    return df

orders_df = generate_orders_data(NUM_ORDERS, customers_df, products_df)

# ----------------------------
# STEP 5 — Convert types for BigQuery compatibility
# ----------------------------
print("\n[STEP 5] Converting data types for BigQuery...")

if not customers_df.empty:
    customers_df["created_at"] = pd.to_datetime(customers_df["created_at"])
    print("  Customers: OK")

if not products_df.empty:
    products_df["price"] = products_df["price"].apply(
        lambda x: Decimal(str(x)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    )
    products_df["created_at"] = pd.to_datetime(products_df["created_at"])
    print("  Products: OK")

if not orders_df.empty:
    orders_df['unit_price'] = orders_df['unit_price'].apply(
    lambda x: Decimal(str(x)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    )
    orders_df['order_total'] = orders_df['order_total'].apply(
    lambda x: Decimal(str(x)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    )
    orders_df['order_ts'] = pd.to_datetime(orders_df['order_ts'])
    orders_df['created_at'] = pd.to_datetime(orders_df['created_at'])
    print("  Orders: OK")

print("\nSummary:")
print(f"  Customers: {len(customers_df)} rows")
print(f"  Products:  {len(products_df)} rows")
print(f"  Orders:    {len(orders_df)} rows")

# ----------------------------
# STEP 6 — Load DataFrames into BigQuery (TRUNCATE & INSERT)
# ----------------------------
def load_dataframe_to_bigquery(df: pd.DataFrame, table_name: str, bq_client: bigquery.Client):
    """Load df into BigQuery table using WRITE_TRUNCATE."""
    full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    print(f"\n[STEP 6] Loading to {full_table_id} ...")
    try:
        job = bq_client.load_table_from_dataframe(
            df, full_table_id, job_config=job_config
        )
        job.result()
        print(f"  Loaded {job.output_rows} rows.")
    except Exception as e:
        print(f"  Error loading {table_name}: {e}")

load_dataframe_to_bigquery(customers_df, "customers", bq_client)
load_dataframe_to_bigquery(products_df, "products", bq_client)
load_dataframe_to_bigquery(orders_df, "orders", bq_client)

print("\nComplete. Check BigQuery landing tables.")

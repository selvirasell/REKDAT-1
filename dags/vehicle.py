from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import logging

# Constants
COMPANIES = [
    {"symbol": "TSLA", "table": "tesla_stock_data2", "name": "Tesla"},
    {"symbol": "XOM", "table": "exxon_stock_data2", "name": "Exxon"},
]
INTERVAL = "60min"  # Time interval (hourly)
POSTGRES_CONN_ID = "postgres_default"
API_CONN_ID = "alpha_vantage_api"

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="alpha_vantage_tesla_exxon_etl",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False,
) as dag:

    @task()
    def extract_stock_data(company):
        logging.info(f"Starting data extraction for {company['name']} ({company['symbol']})...")
        http_hook = HttpHook(http_conn_id=API_CONN_ID, method="GET")
        connection = http_hook.get_connection(API_CONN_ID)
        api_key = connection.extra_dejson.get("api_key")

        if not api_key:
            raise ValueError("API key not found in connection 'alpha_vantage_api'")

        endpoint = f"/query?function=TIME_SERIES_INTRADAY&symbol={company['symbol']}&interval={INTERVAL}&apikey={api_key}"
        response = http_hook.run(endpoint)

        if response.status_code != 200:
            logging.error(f"Failed to fetch data for {company['symbol']}: {response.status_code}")
            raise Exception(f"API request failed with status code {response.status_code}")

        data = response.json()

        if "Note" in data or "Error Message" in data:
            logging.error(f"Error fetching data for {company['symbol']}: {data}")
            raise ValueError("Error in API response")

        time_series = data.get("Time Series (60min)", {})
        if not time_series:
            logging.error(f"No 'Time Series (60min)' data found for {company['symbol']}.")
            raise ValueError("Missing 'Time Series (60min)' in API response")

        logging.info(f"Fetched {len(time_series)} records for {company['name']}.")
        return {"company": company, "data": time_series}

    @task()
    def transform_stock_data(stock_payload):
        company = stock_payload["company"]
        stock_data = stock_payload["data"]
        logging.info(f"Starting data transformation for {company['name']}...")

        transformed_data = []
        for timestamp, values in stock_data.items():
            transformed_data.append({
                "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            })
        return {"table": company["table"], "data": transformed_data}

    @task()
    def load_stock_data(payload):
        table_name = payload["table"]
        transformed_data = payload["data"]
        if not transformed_data:
            logging.warning(f"No data to load into {table_name}.")
            return

        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            timestamp TIMESTAMP PRIMARY KEY,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume BIGINT
        );
        """)

        for record in transformed_data:
            cursor.execute(f"""
            INSERT INTO {table_name} (timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO NOTHING;
            """, (
                record["timestamp"],
                record["open"],
                record["high"],
                record["low"],
                record["close"],
                record["volume"],
            ))

        conn.commit()
        cursor.close()

    for company in COMPANIES:
        stock_data = extract_stock_data(company)
        transformed_data = transform_stock_data(stock_data)
        load_stock_data(transformed_data)

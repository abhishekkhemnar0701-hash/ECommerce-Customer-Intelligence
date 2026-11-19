
# E-Commerce Customer Intelligence Platform

## Overview
An end-to-end data engineering project designed to process e-commerce transactions, integrate batch and streaming data, and generate customer intelligence using RFM analysis.

## Architecture
CSV Data → Python ETL → PostgreSQL
Kafka Producer → Kafka Topic → Kafka Consumer → PostgreSQL
PostgreSQL → RFM Analytics → Streamlit Dashboard

## Technologies Used
- Python
- PostgreSQL
- SQLAlchemy
- Apache Kafka
- Pandas
- Streamlit
- Plotly
- Git & GitHub

## Key Features
- Synthetic e-commerce data generation
- Batch ETL pipeline
- Incremental data loading and upsert
- Data quality validation
- ETL execution logging
- Kafka event producer and consumer
- Streaming events stored in PostgreSQL
- Customer segmentation using RFM analysis
- Customer intelligence dashboard

## Project Modules
- Data ingestion
- ETL extraction
- Data transformation
- Database loading
- Data quality checks
- Kafka streaming
- Customer RFM analysis
- Streamlit dashboard

## Run Locally

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ECommerce-Customer-Intelligence.git

### 2. Navigate into the project
cd ECommerce-Customer-Intelligence

### 3. Create virtual environment
python -m venv venv

### 4. Activate environment (Windows)
venv\Scripts\activate

### 5. Install dependencies
pip install -r requirements.txt

### 6. Configure PostgreSQL
Create the PostgreSQL database and configure your local .env file.

### 7. Initialize database schema
python -m src.ingestion.init_schema

### 8. Generate synthetic data
python -m src.ingestion.generate_data

### 9. Run ETL pipeline
python -m src.etl.run_pipeline

### 10. Run customer RFM analysis
python -m src.intelligence.rfm_analysis

### 11. Start Streamlit dashboard
python -m streamlit run dashboard/app.py

## Disclaimer
This project uses synthetic data and is developed for educational and portfolio demonstration purposes.

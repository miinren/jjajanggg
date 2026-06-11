# Databricks Lakehouse Project

## Overview
End-to-end data engineering pipeline built using Databricks, Auto Loader, and Power BI.

## Architecture

### Batch Pipeline

Raw CSV/JSON Files
    ↓
Databricks Auto Loader
    ↓
Bronze Delta Tables
    ↓
Silver Cleaned Tables
    ↓
Gold Business Aggregations
    ↓
Power BI Dashboard

### Streaming Pipeline

Confluent Kafka Topic (`orders`)
    ↓
Databricks Structured Streaming
    ↓
Bronze Kafka Delta Table
    ↓
Silver Kafka Cleansed Table
    ↓
Gold Kafka Revenue Aggregation

## Tools Used

- Databricks (Delta Lake, PySpark)
- Auto Loader
- Power BI

## Pipeline

1. Bronze ingestion
2. Silver cleaning
3. Gold aggregation
4. Data quality checks
5. Audit logging
6. Validation

## Key Features

- Incremental ingestion (Auto Loader)
- Medallion architecture
- Data quality validation
- Business-ready analytics tables
- Dashboard visualization

## Tables

### Bronze
- bronze_orders
- bronze_customers

### Silver
- silver_orders
- silver_customers

### Gold
- gold_daily_revenue
- gold_customer_360
- gold_product_performance

## Dashboard

See `/powerbi/dashboard.pbix`

## Kafka Streaming Pipeline

This project includes a Kafka streaming ingestion pipeline using Confluent Cloud and Databricks Structured Streaming.

### Architecture

Kafka Topic (`orders`)
    ↓
Bronze Kafka Table
    ↓
Silver Kafka Table
    ↓
Gold Kafka Aggregation

### Features

- Real-time Kafka ingestion
- Structured Streaming
- Delta Lake Bronze/Silver/Gold architecture
- Secret management using Databricks Secrets
- Event deduplication using watermarking
- Quarantine handling for invalid records
- Kafka metadata tracking (topic, partition, offset)

## Future Improvements

- Workflow orchestration using Apache Airflow
- Real-time dashboard refresh automation
- Advanced data observability and monitoring
- Additional Kafka topics and event streams
- Cloud deployment automation
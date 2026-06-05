# Databricks Lakehouse Project

## Overview
End-to-end data engineering pipeline built using Databricks, Auto Loader, and Power BI.

## Architecture

Raw Data → Bronze → Silver → Gold → Power BI

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
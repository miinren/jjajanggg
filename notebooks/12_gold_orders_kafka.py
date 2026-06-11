# Databricks notebook source
from pyspark.sql.functions import col, to_date, count, sum, round

orders = spark.table("workspace.default.silver_orders_kafka")

gold_daily_revenue_kafka = (
    orders
    .groupBy(to_date(col("order_ts")).alias("order_date"))
    .agg(
        count("*").alias("order_count"),
        round(sum("total_amount"), 2).alias("revenue")
    )
    .orderBy("order_date")
)

gold_daily_revenue_kafka.write.format("delta").mode("overwrite").saveAsTable("workspace.default.gold_daily_revenue_kafka")

display(gold_daily_revenue_kafka)
# Databricks notebook source
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("run_date", "")
dbutils.widgets.text("environment", "dev")

run_id = dbutils.widgets.get("run_id")
run_date = dbutils.widgets.get("run_date")
environment = dbutils.widgets.get("environment")

# COMMAND ----------

from pyspark.sql.functions import col, to_date, count, countDistinct, sum, avg, round, when, datediff, expr

# COMMAND ----------

orders = spark.table("silver_orders")

gold_daily_revenue = (
    orders.groupBy(to_date(col("order_ts")).alias("order_date"))
    .agg(count("*").alias("order_count"),
         countDistinct(col("order_id")).alias("distinct_order_count"),
         sum(col("total_amount")).alias("revenue"),
         round(avg(col("total_amount")), 2).alias("avg_order_value")
).orderBy("order_date")
)

gold_daily_revenue.write.format("delta").mode("overwrite").saveAsTable("gold_daily_revenue")

# COMMAND ----------

payments = spark.table("silver_payments")

gold_payment_success_rate = (
    payments
    .groupBy(to_date(col("payment_ts")).alias("payment_date"))
    .agg(
        count("*").alias("total_payments"),
        sum(when(col("payment_status") == "success", 1).otherwise(0)).alias("successful_payments"),
        sum(when(col("payment_status") == "failed", 1).otherwise(0)).alias("failed_payments"),
        round(
            sum(when(col("payment_status") == "success", 1).otherwise(0)) / count("*"),
            4
        ).alias("payment_success_rate")
    )
    .orderBy("payment_date")
)

gold_payment_success_rate.write.format("delta").mode("overwrite").saveAsTable("gold_payment_success_rate")

# COMMAND ----------

customers = spark.table("silver_customers")
orders = spark.table("silver_orders")

customer_order_metrics = (
    orders
    .groupBy("customer_id")
    .agg(
        count("*").alias("total_orders"),
        round(sum("total_amount"), 2).alias("lifetime_value"),
        round(avg("total_amount"), 2).alias("avg_order_value")
    )
)

gold_customer_lifetime_value = (
    customers
    .join(customer_order_metrics, "customer_id", "left")
    .fillna({
        "total_orders": 0,
        "lifetime_value": 0.0,
        "avg_order_value": 0.0
    })
    .select(
        "customer_id",
        "customer_name",
        "email",
        "country",
        "customer_segment",
        "signup_date",
        "total_orders",
        "lifetime_value",
        "avg_order_value"
    )
)

gold_customer_lifetime_value.write.format("delta").mode("overwrite").saveAsTable("gold_customer_lifetime_value")

# COMMAND ----------

order_items = spark.table("silver_order_items")
products = spark.table("silver_products")

gold_product_performance = (
    order_items
    .join(products, "product_id", "left")
    .groupBy("product_id", "product_name", "category")
    .agg(
        sum("quantity").alias("total_units_sold"),
        round(sum("line_amount"), 2).alias("total_sales"),
        round(avg("silver_order_items.unit_price"), 2).alias("avg_selling_price")
    )
    .orderBy(col("total_sales").desc())
)

gold_product_performance.write.format("delta").mode("overwrite").saveAsTable("gold_product_performance")

# COMMAND ----------

tickets = spark.table("silver_support_tickets")

gold_support_sla_metrics = (
    tickets
    .withColumn(
        "resolution_hours",
        when(
            col("resolved_at").isNotNull(),
            (col("resolved_at").cast("long") - col("created_at").cast("long")) / 3600
        )
    )
    .withColumn(
        "sla_breached",
        when((col("priority") == "critical") & (col("resolution_hours") > 24), 1)
        .when((col("priority") == "high") & (col("resolution_hours") > 48), 1)
        .when((col("priority") == "medium") & (col("resolution_hours") > 72), 1)
        .when((col("priority") == "low") & (col("resolution_hours") > 120), 1)
        .otherwise(0)
    )
    .groupBy(
        to_date(col("created_at")).alias("ticket_date"),
        "priority",
        "issue_type"
    )
    .agg(
        count("*").alias("ticket_count"),
        round(avg("resolution_hours"), 2).alias("avg_resolution_hours"),
        sum("sla_breached").alias("sla_breached_count"),
        round(sum("sla_breached") / count("*"), 4).alias("sla_breach_rate"),
        round(avg("satisfaction_score"), 2).alias("avg_satisfaction_score")
    )
    .orderBy("ticket_date", "priority", "issue_type")
)

gold_support_sla_metrics.write.format("delta").mode("overwrite").saveAsTable("gold_support_sla_metrics")

# COMMAND ----------

events = spark.table("silver_customer_events")

gold_clickstream_funnel = (
    events
    .groupBy(to_date(col("event_ts")).alias("event_date"), "event_type")
    .agg(
        count("*").alias("event_count"),
        countDistinct("customer_id").alias("unique_customers"),
        countDistinct("session_id").alias("unique_sessions")
    )
    .orderBy("event_date", "event_type")
)

gold_clickstream_funnel.write.format("delta").mode("overwrite").saveAsTable("gold_clickstream_funnel")

# COMMAND ----------

customers = spark.table("silver_customers")
orders = spark.table("silver_orders")
tickets = spark.table("silver_support_tickets")
events = spark.table("silver_customer_events")

order_summary = (
    orders
    .groupBy("customer_id")
    .agg(
        count("*").alias("total_orders"),
        round(sum("total_amount"), 2).alias("total_spent"),
        round(avg("total_amount"), 2).alias("avg_order_value")
    )
)

ticket_summary = (
    tickets
    .groupBy("customer_id")
    .agg(
        count("*").alias("total_tickets"),
        sum(when(col("status").isin("open", "in_progress"), 1).otherwise(0)).alias("open_tickets"),
        round(avg("satisfaction_score"), 2).alias("avg_satisfaction_score")
    )
)

event_summary = (
    events
    .groupBy("customer_id")
    .agg(
        count("*").alias("total_events"),
        countDistinct("session_id").alias("total_sessions")
    )
)

gold_customer_360 = (
    customers
    .join(order_summary, "customer_id", "left")
    .join(ticket_summary, "customer_id", "left")
    .join(event_summary, "customer_id", "left")
    .fillna({
        "total_orders": 0,
        "total_spent": 0.0,
        "avg_order_value": 0.0,
        "total_tickets": 0,
        "open_tickets": 0,
        "avg_satisfaction_score": 0.0,
        "total_events": 0,
        "total_sessions": 0
    })
    .withColumn(
        "customer_value_tier",
        when(col("total_spent") >= 10000, "high_value")
        .when(col("total_spent") >= 3000, "medium_value")
        .otherwise("low_value")
    )
    .select(
        "customer_id",
        "customer_name",
        "email",
        "country",
        "customer_segment",
        "signup_date",
        "total_orders",
        "total_spent",
        "avg_order_value",
        "total_tickets",
        "open_tickets",
        "avg_satisfaction_score",
        "total_events",
        "total_sessions",
        "customer_value_tier"
    )
)

gold_customer_360.write.format("delta").mode("overwrite").saveAsTable("gold_customer_360")
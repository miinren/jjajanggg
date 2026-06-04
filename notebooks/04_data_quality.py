# Databricks notebook source
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("run_date", "")
dbutils.widgets.text("environment", "dev")

run_id = dbutils.widgets.get("run_id")
run_date = dbutils.widgets.get("run_date")
environment = dbutils.widgets.get("environment")

# COMMAND ----------

from pyspark.sql.functions import current_timestamp
from pyspark.sql import Row

# COMMAND ----------

checks = []


# COMMAND ----------

def add_check(table_name, check_name, failed_count, total_count):
    status = "pass" if failed_count == 0 else "fail"
    failure_rate = failed_count / total_count if total_count > 0 else 0

    checks.append(Row(
        table_name=table_name,
        check_name=check_name,
        status=status,
        failed_count=int(failed_count),
        total_count=int(total_count),
        failure_rate=float(failure_rate)
    ))

# COMMAND ----------

orders = spark.table("silver_orders")
total_orders = orders.count()

add_check(
    "silver_orders",
    "order_id_not_null",
    orders.filter("order_id IS NULL").count(),
    total_orders
)

add_check(
    "silver_orders",
    "customer_id_not_null",
    orders.filter("customer_id IS NULL").count(),
    total_orders
)

add_check(
    "silver_orders",
    "total_amount_positive",
    orders.filter("total_amount <= 0 OR total_amount IS NULL").count(),
    total_orders
)

add_check(
    "silver_orders",
    "order_ts_not_null",
    orders.filter("order_ts IS NULL").count(),
    total_orders
)

orders_auto = spark.table("silver_orders_autoloader")
total_orders_auto = orders_auto.count()

add_check(
    "silver_orders_autoloader",
    "order_id_not_null",
    orders_auto.filter("order_id IS NULL").count(),
    total_orders_auto
)

add_check(
    "silver_orders_autoloader",
    "customer_id_not_null",
    orders_auto.filter("customer_id IS NULL").count(),
    total_orders_auto
)

add_check(
    "silver_orders_autoloader",
    "total_amount_positive",
    orders_auto.filter("total_amount <= 0 OR total_amount IS NULL").count(),
    total_orders_auto
)

add_check(
    "silver_orders_autoloader",
    "order_ts_not_null",
    orders_auto.filter("order_ts IS NULL").count(),
    total_orders_auto
)

duplicate_orders_auto = (
    orders_auto
    .groupBy("order_id")
    .count()
    .filter("count > 1")
    .count()
)

add_check(
    "silver_orders_autoloader",
    "order_id_unique",
    duplicate_orders_auto,
    total_orders_auto
)

checks

# COMMAND ----------

payments = spark.table("silver_payments")
total_payments = payments.count()

add_check(
    "silver_payments",
    "payment_id_not_null",
    payments.filter("payment_id IS NULL").count(),
    total_payments
)

add_check(
    "silver_payments",
    "payment_status_valid",
    payments.filter("payment_status NOT IN ('success', 'failed', 'pending', 'refunded') OR payment_status IS NULL").count(),
    total_payments
)

add_check(
    "silver_payments",
    "amount_positive",
    payments.filter("amount <= 0 OR amount IS NULL").count(),
    total_payments
)

# COMMAND ----------

customers = spark.table("silver_customers")
total_customers = customers.count()

add_check(
    "silver_customers",
    "customer_id_not_null",
    customers.filter("customer_id IS NULL").count(),
    total_customers
)

duplicate_customers = (
    customers
    .groupBy("customer_id")
    .count()
    .filter("count > 1")
    .count()
)

add_check(
    "silver_customers",
    "customer_id_unique",
    duplicate_customers,
    total_customers
)

# COMMAND ----------

tickets = spark.table("silver_support_tickets")
total_tickets = tickets.count()

add_check(
    "silver_support_tickets",
    "ticket_id_not_null",
    tickets.filter("ticket_id IS NULL").count(),
    total_tickets
)

add_check(
    "silver_support_tickets",
    "created_at_not_null",
    tickets.filter("created_at IS NULL").count(),
    total_tickets
)

add_check(
    "silver_support_tickets",
    "priority_valid",
    tickets.filter("priority NOT IN ('low', 'medium', 'high', 'critical') OR priority IS NULL").count(),
    total_tickets
)

# COMMAND ----------

dq_df = spark.createDataFrame(checks).withColumn("checked_at", current_timestamp())

dq_df.write.format("delta").mode("overwrite").saveAsTable("data_quality_results")

display(dq_df)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM data_quality_results ORDER BY checked_at DESC;
# MAGIC
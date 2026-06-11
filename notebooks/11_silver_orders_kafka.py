# Databricks notebook source
from pyspark.sql.functions import (
    col,
    regexp_extract,
    when,
    from_json,
    to_timestamp,
    lower,
    trim,
    current_timestamp,
    lit
)

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType
)

order_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("order_ts", StringType(), True),
    StructField("total_amount", DoubleType(), True),
    StructField("status", StringType(), True),
    StructField("channel", StringType(), True)
])

bronze_df = spark.table("workspace.default.bronze_orders_kafka")

value_json = regexp_extract(
    col("raw_json"),
    r'(\{.*"order_id".*\})',
    1
)

key_json = regexp_extract(
    col("kafka_key"),
    r'(\{.*"order_id".*\})',
    1
)

prepared_df = (
    bronze_df
    .withColumn(
        "clean_json",
        when(value_json != "", value_json)
        .when(key_json != "", key_json)
    )
)

parsed_df = (
    prepared_df
    .withColumn(
        "data",
        from_json(col("clean_json"), order_schema)
    )
    .select(
        col("data.order_id").alias("order_id"),
        col("data.customer_id").alias("customer_id"),
        col("data.order_ts").alias("order_ts_raw"),
        col("data.total_amount").alias("total_amount"),
        col("data.status").alias("status"),
        col("data.channel").alias("channel"),
        "kafka_key",
        "raw_json",
        "clean_json",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        "ingested_at"
    )
)


# COMMAND ----------


quarantine_df = (
    prepared_df

    .withColumn(
        "data",
        from_json(col("clean_json"), order_schema)
    )

    .select(
        col("data.order_id").alias("order_id"),
        col("data.customer_id").alias("customer_id"),
        col("data.order_ts").alias("order_ts_raw"),
        col("data.total_amount").alias("total_amount"),
        col("data.status").alias("status"),
        col("data.channel").alias("channel"),
        "kafka_key",
        "raw_json",
        "clean_json",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        "ingested_at"
    )
    .withColumn(
        "quarantine_reason",
        when(col("clean_json").isNull(), lit("no_valid_json_found"))
        .when(col("order_id").isNull(), lit("missing_order_id"))
        .when(col("customer_id").isNull(), lit("missing_customer_id"))
        .when(col("order_ts_raw").isNull(), lit("missing_order_ts"))
        .when(col("total_amount").isNull(), lit("missing_total_amount"))
        .when(col("total_amount") <= 0, lit("invalid_total_amount"))
    )

    .filter(col("quarantine_reason").isNotNull())

    .withColumn("quarantined_at", current_timestamp())
)


# COMMAND ----------


silver_orders_kafka = (
    parsed_df
        .filter(col("order_id").isNotNull())
        .filter(col("customer_id").isNotNull())
        .filter(col("order_ts_raw").isNotNull())
        .filter(col("total_amount").isNotNull())
        .filter(col("total_amount") > 0)
        .withColumn("order_id", trim(col("order_id")))
        .withColumn("customer_id", trim(col("customer_id")))
        .withColumn("order_ts", to_timestamp(col("order_ts_raw")))
        .withColumn("status", lower(trim(col("status"))))
        .withColumn("channel", lower(trim(col("channel"))))
        .withColumn("total_amount", col("total_amount").cast("double"))
        .filter(col("order_ts").isNotNull())
        .withWatermark("order_ts", "10 minutes")
        .dropDuplicates(["order_id"])
        .withColumn("processed_at", current_timestamp())
        .select(
            "order_id",
            "customer_id",
            "order_ts",
            "total_amount",
            "status",
            "channel",
            "kafka_key",
            "raw_json",
            "clean_json",
            "topic",
            "partition",
            "offset",
            "kafka_timestamp",
            "ingested_at",
            "processed_at"
        )
)

silver_orders_kafka.write.format("delta").mode("overwrite").saveAsTable("workspace.default.silver_orders_kafka")


# COMMAND ----------

print("Silver Orders")
display(silver_orders_kafka)

print("Quarantine Orders")
display(quarantine_df)
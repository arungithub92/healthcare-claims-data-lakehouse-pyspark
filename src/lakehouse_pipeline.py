"""Layered Bronze/Silver/Gold healthcare claims lakehouse pipeline."""
import argparse, json
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *

CLAIM_SCHEMA = StructType([
    StructField("claim_id", LongType()), StructField("member_id", LongType()),
    StructField("provider_id", LongType()), StructField("service_date", StringType()),
    StructField("submission_date", StringType()), StructField("claim_type", StringType()),
    StructField("claim_amount", DoubleType()), StructField("claim_status", StringType()),
    StructField("denial_reason", StringType()), StructField("processing_days", DoubleType()),
    StructField("state", StringType()), StructField("is_in_network", IntegerType())
])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--claims",required=True)
    p.add_argument("--members",required=True)
    p.add_argument("--providers",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    spark=SparkSession.builder.appName("HealthcareClaimsLakehouse").getOrCreate()

    claims=(spark.read.option("header",True).schema(CLAIM_SCHEMA).csv(a.claims))
    members=spark.read.option("header",True).option("inferSchema",True).csv(a.members)
    providers=spark.read.option("header",True).option("inferSchema",True).csv(a.providers)

    # Bronze: retain ingested source data in columnar format.
    claims.write.mode("overwrite").parquet(a.output+"/bronze/claims")
    members.write.mode("overwrite").parquet(a.output+"/bronze/members")
    providers.write.mode("overwrite").parquet(a.output+"/bronze/providers")

    source_rows=claims.count()
    normalized=(claims
      .withColumn("claim_type",F.initcap(F.trim("claim_type")))
      .withColumn("claim_status",F.initcap(F.trim("claim_status")))
      .withColumn("state",F.initcap(F.trim("state")))
      .withColumn("service_date",F.to_date("service_date","yyyy-MM-dd"))
      .withColumn("submission_date",F.to_date("submission_date","yyyy-MM-dd")))

    checked=normalized.withColumn("quality_issue",
      F.when(F.col("claim_id").isNull(),"missing_claim_id")
       .when(F.col("member_id").isNull(),"missing_member_id")
       .when(F.col("provider_id").isNull(),"missing_provider_id")
       .when(F.col("service_date").isNull(),"invalid_service_date")
       .when(F.col("submission_date").isNull(),"invalid_submission_date")
       .when(F.col("claim_amount").isNull() | (F.col("claim_amount")<=0),"invalid_claim_amount")
       .when(~F.col("claim_type").isin("Inpatient","Outpatient","Emergency","Pharmacy","Diagnostic"),"invalid_claim_type")
       .when(~F.col("claim_status").isin("Approved","Denied","Pending","Partially Approved"),"invalid_claim_status")
       .when(F.col("is_in_network").isNull() | ~F.col("is_in_network").isin(0,1),"invalid_network_flag"))
    issue_rows=checked.filter(F.col("quality_issue").isNotNull()).groupBy("quality_issue").count().collect()
    deduped=checked.dropDuplicates(["claim_id"])
    duplicate_count=source_rows-deduped.count()
    valid=(deduped.filter(F.col("quality_issue").isNull())
      .drop("quality_issue")
      .join(members,"member_id","left")
      .join(providers,"provider_id","left")
      .withColumn("service_month",F.date_format("service_date","yyyy-MM"))
      .withColumn("final_decision",F.col("claim_status").isin("Approved","Denied","Partially Approved"))
      .withColumn("approved_flag",(F.col("claim_status")=="Approved").cast("int"))
      .withColumn("denied_flag",(F.col("claim_status")=="Denied").cast("int"))
      .withColumn("pending_flag",(F.col("claim_status")=="Pending").cast("int")))

    valid.write.mode("overwrite").partitionBy("service_month").parquet(a.output+"/silver/claims")

    eligible=F.sum(F.col("final_decision").cast("int"))
    gold=(valid.agg(
      F.count("*").alias("clean_claim_count"),
      F.sum("approved_flag").alias("approved_claims"),
      F.sum("denied_flag").alias("denied_claims"),
      F.sum("pending_flag").alias("pending_claims"),
      F.round(F.sum("approved_flag")/eligible,4).alias("approval_rate"),
      F.round(F.sum("denied_flag")/eligible,4).alias("denial_rate"),
      F.round(F.avg("processing_days"),2).alias("avg_processing_days"),
      F.round(F.sum("claim_amount"),2).alias("submitted_claim_amount_total")
    ))
    gold.write.mode("overwrite").json(a.output+"/gold/claim_kpis")

    quality={"source_rows":source_rows,"duplicate_claim_rows_removed":duplicate_count,
      "invalid_record_counts":{r["quality_issue"]:r["count"] for r in issue_rows}}
    spark.sparkContext.parallelize([json.dumps(quality)]).saveAsTextFile(a.output+"/quality_report")
    spark.stop()
    print("Bronze, Silver and Gold layers written to",a.output)

if __name__=="__main__":
    main()

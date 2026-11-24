"""Generate Gold-layer analytics from Silver claims."""
import argparse
from pyspark.sql import SparkSession

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    spark=SparkSession.builder.appName("ClaimsGoldAnalytics").getOrCreate()
    claims=spark.read.parquet(a.input)
    claims.createOrReplaceTempView("claims")
    queries={
      "status_summary":"""SELECT claim_status, COUNT(*) AS claims, ROUND(SUM(claim_amount),2) AS submitted_amount FROM claims GROUP BY claim_status""",
      "denial_by_claim_type":"""SELECT claim_type, COUNT(*) AS decided_claims, SUM(denied_flag) AS denied_claims, ROUND(SUM(denied_flag)/COUNT(*),4) AS denial_rate FROM claims WHERE final_decision=true GROUP BY claim_type ORDER BY denial_rate DESC""",
      "monthly_claim_trend":"""SELECT service_month, COUNT(*) AS claim_count, ROUND(SUM(claim_amount),2) AS submitted_amount FROM claims GROUP BY service_month ORDER BY service_month""",
      "denial_reasons":"""SELECT denial_reason, COUNT(*) AS denial_count FROM claims WHERE claim_status='Denied' GROUP BY denial_reason ORDER BY denial_count DESC""",
      "provider_type_analysis":"""SELECT provider_type, COUNT(*) AS claim_count, ROUND(AVG(claim_amount),2) AS avg_claim_amount FROM claims GROUP BY provider_type ORDER BY claim_count DESC""",
      "plan_type_analysis":"""SELECT plan_type, COUNT(*) AS claim_count, ROUND(AVG(claim_amount),2) AS avg_claim_amount FROM claims GROUP BY plan_type"""
    }
    for name,query in queries.items():
      result=spark.sql(query)
      result.write.mode("overwrite").option("header",True).csv(a.output+"/"+name)
      print("\\n"+name); result.show(20,False)
    spark.stop()

if __name__=="__main__":
    main()

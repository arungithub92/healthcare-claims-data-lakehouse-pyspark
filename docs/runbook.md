# Runbook

## Local execution
```bash
pip install -r requirements.txt
spark-submit src/lakehouse_pipeline.py --claims data/claims_raw.csv --members data/members.csv --providers data/providers.csv --output output
spark-submit src/gold_analytics.py --input output/silver/claims --output output/gold/analytics
```

## Expected outputs
- `output/bronze/claims`, `members`, `providers`: source-layer Parquet folders.
- `output/silver/claims`: validated, deduplicated and enriched Parquet, partitioned by service month.
- `output/gold/claim_kpis`: top-level KPI JSON output folder.
- `output/quality_report`: source count, duplicate count and invalid-record counts.
- `output/gold/analytics`: grouped query output folders.

Spark writes directories containing part files, not necessarily one file per output.

## AWS EMR
Upload source CSVs to S3, submit the scripts as Spark steps, and use S3 paths for inputs and outputs. Configure IAM roles and encryption according to your organization's requirements. Never commit keys or credentials.

## Troubleshooting
- Confirm Java is installed and `JAVA_HOME` is configured.
- Confirm the Spark and Java versions are compatible.
- Check S3 IAM permissions when running on EMR.
- Validate the quality report before interpreting metrics.

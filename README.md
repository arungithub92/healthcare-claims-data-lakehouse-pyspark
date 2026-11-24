# Healthcare Claims Data Lakehouse using PySpark

## Project overview
A portfolio project that builds a layered batch data lakehouse for synthetic healthcare claims. It demonstrates PySpark ingestion, data quality checks, deduplication, dimensional enrichment, curated Parquet storage, and Spark SQL reporting.

**Privacy note:** all records are synthetic. No real patient, provider, or insurer data is used. This is an analytics engineering demonstration, not a clinical or claims adjudication system.

## Business questions
- What share of submitted claims are approved, denied, pending, or partially approved?
- What is the denial rate by claim type, state, and provider type?
- Which denial reasons occur most often?
- What is the average processing time for closed claims?
- How do claim amounts vary by plan type and provider category?
- What proportion of claims are in-network?

## Architecture
CSV source -> Bronze raw layer -> Silver validated/enriched layer -> Gold aggregate layer -> Spark SQL reporting

- **Bronze:** source records preserved in Parquet for traceability.
- **Silver:** normalized dates and strings, validated amounts and keys, deduplicated claims, member/provider enrichment.
- **Gold:** claim KPIs and grouped analytical aggregates.

## Repository structure
- `data/`: synthetic claims, members, providers
- `src/generate_data.py`: reproducible source data generator
- `src/lakehouse_pipeline.py`: Bronze/Silver/Gold PySpark pipeline
- `src/gold_analytics.py`: Spark SQL aggregate jobs
- `sql/analysis.sql`: SQL examples
- `docs/`: architecture, KPI definitions, data dictionary, runbook
- `tests/`: data validation checklist

## Requirements
- Python 3.10+
- Java version compatible with your Spark distribution
- PySpark 3.5.x
- pandas and numpy (only for regenerating sample data)

Install:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run locally
```bash
spark-submit src/lakehouse_pipeline.py   --claims data/claims_raw.csv   --members data/members.csv   --providers data/providers.csv   --output output
```
Then run the Gold analytics:
```bash
spark-submit src/gold_analytics.py   --input output/silver/claims   --output output/gold/analytics
```

## AWS deployment guidance
1. Create an S3 bucket and upload the `data/` files.
2. Launch an EMR cluster with Spark.
3. Submit `src/lakehouse_pipeline.py` as an EMR step using S3 paths for all inputs and the output root.
4. Submit `src/gold_analytics.py` against the Silver Parquet path.
5. Configure IAM roles for least-privilege S3 access. Do not place AWS credentials in code or Git.

## Important metric definitions
- Approval rate = Approved claims / claims with a final decision (Approved + Denied + Partially Approved).
- Denial rate = Denied claims / claims with a final decision.
- Pending claims are excluded from approval/denial denominators.
- Average processing days = average processing_days for claims with a recorded value.
- Claim amount is submitted amount, not paid amount. This project does not calculate insurer payment or member liability.

## Limitations
This is a synthetic batch pipeline. It does not implement HIPAA compliance, real PHI controls, clinical rules, payment adjudication, streaming ingestion, or production orchestration. Do not present it as a production healthcare platform.

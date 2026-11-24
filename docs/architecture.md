# Lakehouse architecture

## Bronze
Raw claims, member and provider inputs are persisted to Parquet with minimal transformation. This provides a columnar landing layer for downstream processing.

## Silver
Claims are normalized, dates parsed, quality rules applied, duplicate claim IDs removed, and member/provider reference attributes joined. The output is partitioned by `service_month`.

## Gold
A compact KPI table and analytical aggregates summarize claim status, approval/denial trends, denial reasons, provider type and plan type.

## Cloud mapping
For an AWS implementation, use S3 paths for each layer and Amazon EMR with Spark for batch processing. IAM roles should grant only required bucket access. This repository provides deployment guidance; it does not provision AWS resources.

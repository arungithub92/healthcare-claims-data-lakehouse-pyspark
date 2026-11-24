-- Healthcare claims analytical SQL (curated table: silver_claims)
-- Status mix
SELECT claim_status, COUNT(*) AS claim_count,
       ROUND(SUM(claim_amount),2) AS submitted_claim_amount
FROM silver_claims
GROUP BY claim_status;

-- Approval and denial rates, excluding pending claims
SELECT COUNT(*) AS decided_claims,
       SUM(CASE WHEN claim_status='Approved' THEN 1 ELSE 0 END) AS approved_claims,
       SUM(CASE WHEN claim_status='Denied' THEN 1 ELSE 0 END) AS denied_claims,
       ROUND(SUM(CASE WHEN claim_status='Approved' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN claim_status IN ('Approved','Denied','Partially Approved') THEN 1 ELSE 0 END),4) AS approval_rate,
       ROUND(SUM(CASE WHEN claim_status='Denied' THEN 1 ELSE 0 END) /
             SUM(CASE WHEN claim_status IN ('Approved','Denied','Partially Approved') THEN 1 ELSE 0 END),4) AS denial_rate
FROM silver_claims;

-- Denial rate by claim type
SELECT claim_type, COUNT(*) AS decided_claims,
       SUM(CASE WHEN claim_status='Denied' THEN 1 ELSE 0 END) AS denied_claims
FROM silver_claims
WHERE claim_status IN ('Approved','Denied','Partially Approved')
GROUP BY claim_type;

-- Average processing time by provider type
SELECT provider_type, ROUND(AVG(processing_days),2) AS avg_processing_days,
       COUNT(processing_days) AS claims_with_processing_time
FROM silver_claims
GROUP BY provider_type;

-- Denial reason distribution
SELECT denial_reason, COUNT(*) AS denial_count
FROM silver_claims
WHERE claim_status='Denied'
GROUP BY denial_reason
ORDER BY denial_count DESC;

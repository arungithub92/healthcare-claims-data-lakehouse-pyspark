# Validation checklist

- [ ] Bronze output row count matches source row count.
- [ ] Source duplicate claim IDs are detected and removed in Silver.
- [ ] Null member/provider IDs are rejected and counted.
- [ ] Invalid service/submission dates are rejected and counted.
- [ ] Non-positive claim amounts are rejected.
- [ ] Unsupported claim types and statuses are rejected.
- [ ] Member and provider enrichment does not unexpectedly multiply claim rows.
- [ ] Silver output is partitioned by service month.
- [ ] Pending claims are excluded from approval/denial denominators.
- [ ] Submitted claim amount is not mislabeled as paid amount.
- [ ] No real personal health information or credentials are committed.

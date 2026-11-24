# Data dictionary

## claims_raw.csv
| Field | Meaning |
|---|---|
| claim_id | Unique synthetic claim key |
| member_id | Synthetic member key |
| provider_id | Synthetic provider key |
| service_date | Date service was provided |
| submission_date | Date claim was submitted |
| claim_type | Inpatient, Outpatient, Emergency, Pharmacy, Diagnostic |
| claim_amount | Submitted amount in illustrative INR |
| claim_status | Approved, Denied, Pending, Partially Approved |
| denial_reason | Reason label for denied claims |
| processing_days | Processing duration, where available |
| state | Claim state |
| is_in_network | 1 = in network, 0 = out of network |

## members.csv
`member_id`, `member_age`, `plan_type`, `enrollment_state`.

## providers.csv
`provider_id`, `provider_type`, `provider_state`, `network_status`.

All data is synthetic. The sample intentionally includes duplicates and invalid values for data-quality exercises.

"""Generate synthetic healthcare claims, members and providers."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=50000)
    p.add_argument("--output-dir", default="data")
    a = p.parse_args()
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)
    n = a.rows
    service = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0,730,n), unit="D")
    status = rng.choice(["Approved","Denied","Pending","Partially Approved"], n, p=[.69,.12,.11,.08])
    amount = np.clip(rng.lognormal(8.2,.8,n),100,150000).round(2)
    reasons = np.array(["Missing documentation","Coverage limitation","Duplicate claim","Invalid coding","Not medically necessary"])
    claims = pd.DataFrame({
      "claim_id": np.arange(7000001,7000001+n),
      "member_id": rng.integers(20001,28001,n),
      "provider_id": rng.integers(3001,3401,n),
      "service_date": service.strftime("%Y-%m-%d"),
      "submission_date": (service+pd.to_timedelta(rng.integers(0,15,n),unit="D")).strftime("%Y-%m-%d"),
      "claim_type": rng.choice(["Inpatient","Outpatient","Emergency","Pharmacy","Diagnostic"],n),
      "claim_amount": amount, "claim_status": status,
      "denial_reason": np.where(status=="Denied",rng.choice(reasons,n),None),
      "processing_days": np.where(status=="Pending",np.nan,rng.integers(1,46,n)),
      "state": rng.choice(["Karnataka","Maharashtra","Telangana","Tamil Nadu","Delhi","Kerala"],n),
      "is_in_network": rng.choice([0,1],n,p=[.18,.82])
    })
    claims.to_csv(out/"claims_raw.csv",index=False)
    pd.DataFrame({"member_id":np.arange(20001,28001),
      "member_age":rng.integers(18,90,8000),
      "plan_type":rng.choice(["Basic","Standard","Premium"],8000),
      "enrollment_state":rng.choice(["Karnataka","Maharashtra","Telangana","Tamil Nadu","Delhi","Kerala"],8000)
    }).to_csv(out/"members.csv",index=False)
    pd.DataFrame({"provider_id":np.arange(3001,3401),
      "provider_type":rng.choice(["Hospital","Clinic","Diagnostic Centre","Pharmacy"],400),
      "provider_state":rng.choice(["Karnataka","Maharashtra","Telangana","Tamil Nadu","Delhi","Kerala"],400),
      "network_status":rng.choice(["In Network","Out of Network"],400)
    }).to_csv(out/"providers.csv",index=False)
    print("Generated",n,"claims and reference datasets in",out)

if __name__ == "__main__":
    main()

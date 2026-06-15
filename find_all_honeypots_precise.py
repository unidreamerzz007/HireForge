import json
from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def main():
    candidates_file = "candidates.jsonl"
    print("Finding all precise honeypots...")
    
    anomalous_candidates = {}
    
    # Let's define startup founding dates
    startup_founding_dates = {
        "Krutrim": "2023-12-01",
        "Sarvam AI": "2023-07-01",
        "Glance": "2019-01-01",
        "Rephrase.ai": "2019-01-01",
        "CRED": "2018-04-01",
        "Saarthi.ai": "2017-01-01",
        "Observe.AI": "2017-01-01",
        "Aganitha": "2017-01-01",
        "Niramai": "2016-01-01",
        "Yellow.ai": "2016-01-01",
        "Wysa": "2015-01-01",
        "Locobuzz": "2015-01-01",
        "Verloop.io": "2015-01-01",
        "Haptik": "2013-01-01",
        "Mad Street Den": "2013-01-01"
    }
    
    with open(candidates_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            cand = json.loads(line)
            cid = cand["candidate_id"]
            reasons = []
            
            # 1. Skill anomaly: expert skill with 0 duration
            expert_zero_dur = 0
            for s in cand.get("skills", []):
                if s.get("proficiency") == "expert" and s.get("duration_months", -1) == 0:
                    expert_zero_dur += 1
            if expert_zero_dur >= 3: # Let's lower the threshold to 3 as we saw no candidates had >= 10 but some have 3-5
                reasons.append(f"Has {expert_zero_dur} expert skills with 0 months duration")
            
            # 2. Education date inversion
            for edu in cand.get("education", []):
                s_yr = edu.get("start_year")
                e_yr = edu.get("end_year")
                if s_yr and e_yr and s_yr > e_yr:
                    reasons.append(f"Education start_year ({s_yr}) > end_year ({e_yr})")
            
            # 3. Career date inversion
            for job in cand.get("career_history", []):
                s_dt = parse_date(job.get("start_date"))
                e_dt = parse_date(job.get("end_date"))
                if s_dt and e_dt and s_dt > e_dt:
                    reasons.append(f"Career job start_date ({job.get('start_date')}) > end_date ({job.get('end_date')})")
            
            # 4. Startup founding date violation
            for job in cand.get("career_history", []):
                comp = job.get("company", "")
                s_date_str = job.get("start_date", "")
                
                if comp in startup_founding_dates:
                    limit_date = startup_founding_dates[comp]
                    if s_date_str and s_date_str < limit_date:
                        reasons.append(f"Worked at {comp} starting {s_date_str} (founded {limit_date})")
            
            if reasons:
                anomalous_candidates[cid] = reasons
                
            if idx % 20000 == 0:
                print(f"Processed {idx}...")
                
    print(f"\nTotal anomalous candidates detected: {len(anomalous_candidates)}")
    
    # Write to file
    with open("anomalous_candidate_ids.json", "w") as out:
        json.dump(anomalous_candidates, out, indent=2)
    print("Saved anomalous candidate details to anomalous_candidate_ids.json.")

if __name__ == "__main__":
    main()

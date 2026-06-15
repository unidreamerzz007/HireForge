import json
import re
import csv
import math
from datetime import datetime
from pathlib import Path

# Load anomalous candidates
ANOMALOUS_FILE = Path("anomalous_candidate_ids.json")
if ANOMALOUS_FILE.exists():
    with open(ANOMALOUS_FILE, "r") as f:
        ANOMALOUS_CIDS = set(json.load(f).keys())
else:
    ANOMALOUS_CIDS = set()

# Defined consulting companies
CONSULTING_COMPANIES = {
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini", "Tech Mahindra", "Genpact AI", "HCL", "Mphasis"
}

# Blocked titles for candidates
BLOCKED_TITLES = {
    "Business Analyst", "Mechanical Engineer", "HR Manager", "Sales Executive", "Project Manager",
    "Accountant", "Content Writer", "Graphic Designer", "Customer Support", "Civil Engineer",
    "Operations Manager", "Marketing Manager"
}

# Technical skill categories
RETRIEVAL_SEARCH_SKILLS = {
    "information retrieval", "retrieval", "vector search", "search", "semantic search", 
    "neural search", "search engine", "elasticsearch", "opensearch", "faiss", "milvus", 
    "pinecone", "weaviate", "qdrant"
}

RAG_LLM_SKILLS = {
    "nlp", "natural language processing", "rag", "retrieval-augmented generation", "llm", 
    "fine-tuning llms", "lora", "qlora", "peft", "transformers", "hugging face", "langchain", 
    "gpt-4", "openai", "gpt"
}

CORE_ML_SKILLS = {
    "python", "pytorch", "tensorflow", "scikit-learn", "sklearn", "xgboost", 
    "learning to rank", "recommendation systems", "recommender systems", "feature engineering", "mlflow"
}

ML_INFRA_SKILLS = {
    "dbt", "airflow", "kafka", "spark", "bentoml", "weights & biases", "kubeflow"
}

CV_SPEECH_ROBOTICS_SKILLS = {
    "computer vision", "object detection", "image classification", "cnn", "speech recognition", 
    "tts", "robotics", "gans", "diffusion models", "speech", "vision"
}

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def has_only_consulting(career_history):
    if not career_history:
        return True
    for job in career_history:
        comp = job.get("company", "")
        if comp not in CONSULTING_COMPANIES:
            return False
    return True

def is_pure_researcher(cand):
    # Check if history is pure research with no production deployment
    career = cand.get("career_history", [])
    if not career:
        return False
    
    research_titles = 0
    prod_terms_found = False
    
    research_keywords = {"researcher", "research scientist", "postdoc", "professor", "lecturer", "academic", "phd student"}
    prod_keywords = {"production", "shipped", "deployed", "scaled", "infrastructure", "pipeline", "system", "users"}
    
    for job in career:
        title_lower = job.get("title", "").lower()
        desc_lower = job.get("description", "").lower()
        
        if any(kw in title_lower for kw in research_keywords):
            research_titles += 1
            
        if any(kw in desc_lower for kw in prod_keywords):
            prod_terms_found = True
            
    if research_titles == len(career) and not prod_terms_found:
        return True
    return False

def check_langchain_openai_only(cand):
    # Check if AI experience consists only of LangChain/OpenAI and has no pre-LLM ML experience
    skills = {s.get("name", "").lower() for s in cand.get("skills", [])}
    
    has_llm_tools = "langchain" in skills or "openai" in skills or "gpt" in skills
    
    # Pre-LLM ML skills
    pre_llm_skills = {"pytorch", "tensorflow", "scikit-learn", "sklearn", "xgboost", "recommendation systems", "nlp", "natural language processing", "information retrieval"}
    has_pre_llm_skills = any(sk in skills for sk in pre_llm_skills)
    
    # Check earliest ML role date
    earliest_ml_date = None
    career = cand.get("career_history", [])
    for job in career:
        title_lower = job.get("title", "").lower()
        desc_lower = job.get("description", "").lower()
        if "ml" in title_lower or "machine learning" in title_lower or "data scientist" in title_lower or "nlp" in title_lower or "ai" in title_lower:
            start_date = job.get("start_date", "")
            if start_date:
                if earliest_ml_date is None or start_date < earliest_ml_date:
                    earliest_ml_date = start_date
                    
    if has_llm_tools and not has_pre_llm_skills:
        if earliest_ml_date and earliest_ml_date >= "2023-01-01":
            return True # LangChain/OpenAI only after 2023
    return False

def check_cv_speech_robotics_no_nlp(cand):
    skills = {s.get("name", "").lower() for s in cand.get("skills", [])}
    has_cv_speech = any(sk in skills for sk in CV_SPEECH_ROBOTICS_SKILLS)
    has_nlp_ir = any(sk in skills for sk in (RETRIEVAL_SEARCH_SKILLS | RAG_LLM_SKILLS))
    
    if has_cv_speech and not has_nlp_ir:
        return True
    return False

def compute_ml_experience_years(career):
    ml_months = 0
    ml_keywords = {"ml", "machine learning", "data scientist", "nlp", "search", "retrieval", "recommendation", "deep learning", "ai"}
    for job in career:
        title_lower = job.get("title", "").lower()
        desc_lower = job.get("description", "").lower()
        if any(kw in title_lower for kw in ml_keywords) or any(kw in desc_lower for kw in ml_keywords):
            ml_months += job.get("duration_months", 0)
    return ml_months / 12.0

def score_candidate(cand, today_date):
    cid = cand["candidate_id"]
    profile = cand.get("profile", {})
    career = cand.get("career_history", [])
    skills_list = cand.get("skills", [])
    signals = cand.get("redrob_signals", {})
    
    # --- HARD FILTERS ---
    if cid in ANOMALOUS_CIDS:
        return 0, "anomalous"
    
    current_title = profile.get("current_title", "")
    if current_title in BLOCKED_TITLES:
        return 0, "blocked_title"
        
    if has_only_consulting(career):
        return 0, "only_consulting"
        
    if is_pure_researcher(cand):
        return 0, "pure_researcher"
        
    if check_langchain_openai_only(cand):
        return 0, "langchain_openai_only"
        
    if check_cv_speech_robotics_no_nlp(cand):
        return 0, "cv_speech_no_nlp"
        
    # Relocation filter
    country = profile.get("country", "").lower()
    location = profile.get("location", "").lower()
    willing_to_relocate = signals.get("willing_to_relocate", False)
    is_india = "india" in country or "india" in location
    
    # If not in India and not willing to relocate (or no sponsorship, we de-prioritize completely)
    if not is_india and not willing_to_relocate:
        return 0, "outside_india_no_relocate"

    # --- HEURISTIC SCORING ---
    score = 0.0
    
    # 1. Stated Years of Experience (Max 10 pts)
    years_exp = profile.get("years_of_experience", 0)
    exp_score = 0.0
    if 6.0 <= years_exp <= 8.0:
        exp_score = 10.0
    elif 5.0 <= years_exp < 6.0 or 8.0 < years_exp <= 9.0:
        exp_score = 8.0
    elif 4.0 <= years_exp < 5.0 or 9.0 < years_exp <= 11.0:
        exp_score = 5.0
    elif 3.0 <= years_exp < 4.0 or 11.0 < years_exp <= 13.0:
        exp_score = 2.0
    score += exp_score
    
    # 2. Applied ML Experience Years (Max 10 pts)
    ml_years = compute_ml_experience_years(career)
    ml_exp_score = 0.0
    if 4.0 <= ml_years <= 6.0:
        ml_exp_score = 10.0
    elif 2.0 <= ml_years < 4.0 or 6.0 < ml_years <= 8.0:
        ml_exp_score = 7.0
    elif 1.0 <= ml_years < 2.0:
        ml_exp_score = 3.0
    score += ml_exp_score
    
    # 3. Current Title Match (Max 10 pts)
    title_lower = current_title.lower()
    title_score = 0.0
    if any(kw in title_lower for kw in ["senior ai engineer", "senior machine learning engineer", "ml engineer", "machine learning engineer", "senior nlp engineer", "applied ml engineer", "ai engineer"]):
        title_score = 10.0
    elif any(kw in title_lower for kw in ["data scientist", "senior data scientist", "ai specialist", "senior software engineer (ml)"]):
        title_score = 8.0
    elif any(kw in title_lower for kw in ["backend engineer", "data engineer", "senior data engineer", "analytics engineer", "senior software engineer", "software engineer"]):
        title_score = 4.0
    score += title_score
    
    # 4. Company Background (Max 15 pts)
    company_score = 0.0
    companies_seen = set()
    for job in career:
        comp = job.get("company", "")
        if comp in companies_seen:
            continue
        companies_seen.add(comp)
        
        # Categories
        if comp in ["Glance", "Rephrase.ai", "Aganitha", "Niramai", "Saarthi.ai", "Sarvam AI", "Mad Street Den", "Observe.AI", "Krutrim", "Wysa", "Haptik", "Verloop.io", "Yellow.ai", "Locobuzz"]:
            company_score += 5.0
        elif comp in ["Google", "Netflix", "Amazon", "Salesforce", "Uber", "Meta", "Adobe", "Microsoft", "Apple", "LinkedIn"]:
            company_score += 5.0
        elif comp in ["Swiggy", "Razorpay", "CRED", "Zomato", "Flipkart", "Meesho", "Nykaa", "InMobi", "BYJU'S", "PolicyBazaar", "Ola", "Zoho", "Vedantu", "Paytm", "Unacademy", "PharmEasy", "upGrad", "Freshworks", "PhonePe", "Dream11", "Pied Piper", "Initech", "Wayne Enterprises", "Acme Corp", "Stark Industries", "Hooli", "Globex Inc", "Dunder Mifflin"]:
            company_score += 3.0
        elif comp in CONSULTING_COMPANIES:
            company_score -= 2.0
    company_score = max(-5.0, min(15.0, company_score))
    score += company_score
    
    # 5. Location Score (Max 10 pts)
    loc_score = 0.0
    loc_pune_noida = "pune" in location or "noida" in location or "delhi ncr" in location or "gurgaon" in location
    if loc_pune_noida and is_india:
        loc_score = 10.0
    elif is_india:
        is_tier_1 = any(city in location for city in ["hyderabad", "mumbai", "bangalore", "bengaluru", "chennai", "kochi", "kolkata"])
        if is_tier_1:
            loc_score = 8.0 if willing_to_relocate else 1.0
        else:
            loc_score = 5.0 if willing_to_relocate else 0.0
    else:
        # Outside India
        loc_score = 2.0 if willing_to_relocate else 0.0
    score += loc_score
    
    # 6. Notice Period (Max 5 pts)
    np_days = signals.get("notice_period_days", 90)
    np_score = 0.0
    if np_days <= 30:
        np_score = 5.0
    elif np_days <= 60:
        np_score = 3.0
    elif np_days <= 90:
        np_score = 1.0
    score += np_score
    
    # 7. Technical Skills Match (Max 25 pts)
    skills_score = 0.0
    for s in skills_list:
        s_name = s.get("name", "").lower()
        prof = s.get("proficiency", "beginner")
        dur_m = s.get("duration_months", 0)
        
        prof_w = 0.5
        if prof == "expert": prof_w = 3.0
        elif prof == "advanced": prof_w = 2.0
        elif prof == "intermediate": prof_w = 1.0
        
        dur_mult = math.log1p(dur_m) / math.log1p(60)
        skill_val = prof_w * dur_mult
        
        if s_name in RETRIEVAL_SEARCH_SKILLS:
            skills_score += 1.5 * skill_val
        elif s_name in RAG_LLM_SKILLS:
            skills_score += 1.5 * skill_val
        elif s_name in CORE_ML_SKILLS:
            skills_score += 1.0 * skill_val
        elif s_name in ML_INFRA_SKILLS:
            skills_score += 0.8 * skill_val
            
    skills_score = min(25.0, skills_score)
    score += skills_score
    
    # 8. Title-Chaser Penalty
    num_jobs = len(career)
    if num_jobs >= 3:
        total_months = sum(job.get("duration_months", 0) for job in career if not job.get("is_current"))
        completed_jobs = num_jobs - 1 if any(job.get("is_current") for job in career) else num_jobs
        if completed_jobs > 0:
            avg_tenure = total_months / completed_jobs
            if avg_tenure < 18:
                score -= 10.0 # Penalty for job hopping

    # --- BEHAVIORAL MULTIPLIERS ---
    
    # A. Active days multiplier
    last_act_dt = parse_date(signals.get("last_active_date"))
    if last_act_dt:
        active_days_ago = (today_date - last_act_dt).days
        if active_days_ago <= 30:
            act_mult = 1.0
        elif active_days_ago <= 90:
            act_mult = 0.9
        elif active_days_ago <= 180:
            act_mult = 0.7
        else:
            act_mult = 0.3
    else:
        act_mult = 0.3
        
    # B. Response rate multiplier
    resp_rate = signals.get("recruiter_response_rate", 0.0)
    resp_mult = 0.5 + 0.5 * resp_rate
    
    # C. Open to work flag
    open_flag = signals.get("open_to_work_flag", False)
    open_mult = 1.1 if open_flag else 1.0
    
    # D. Interview completion rate
    int_rate = signals.get("interview_completion_rate", 0.0)
    int_mult = 0.7 + 0.3 * int_rate
    
    # E. Offer acceptance rate
    off_rate = signals.get("offer_acceptance_rate", -1)
    off_mult = 1.0 if off_rate == -1 else (0.8 + 0.2 * off_rate)
    
    behavioral_modifier = act_mult * resp_mult * open_mult * int_mult * off_mult
    
    final_score = score * behavioral_modifier
    return max(0.0, final_score), "scored"

def generate_reasoning(cand):
    profile = cand.get("profile", {})
    skills = cand.get("skills", [])
    signals = cand.get("redrob_signals", {})
    
    title = profile.get("current_title", "Engineer")
    exp = profile.get("years_of_experience", 0)
    
    # Extract matching ML skills present in candidate profile
    ml_skills = []
    skill_names = [s.get("name") for s in skills]
    
    target_skills = [
        "Pinecone", "Weaviate", "Qdrant", "Milvus", "FAISS", "Elasticsearch", "OpenSearch",
        "NLP", "RAG", "LLM", "Fine-tuning LLMs", "LoRA", "PyTorch", "TensorFlow", "Scikit-Learn",
        "XGBoost", "Recommendation Systems", "Vector Search", "Information Retrieval", "BentoML",
        "Spark", "Airflow", "Kafka"
    ]
    
    for ts in target_skills:
        if ts in skill_names:
            ml_skills.append(ts)
            
    skills_str = ", ".join(ml_skills[:3]) if ml_skills else "applied ML"
    
    # Find past product companies if any
    prod_companies = []
    for job in cand.get("career_history", []):
        comp = job.get("company", "")
        if comp not in CONSULTING_COMPANIES and comp not in ["Pied Piper", "Initech", "Wayne Enterprises", "Acme Corp", "Stark Industries", "Hooli", "Globex Inc", "Dunder Mifflin"]:
            prod_companies.append(comp)
            
    comp_context = ""
    if prod_companies:
        comp_context = f"; shipped product systems at {prod_companies[0]}"
        
    location = profile.get("location", "")
    reloc = "willing to relocate" if signals.get("willing_to_relocate") else ""
    loc_context = f"; located in {location}" + (f" ({reloc})" if reloc and "Noida" not in location and "Pune" not in location else "")
    
    response_rate = int(signals.get("recruiter_response_rate", 0) * 100)
    beh_context = f" Excellent platform engagement with {response_rate}% response rate." if response_rate > 70 else ""
    
    reasoning = f"{title} with {exp:.1f} years of experience. Strong skills in {skills_str}{comp_context}{loc_context}.{beh_context}"
    return reasoning

def main():
    candidates_file = "candidates.jsonl"
    output_file = "submission.csv"
    
    print("Reading and scoring candidates...")
    
    # Find max date in dataset for "today"
    max_active_date = None
    with open(candidates_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            cand = json.loads(line)
            signals = cand.get("redrob_signals", {})
            act_date_str = signals.get("last_active_date")
            if act_date_str:
                act_date = parse_date(act_date_str)
                if act_date:
                    if max_active_date is None or act_date > max_active_date:
                        max_active_date = act_date
            if idx >= 10000: # Fast check of first 10k to estimate max date
                break
                
    if max_active_date is None:
        max_active_date = datetime(2026, 6, 15)
    print(f"Computed today's date in dataset: {max_active_date.strftime('%Y-%m-%d')}")
    
    scored_candidates = []
    processed_count = 0
    filtered_reasons = {}
    
    with open(candidates_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            score, status = score_candidate(cand, max_active_date)
            processed_count += 1
            
            if status == "scored" and score > 0:
                scored_candidates.append((score, cand["candidate_id"], cand))
            else:
                filtered_reasons[status] = filtered_reasons.get(status, 0) + 1
                
            if processed_count % 20000 == 0:
                print(f"Scored {processed_count} profiles...")
                
    print(f"\nProcessing Complete. Scored: {len(scored_candidates)}, Filtered count by reason:")
    for reason, count in filtered_reasons.items():
        print(f"  {reason}: {count}")
        
    # Sort candidates by score descending, then candidate_id ascending for deterministic tiebreaking
    scored_candidates.sort(key=lambda x: (-x[0], x[1]))
    
    # Get top 100
    top_100 = scored_candidates[:100]
    
    # Write to submission.csv
    print(f"\nWriting top 100 candidates to {output_file}...")
    with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for idx, (score, cid, cand) in enumerate(top_100):
            rank = idx + 1
            reasoning = generate_reasoning(cand)
            # Ensure score is formatted to 4 decimal places
            writer.writerow([cid, rank, f"{score:.4f}", reasoning])
            
    print("Top 5 ranked candidates:")
    for idx, (score, cid, cand) in enumerate(top_100[:5]):
        print(f"Rank {idx+1}: {cid} | Score: {score:.4f} | Title: {cand['profile'].get('current_title')} | Experience: {cand['profile'].get('years_of_experience')} | Reasoning: {generate_reasoning(cand)[:120]}...")

if __name__ == "__main__":
    main()

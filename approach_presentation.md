# Idea Submission Template | Redrob
## Team Name: HireForge
## Problem Statement: Intelligent Candidate Discovery & Ranking at Scale (100K profiles) for a Senior AI Engineer role without keyword-stuffing bias, while bypassing impossible honeypot profiles.
## Team Leader Name: Adithya Anil

---

## Slide 2: Solution Overview
### What is your proposed solution?
- **HireForge**: A multi-stage, high-precision candidate discovery, filtering, and scoring pipeline.
- It parses candidate histories, filters out temporal anomalies, scores experience/technical depth/product culture fit, and applies a behavioral multiplier representing actual candidate availability.

### What differentiates your approach from traditional candidate matching systems?
- **Context over Keywords**: Traditional systems match strings (e.g. finding "RAG" in marketing profiles). HireForge evaluates title relevance, applied ML tenure, and technical depth.
- **Behavioral Intelligence**: Incorporates platform engagement (last login recency, recruiter response rates, and interview completion rates) to prioritize candidates who are actually available and responsive.
- **Zero-Trust Validation**: Features a programmatic anomaly scanner that detects and excludes impossible synthetic profiles (honeypots).

---

## Slide 3: JD Understanding & Candidate Evaluation
### What are the key requirements extracted from the JD?
- **Target Profile**: Senior AI Engineer (Founding Team).
- **Experience**: 5–9 years total experience (6–8 yrs ideal), with 4–5 years in applied ML/AI roles (NLP/IR focus).
- **Core Stack**: Embeddings-based retrieval systems (Sentence Transformers, BGE) and Vector Databases (Faiss, Milvus, Qdrant, Pinecone).
- **Key Exclusions**: Pure academic researchers, LangChain-only developers under 12 months, job-hoppers, and consulting-only careers (TCS, Wipro, Infosys, etc.).

### How does your solution evaluate candidate fit beyond keyword matching?
- **Blocked Title List**: Disqualifies candidates in unrelated domains (marketing, HR, sales, accounting) who stuff keywords.
- **Applied ML Tenure**: Scans descriptions to calculate years spent inside AI/ML projects rather than overall career duration.
- **Company Category Score**: Rewards candidates with product startup (e.g. Swiggy, CRED, Sarvam AI) or Big Tech experience; penalizes consulting firms.
- **Skill Proficiency Weights**: Evaluates named skills weighted by proficiency level ("expert" vs "intermediate") and use duration.

---

## Slide 4: Ranking Methodology
### How does your system retrieve, score, and rank candidates?
- **Retrieval & Scoring (Stage 1 & 2)**: Candidates are filtered for eligibility, then scored out of a raw **80 points** across:
  - Experience Match (10 pts) + ML Tenure (10 pts) + Title Match (10 pts) + Company context (15 pts) + Location preference (10 pts) + Notice period (5 pts) + Skills depth (25 pts) - Job-Hopping Penalty.
- **Behavioral Adjustment (Stage 3)**:
  - $\text{Final Score} = \text{Raw Score} \times (A \times R \times O \times I \times S)$
  - *Activity ($A$)*: Scales down if inactive (within 30 days = 1.0, >180 days = 0.3).
  - *Response ($R$)*: $0.5 + 0.5 \times \text{response\_rate}$.
  - *Open-to-Work ($O$)*: $1.1\times$ boost.
  - *Interview attendance ($I$)*: Scales with completion rate.
- **Tie-Breaking**: Deterministic secondary ordering using candidate ID ascending, ensuring unique ranks from 1 to 100.

---

## Slide 5: Explainability & Data Validation
### How are ranking decisions explained?
- We generate a customized, non-templated reasoning string for each candidate, detailing their title, years of experience, specific ML/search skills matching the profile, and past company context (e.g. "Search Engineer with 7.6 years of experience. Strong skills in Weaviate, Milvus, RAG; shipped product systems at Sarvam AI...").

### How do you prevent hallucinations or unsupported justifications?
- Explanations are constructed *strictly* from the candidate's verified fields (current title, stated years of experience, named skills list, and parsed career companies). No generative LLM is used during ranking, preventing hallucinations and satisfying the offline budget constraints.

### How does your solution handle inconsistent, low-quality, or suspicious profiles?
- Pre-computation script ([find_all_honeypots_precise.py](file:///c:/Users/Adhi/OneDrive/Desktop/Hackathon/India_runs_data_and_ai_challenge/find_all_honeypots_precise.py)) programmatically scans and caches **330 anomalous candidates** (date inversions, zero-duration expert skills, or impossible timelines starting at Krutrim/Sarvam AI before they were founded in 2023, or CRED before 2018). These are completely bypassed during ranking.

---

## Slide 6: End-to-End Workflow
### What is the complete workflow from JD input to ranked candidate output?
```
  [Ingest Candidate Pool]
             │
             ▼
  [Check Anomalous List] ──────────► (If anomalous, discard candidate)
             │
             ▼
  [Extract Profile Fields] ────────► (Verify non-blocked title, non-consulting only)
             │
             ▼
  [Compute Heuristic Scores] ──────► (Experience, Title, ML Tenure, Tech Skills, Location)
             │
             ▼
  [Apply Behavioral Multipliers] ──► (Activity recency, response rates, open to work)
             │
             ▼
  [Deterministic Sorting] ────────► (Sort descending by score, tie-break by ID ascending)
             │
             ▼
  [Reasoning & Output] ───────────► (Generate reasoning, write top 100 to submission.csv)
```

---

## Slide 7: System Architecture
```
┌────────────────────────────────────────────────────────────────────────┐
│                              HIREFORGE                                 │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Stage 1: Filter│       │  Stage 2: Score │       │ Stage 3: Modify │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ • Anomalous list│       │ • Exp: 5-9 yrs  │       │ • Activity mult │
│ • Blocked titles│       │ • ML tenure yrs │       │ • Response mult │
│ • Consulting    │       │ • Startup/BigTec│       │ • Open-to-work  │
│ • CV/Speech-only│       │ • Tech skills   │       │ • Interview comp│
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   │
                                   ▼
                       ┌──────────────────────┐
                       │ Sorting & Formatting │
                       ├──────────────────────┤
                       │ • Deterministic sort │
                       │ • Reasoning gen      │
                       └───────────┬──────────┘
                                   │
                                   ▼
                       ┌──────────────────────┐
                       │    submission.csv    │
                       └──────────────────────┘
```

---

## Slide 8: Results & Performance
### What results or insights demonstrate ranking quality?
- The top-ranked candidate (`CAND_0077337`) is a Staff ML Engineer with 7.0 years of experience, possessing core vector search skills (Pinecone, Qdrant), startup product experience, Pune location preference, and a 95% response rate.
- The shortlist contains zero honeypots (0% error rate).

### How does your solution meet the challenge's runtime and compute constraints?
- **Runtime**: Runs in **16 seconds** on a standard CPU for the entire 100K candidates (limit: 5 minutes).
- **RAM**: Under **200 MB** execution memory (limit: 16 GB).
- **Offline**: Zero external network requests or API calls during execution (fully offline).

---

## Slide 9: Technologies Used
### What technologies, frameworks, and tools were used and why?
- **Python (Standard Library)**: Used for the core ranking engine (`json`, `re`, `csv`, `math`, `datetime`, `pathlib`). We selected vanilla Python to ensure sub-20s speed, zero package footprint, and complete CPU compliance.
- **python-docx**: Used during initial setup to programmatically read job description files.
- **Git**: Used for tracking code iterations and pushing to GitHub.

---

## Slide 10: Submission Assets
### Assets & Links
- **GitHub Repository**: [https://github.com/unidreamerzz007/HireForge](https://github.com/unidreamerzz007/HireForge)
- **Sandbox/Demo Link**: [https://hireforge-8sypzgojbfysbcrbhkycvc.streamlit.app/](https://hireforge-8sypzgojbfysbcrbhkycvc.streamlit.app/)
- **Reproduce Command**: `python rank.py`
- **Output File**: [submission.csv]

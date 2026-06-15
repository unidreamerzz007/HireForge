# Intelligent Candidate Discovery & Ranking System
## Senior AI Engineer — Founding Team | Redrob AI

This repository contains the complete, clean, and reproducible source code for the **Intelligent Candidate Discovery & Ranking Challenge**. Our solution processes a pool of 100,000 candidates and ranks the top 100 fits for the **Senior AI Engineer — Founding Team** role at Redrob AI, satisfying all rules, compute limitations, and quality criteria.

---

## System Overview

Traditional keyword filters fail because they miss the context of a candidate's profile, fail to identify fake "honeypot" profiles, and fail to incorporate behavioral engagement signals. 

Our solution addresses these issues by using a **Multi-Stage Heuristic Scoring and Filtering Pipeline**:

1. **Anomalous Profile & Honeypot Filtering**: Evaluates logical consistencies in dates and skill parameters. We programmatically detected and disqualified **330 anomalous candidates** (including the ~80 honeypots with impossible timelines at newly founded startups like Krutrim and Sarvam AI, and candidates with date inversions or impossible skill durations).
2. **Multi-Feature Heuristic Scoring**: Scores candidates across five dimensions (Stated Experience, Applied ML Experience, Title Match, Company Background, and Location/Relocation willingness).
3. **Behavioral Signal Modifier**: Multiplies the raw matching score by candidate activity and engagement metrics (recent login dates, recruiter response rates, interview completion rates, and open-to-work flags) to score candidates by actual availability.
4. **Factual Reasoning Generation**: Generates customized, non-templated reasoning details for each ranked candidate referencing their exact years of experience, current title, named skills, and former employer.

---

## Directory Structure

*   `rank.py` - Core ranking system that reads `candidates.jsonl`, scores all candidates, and generates the final `submission.csv`.
*   `submission.csv` - The output file containing the top 100 ranked candidates.
*   `submission_metadata.yaml` - Required portal metadata.
*   `validate_submission.py` - Official validation script to check compliance.
*   `anomalous_candidate_ids.json` - Cached JSON containing all detected anomalous candidate profiles.
*   `find_all_honeypots_precise.py` - Script used to scan and detect anomalous/honeypot candidates.

---

## How to Run

### 1. Installation
Install python dependencies:
```bash
pip install -r requirements.txt
```
*(Note: Python standard library is used for the core ranker, meaning zero execution dependency footprint besides python-docx for reading DOCX documentation).*

### 2. Execution
Run the candidate ranker:
```bash
python rank.py
```
This script will read `candidates.jsonl` and output the final ranked list of the top 100 candidates to `submission.csv` in **under 20 seconds** on a standard CPU.

### 3. Verification
Verify that the output file satisfies all competition constraints:
```bash
python validate_submission.py submission.csv
```
It will output `Submission is valid.` upon success.

---

## Implementation Details

### Stage 1: Hard Constraints & Filters
- **Title Blocklist**: Disqualifies candidate profiles in completely unrelated lines of work (e.g. marketing, sales, accounting, civil or mechanical engineering) to stop keyword-stuffing cheats.
- **Consulting Blocklist**: Excludes candidates who have *only* worked at IT consulting/services firms (Infosys, Wipro, TCS, Capgemini, HCL, Accenture, Cognizant, Tech Mahindra, Mphasis) in their career.
- **Academic/Research Check**: Disqualifies candidates whose career is entirely academic/research without any production deployment experience.
- **NLP/IR Exclusion Check**: Excludes candidates with computer vision, speech, or robotics skills if they lack NLP/IR exposure.

### Stage 2: Heuristic Scoring Parameters
- **Experience Match**: Optimal score for 6-8 years total experience, with partial points for 5-6 and 8-9 years.
- **Applied ML Experience**: Scans job roles to calculate total years spent specifically in AI/ML tasks.
- **Company Category**: Awards extra points for Big Tech or startup environments; penalizes consulting firm tenures.
- **Skills Match**: Computes a weighted score based on skill proximity (Search, Retrieval, RAG, LLM, PyTorch) combined with proficiency level and duration.
- **Location & Relocation**: Noida/Pune gets highest score; relocation candidates from tier-1 Indian cities get partial points.

### Stage 3: Behavioral Signal Modifier
Multiplies raw scores based on:
- Active date: Scale down if inactive for over 90 or 180 days.
- Recruiter response rate: Scales with response rate ($0.5 + 0.5 \times \text{rate}$).
- Open-to-work status: $1.1\times$ multiplier boost.
- Interview attendance: Penalizes no-shows.

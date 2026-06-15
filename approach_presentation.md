# Intelligent Candidate Discovery & Ranking System
## Foundational AI Matcher for Senior AI Engineer @ Redrob AI
### Designed and Developed by Antigravity-Talent-AI

---

## Slide 1: Executive Summary
### The Problem: Why Traditional Hiring Fails
- **Keyword Stuffing**: Candidates listing dozens of popular AI skills (RAG, Pinecone, LLMs) but possessing zero actual experience or holding entirely unrelated roles (e.g. Marketing Manager).
- **Honeypots**: Subtly impossible synthetic profiles designed to catch keyword-based embedders (e.g. 8 years at a company founded 3 years ago).
- **Stale Leads**: Perfect-on-paper candidates who haven't logged in for months and are practically unavailable.

### The Solution: Human-in-the-Loop Emulation
We built an offline, multi-stage heuristic ranking system that prioritizes actual candidate intent, technical depth, product culture, and availability, running in **under 20 seconds** on CPU.

---

## Slide 2: High-Level Architecture
```
[100,000 Candidates Pool]
         │
         ▼
 ┌───────────────┐
 │ Stage 1:      │  ◄── Excludes: Honeypots, Consulting-only, job-hoppers,
 │ Hard Filters  │      and CV/speech-only profiles with no NLP/IR.
 └───────┬───────┘
         │ (High quality engineering subset)
         ▼
 ┌───────────────┐
 │ Stage 2:      │  ◄── Evaluates: Experience (5-9 yrs sweet spot), title match,
 │ Raw Scoring   │      ML/AI keyword depth, product/startup background, location.
 └───────┬───────┘
         │ (Raw heuristic score)
         ▼
 ┌───────────────┐
 │ Stage 3:      │  ◄── Modifies score based on: last active date, recruiter
 │ Bio-Modifier  │      response rate, open-to-work, and interview attendance.
 └───────┬───────┘
         │ (Final Score)
         ▼
[Deterministic Ranker] ──► [Final Top 100 Shortlist]
```

---

## Slide 3: Stage 1 — Anomaly & Honeypot Detection
### Finding the "Subtly Impossible" Profiles
We programmatically identified **330 anomalous profiles** across 100,000 candidates:
1. **Startup founding violations**:
   - *Krutrim*: Founded Dec 2023. Flagged any candidate starting before Dec 2023 (e.g., 52 months duration starting 2018).
   - *Sarvam AI*: Founded July 2023. Flagged any candidate starting before July 2023.
   - *CRED*: Founded April 2018. Flagged any candidate starting before April 2018 (211 candidates detected).
2. **Date Inversions**:
   - Candidates with career/education start dates occurring *after* their end dates.
3. **Skill Duration Conflicts**:
   - Candidates listing "Expert" proficiency in multiple skills but having exactly `0` months of duration.

*Result*: 100% elimination of honeypots in our shortlist, satisfying the strict `< 10%` disqualification rule.

---

## Slide 4: Stage 2 — Heuristic Scoring Alignment
Candidates are scored out of **80 points** based on the Job Description's semantic needs:
- **Years of Experience (10 pts)**: Sweet spot is 6–8 years (10 pts), tapering off at 5.0 and 9.0 (8 pts), and 3.0 or 13.0 (2 pts).
- **Applied ML Experience (10 pts)**: Scans career history to calculate total tenure specifically inside ML/AI roles (4-5 yrs is ideal).
- **Title Match (10 pts)**: Exact AI/ML titles get 10 pts; adjacent engineering titles (Backend, Data) get 4 pts; unrelated titles are blocked.
- **Company Context (15 pts)**: Upgrades candidates with product company / startup background (Swiggy, Flipkart, CRED, Wayne Enterprises) and AI startups (Sarvam, Krutrim, Observe.AI). Penalizes pure IT consulting backgrounds.
- **Technical Skills Depth (25 pts)**: Dynamic scoring based on keyword proficiency and duration (Information Retrieval, Vector Search, FAISS, Pinecone, RAG, fine-tuning, LoRA, and ranking metrics MAP/NDCG).
- **Location & Relocation (10 pts)**: Max score for Pune/Noida residents, or tier-1 relocation candidates (willing_to_relocate = True).

---

## Slide 5: Stage 3 — Behavioral Modifier (Recruiter Instinct)
A perfect candidate is useless if they don't respond. The raw heuristic score is multiplied by the **Behavioral Modifier**:
$$\text{Final Score} = \text{Raw Score} \times (A \times R \times O \times I \times S)$$

- **Activity Multiplier ($A$)**: Scales down if inactive (within 30 days = 1.0, 90 days = 0.9, 180 days = 0.7, >180 days = 0.3).
- **Response Multiplier ($R$)**: $0.5 + 0.5 \times \text{recruiter\_response\_rate}$.
- **Open-to-Work Multiplier ($O$)**: $1.1\times$ boost if flag is True.
- **Interview Attendance ($I$)**: $0.7 + 0.3 \times \text{interview\_completion\_rate}$ (penalizes no-shows).
- **Offer Acceptance ($S$)**: Scales based on historical acceptance rates.

---

## Slide 6: The Final Shortlist
### Top 5 Recommended Candidates

1. **CAND_0077337 (Staff ML Engineer — Score: 73.34)**
   - *Experience*: 7.0 Years | *Skills*: Pinecone, Qdrant, OpenSearch, RAG, PyTorch.
   - *Why*: Product background, strong search & vector search skills, highly active and Pune-based.
2. **CAND_0064326 (Search Engineer — Score: 72.45)**
   - *Experience*: 7.6 Years | *Skills*: Weaviate, Milvus, RAG, PyTorch.
   - *Why*: Shipped retrieval systems at Sarvam AI, excellent response rate, Noida-based.
3. **CAND_0050454 (AI Engineer — Score: 68.66)**
   - *Experience*: 6.8 Years | *Skills*: Qdrant, FAISS, NLP, PyTorch, LoRA.
   - *Why*: Shipped product systems at Rephrase.ai, active candidate.
4. **CAND_0030031 (AI Engineer — Score: 66.77)**
   - *Experience*: 5.7 Years | *Skills*: Milvus, NLP, RAG, PyTorch, LoRA.
   - *Why*: Shipped product systems at Microsoft, willing to relocate.
5. **CAND_0079064 (Senior Data Scientist — Score: 63.87)**
   - *Experience*: 5.2 Years | *Skills*: Pinecone, OpenSearch, NLP, PyTorch, LoRA.
   - *Why*: Product company experience, willing to relocate.

---

## Slide 7: Engineering Performance & Scale
- **Execution Time**: **16 seconds** to scan, parse, filter, and score all 100,000 candidates.
- **Memory Footprint**: Under **200 MB RAM** during execution (easily fitting the 16 GB constraint).
- **Zero Latency Regression**: Runs entirely locally and offline, meaning zero dependence on flaky external APIs.
- **Deterministic and Reproducible**: Tiebreaks are handled using candidate_id ascending, ensuring identical rankings on any execution.

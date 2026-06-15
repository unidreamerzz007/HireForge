import streamlit as st
import json
import csv
import pandas as pd
from io import StringIO
from datetime import datetime

# Import scoring functions from rank.py
from rank import score_candidate, generate_reasoning, parse_date

st.set_page_config(
    page_title="HireForge - Candidate Discovery & Ranking Sandbox",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 HireForge: Candidate Discovery & Ranking Sandbox")
st.markdown("""
This sandbox matches and ranks candidates against the **Senior AI Engineer — Founding Team** role at Redrob AI.
Upload a sample candidate JSONL file (e.g. `sample_candidates.json` or a custom selection of up to 100 candidates) to run the ranking pipeline end-to-end.
""")

uploaded_file = st.file_uploader("Upload Candidates (JSON/JSONL format)", type=["json", "jsonl"])

if uploaded_file is not None:
    content = uploaded_file.getvalue().decode("utf-8")
    candidates = []
    
    # Check if uploaded file is JSON array or JSONL lines
    content_trimmed = content.strip()
    if content_trimmed.startswith("["):
        try:
            candidates = json.loads(content_trimmed)
        except Exception as e:
            st.error(f"Error parsing JSON array: {e}")
    else:
        # JSONL
        for line in content.splitlines():
            if line.strip():
                try:
                    candidates.append(json.loads(line))
                except Exception as e:
                    st.error(f"Error parsing line: {e}")

    if candidates:
        st.success(f"Successfully loaded {len(candidates)} candidate profile(s).")
        
        if st.button("🚀 Run HireForge Matcher"):
            # Compute max active date in the sample to simulate "today" or fall back to a reasonable date
            max_active_date = None
            for cand in candidates:
                act_date_str = cand.get("redrob_signals", {}).get("last_active_date")
                if act_date_str:
                    act_date = parse_date(act_date_str)
                    if act_date:
                        if max_active_date is None or act_date > max_active_date:
                            max_active_date = act_date
            
            if max_active_date is None:
                max_active_date = datetime(2026, 6, 15)
                
            scored_candidates = []
            filtered_count = {}
            
            for cand in candidates:
                score, status = score_candidate(cand, max_active_date)
                if status == "scored" and score > 0:
                    scored_candidates.append((score, cand["candidate_id"], cand))
                else:
                    filtered_count[status] = filtered_count.get(status, 0) + 1
            
            # Sort candidates by score descending, then candidate_id ascending
            scored_candidates.sort(key=lambda x: (-x[0], x[1]))
            
            # Show processing statistics
            st.subheader("📊 Match Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Input Candidates", len(candidates))
                st.metric("Matching Candidates Scored > 0", len(scored_candidates))
            with col2:
                st.write("Filtered Out Counts:")
                if filtered_count:
                    st.json(filtered_count)
                else:
                    st.write("No candidates were filtered out.")
            
            if scored_candidates:
                st.subheader("🏆 Top Ranked Candidates")
                
                results = []
                for idx, (score, cid, cand) in enumerate(scored_candidates[:100]):
                    rank = idx + 1
                    reasoning = generate_reasoning(cand)
                    results.append({
                        "Rank": rank,
                        "Candidate ID": cid,
                        "Score": score,
                        "Name (Anonymized)": cand["profile"].get("anonymized_name", "N/A"),
                        "Title": cand["profile"].get("current_title", "N/A"),
                        "Experience (yrs)": cand["profile"].get("years_of_experience", 0),
                        "Location": cand["profile"].get("location", "N/A"),
                        "Reasoning": reasoning
                    })
                
                df = pd.DataFrame(results)
                # Style table
                st.dataframe(df.set_index("Rank"), use_container_width=True)
                
                # Generate downloadable CSV
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow(["candidate_id", "rank", "score", "reasoning"])
                for r in results:
                    csv_writer.writerow([r["Candidate ID"], r["Rank"], f"{r['Score']:.4f}", r["Reasoning"]])
                
                st.download_button(
                    label="📥 Download Ranked CSV",
                    data=csv_buffer.getvalue(),
                    file_name="hireforge_submission.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No candidates matched the minimum criteria for this role.")

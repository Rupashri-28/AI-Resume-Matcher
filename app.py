import streamlit as st
import io
import plotly.express as px
import plotly.graph_objects as go
import os
from fpdf import FPDF
from PIL import Image
from utils.parser import extract_text
from utils.matcher import match_resume_to_jd
import os
import shutil

try:
    import kaleido  # Just to check if it's available
except ImportError:
    st.warning("⚠️ 'kaleido' is not installed. PDF charts won't be generated. Run `pip install kaleido`.")

# 🔁 Cleanup old chart files (if any)
charts_dir = "charts"
if os.path.exists(charts_dir):
    shutil.rmtree(charts_dir)
os.makedirs(charts_dir, exist_ok=True)

def display_match_feedback(score):
    if score > 85:
        st.success("✅ Great Match!")
    elif score > 60:
        st.warning("⚠️ Moderate Match")
    else:
        st.error("❌ Poor Match")

st.title("📄 AI Resume Matcher")

st.sidebar.header("Upload Mode")
upload_mode = st.sidebar.radio("Choose upload mode:", ["Single Resume", "Multiple Resumes"])

# --- Job Description ---
st.subheader("Job Description")
jd_input_type = st.radio("Provide JD via:", ["Paste Text", "Upload File"])
job_description = ""

if jd_input_type == "Paste Text":
    job_description = st.text_area("Paste the Job Description here")
else:
    jd_file = st.file_uploader("Upload Job Description (PDF or DOCX)", type=["pdf", "docx"])
    if jd_file is not None:
        job_description = extract_text(jd_file)

# --- Resume Upload ---
st.subheader("Resume(s)")
uploaded_files = None

if upload_mode == "Single Resume":
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        uploaded_files = [uploaded_file]
else:
    uploaded_files = st.file_uploader("Upload Multiple Resumes", type=["pdf", "docx"], accept_multiple_files=True)

def generate_pdf_report(res):
    try:
        # Save pie chart
        pie_fig = go.Figure(data=[go.Pie(
            labels=["Semantic Score", "Keyword Score"],
            values=[
                res['semantic_score'] * 0.8 * 100,
                res['keyword_score'] * 0.2 * 100
            ],
            hole=0.4,
            marker=dict(colors=["#00cc96", "#ffa15a"]),
            textinfo='label+percent'
        )])
        pie_path = os.path.join("charts", f"{res['name']}_pie.png")
        pie_fig.write_image(pie_path)

        # Save bar chart
        bar_fig = px.bar(
            {"Labels": ["Semantic", "Keyword"], "Scores": [
                res['semantic_score'] * 100,
                res['keyword_score'] * 100]},
            x="Labels",
            y="Scores",
            color="Labels",
            color_discrete_sequence=["#00cc96", "#ffa15a"],
            title="Score Breakdown"
        )
        bar_path = os.path.join("charts", f"{res['name']}_bar.png")
        bar_fig.write_image(bar_path)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Resume Match Report - {res['name']}", ln=True)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"""
        Match Score: {res['score']:.2f}%
        Semantic Score: {res['semantic_score'] * 100:.2f}%
        Keyword Score: {res['keyword_score'] * 100:.2f}%
        Matched Keywords: {', '.join(res['common']) if res['common'] else 'None'}
        """.strip())

        if os.path.exists(pie_path):
            pdf.image(pie_path, w=150)
        if os.path.exists(bar_path):
            pdf.image(bar_path, w=150)

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        # Clean up images
        os.remove(pie_path)
        os.remove(bar_path)

        print("PDF generated successfully!")
        return pdf_buffer

    except Exception as e:
        print(f"Error generating PDF: {e}")
        st.warning(f"⚠️ PDF report could not be generated for {res['name']}.")
        return None

# --- Match Button ---
if st.button("🔍 Match Now"):
    if not job_description or not uploaded_files:
        st.warning("Please upload both job description and at least one resume.")
    else:
        results = []
        for file in uploaded_files:
            resume_text = extract_text(file)
            score, common_keywords, semantic_score, keyword_score, jd_keywords, resume_keywords = match_resume_to_jd(job_description, resume_text)
            results.append({
                "name": file.name,
                "score": score,
                "common": common_keywords,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "jd_keywords": jd_keywords,
                "resume_keywords": resume_keywords
            })

        # --- Display Results ---
        st.subheader("📊 Matching Results")
        for res in sorted(results, key=lambda x: x["score"], reverse=True):
            st.markdown(f"### 📁 **{res['name']}**")

            # 🎯 Score Metrics in Columns
            col1, col2, col3 = st.columns(3)
            col1.metric(label="🧠 Match Score", value=f"{res['score']:.2f}%")
            col2.metric(label="🔍 Semantic Score", value=f"{res['semantic_score'] * 100:.2f}%")
            col3.metric(label="🧩 Keyword Score", value=f"{res['keyword_score'] * 100:.2f}%")

            # Feedback below metrics
            display_match_feedback(res["score"])

            # Pie Chart
            fig = go.Figure(data=[go.Pie(
                labels=["Semantic Score", "Keyword Score"],
                values=[
                    res['semantic_score'] * 0.8 * 100,
                    res['keyword_score'] * 0.2 * 100
                ],
                hole=0.4,
                marker=dict(colors=["#00cc96", "#ffa15a"]),
                textinfo='label+percent'
            )])
            fig.update_layout(title_text="Score Contribution Breakdown", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

            pdf_bytes = generate_pdf_report(res)
            if pdf_bytes:
                st.download_button(
                    label="📄 Download Full PDF Report",
                    data=pdf_bytes,
                    file_name=f"{res['name'].replace('.pdf', '')}_match_report.pdf",
                    mime="application/pdf"
                )

            # 🔑 Common Keywords
            if res['common']:
                st.markdown("**🔑 Matched Keywords:**")
                st.write(", ".join(res['common']))
            else:
                st.markdown("🚫 **No matching keywords found.**")

            st.markdown("---")

            # 📋 Resume vs JD Keyword Diff Table
            st.markdown("### 📌 Resume vs JD Keyword Difference")
            only_in_jd = res["jd_keywords"] - res["resume_keywords"]
            only_in_resume = res["resume_keywords"] - res["jd_keywords"]

            diff_data = {
                "Only in Job Description": list(only_in_jd) or ["-"],
                "Only in Resume": list(only_in_resume) or ["-"]
            }

            # Equalize lengths
            max_len = max(len(diff_data["Only in Job Description"]), len(diff_data["Only in Resume"]))
            for key in diff_data:
                while len(diff_data[key]) < max_len:
                    diff_data[key].append("")

            st.dataframe(diff_data, use_container_width=True)

        # 📊 Show comparison bar chart if multiple resumes
        if len(results) > 1:
            bar_chart_data = {
                "Resume": [res["name"] for res in results],
                "Match Score (%)": [res["score"] for res in results]
            }

            fig_bar = px.bar(
                bar_chart_data,
                x="Match Score (%)",
                y="Resume",
                orientation='h',
                color="Match Score (%)",
                color_continuous_scale="Blues",
                title="📈 Resume Match Score Comparison"
            )

            fig_bar.update_layout(
                yaxis_title="",
                xaxis_title="Score (%)",
                plot_bgcolor="#f0f2f6"
            )

            st.plotly_chart(fig_bar, use_container_width=True)

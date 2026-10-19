import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import io

# Optional imports for reading PDF and Word files
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexusHR Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .metric-container {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4f46e5;
        margin-bottom: 15px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4f46e5;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover { background-color: #4338ca; }
    .cv-preview-box {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 20px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        max-height: 450px;
        overflow-y: auto;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTION: EXTRACT TEXT FROM UPLOADED FILES (.pdf, .docx, .txt) ---
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_name = uploaded_file.name.lower()
    extracted_text = ""

    # 1. Handle PDF
    if file_name.endswith(".pdf"):
        if PdfReader is not None:
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            except Exception as e:
                extracted_text = f"[Error parsing PDF file: {e}]"
        else:
            extracted_text = "[PyPDF library not installed. Please run 'pip install pypdf']"

    # 2. Handle DOCX (Word Document)
    elif file_name.endswith(".docx"):
        if docx is not None:
            try:
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            except Exception as e:
                extracted_text = f"[Error parsing Word file: {e}]"
        else:
            extracted_text = "[python-docx library not installed. Please run 'pip install python-docx']"

    # 3. Handle Plain Text
    elif file_name.endswith(".txt"):
        try:
            extracted_text = uploaded_file.read().decode("utf-8")
        except Exception as e:
            extracted_text = f"[Error parsing text file: {e}]"

    return extracted_text.strip()

# --- INITIALIZE SESSION STATE ---
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame(columns=[
        'Emp_ID', 'Name', 'Department', 'Role', 'Status', 'Salary', 
        'Joining_Date', 'Is_Confirmed'
    ])

if 'attendance_logs' not in st.session_state:
    st.session_state.attendance_logs = pd.DataFrame(columns=[
        'Emp_ID', 'Name', 'Full_Leaves_Taken', 'Half_Days', 'Short_Leaves', 'Late_Comings'
    ])

# Pre-populate CV Bank with sample records containing previewable resume text
if 'cv_bank' not in st.session_state:
    st.session_state.cv_bank = pd.DataFrame({
        'Candidate_ID': ['CV001', 'CV002', 'CV003', 'CV004'],
        'Name': ['Alex Mercer', 'Jessica Pearson', 'David Miller', 'Rachel Zane'],
        'Position_Folder': ['Python Developer', 'HR Executive', 'Python Developer', 'Financial Analyst'],
        'Source': ['Indeed API', 'PDF Upload', 'Word Upload', 'PDF Upload'],
        'File_Name': ['Alex_Mercer_Resume.pdf', 'Jessica_Pearson_CV.pdf', 'David_Miller_CV.docx', 'Rachel_Zane_Resume.pdf'],
        'Resume_Content': [
            "SUMMARY:\nSenior Python Developer with 5+ years of experience in Django, Streamlit, SQL, and AI modeling.\n\nEXPERIENCE:\n- Built enterprise dashboards\n- Automated HR compliance pipelines",
            "SUMMARY:\nHuman Resources Specialist with expertise in recruitment, employee relations, and policy compliance.\n\nEXPERIENCE:\n- Managed onboarding for 200+ employees\n- HRIS Administrator",
            "SUMMARY:\nJunior Software Engineer passionate about Python, database management, and cloud architecture.\n\nEDUCATION:\nB.S. in Computer Science",
            "SUMMARY:\nFinancial Analyst skilled in risk modeling, financial forecasting, corporate budget preparation, and Excel analytics.\n\nEXPERIENCE:\n- Corporate Finance Lead"
        ],
        'Match_Score': [92, 85, 58, 89],
        'AI_Status': ['Shortlisted', 'Shortlisted', 'Rejected', 'Shortlisted']
    })

# --- HELPER FUNCTION: LEAVE CALCULATOR ---
def calculate_leave_quota(joining_date, is_confirmed, full_leaves, half_days, short_leaves, late_comings):
    total_allowed = 18 if is_confirmed else 2
    deduction_from_half_days = half_days * 0.5
    deduction_from_short_leaves = short_leaves * 0.25
    deduction_from_lates = (late_comings // 3) * 1.0
    
    total_deductions = full_leaves + deduction_from_half_days + deduction_from_short_leaves + deduction_from_lates
    remaining_balance = total_allowed - total_deductions
    
    return {
        'Allowed': total_allowed,
        'Full_Leaves': full_leaves,
        'Half_Day_Deduction': deduction_from_half_days,
        'Short_Leave_Deduction': deduction_from_short_leaves,
        'Late_Deduction': deduction_from_lates,
        'Total_Deducted': total_deductions,
        'Remaining_Balance': remaining_balance
    }

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h2 style='text-align: center; color: #4f46e5;'>🚀 NexusHR Suite</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Executive Dashboard", 
        "📂 Excel Data Import Center",
        "🌐 Indeed CV Bank & AI Screener",
        "👥 Core HR Directory", 
        "📅 Attendance & Leave AI Engine", 
        "📈 Performance & Analytics", 
        "💰 Payroll Management"
    ]
)
st.sidebar.markdown("---")
st.sidebar.success("🟢 AI Engine: Active\n\n📄 PDF/DOCX Parser: Online")

# ==========================================
# 1. EXECUTIVE DASHBOARD MODULE
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Command Dashboard")
    st.markdown("Real-time organizational analytics, headcount metrics, and recruitment status overview.")
    st.markdown("---")

    emp_df = st.session_state.employees
    cv_df = st.session_state.cv_bank

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Workforce", len(emp_df))
    with col2: st.metric("Total CV Bank", len(cv_df))
    with col3: st.metric("Shortlisted", len(cv_df[cv_df['AI_Status'] == 'Shortlisted']))
    with col4: st.metric("Backup CVs", len(cv_df[cv_df['AI_Status'] == 'Backup CV']))
    with col5: st.metric("Rejected", len(cv_df[cv_df['AI_Status'] == 'Rejected']))

    st.markdown("<br>", unsafe_allow_html=True)
    if not cv_df.empty:
        st.subheader("📁 Position-Wise Candidate Folders")
        folder_counts = cv_df['Position_Folder'].value_counts().reset_index()
        folder_counts.columns = ['Position Folder', 'Candidate Count']
        fig_folders = px.bar(folder_counts, x='Position Folder', y='Candidate Count', color='Position Folder', template='plotly_white')
        st.plotly_chart(fig_folders, use_container_width=True)

# ==========================================
# 2. EXCEL DATA IMPORT CENTER
# ==========================================
elif menu == "📂 Excel Data Import Center":
    st.title("📂 Excel Data Import Center")
    st.markdown("Upload your existing Excel files (`.xlsx`) to sync employee and attendance records.")
    st.markdown("---")
    col_x, col_y = st.columns(2)
    with col_x:
        emp_file = st.file_uploader("Upload Employee Sheet", type=["xlsx"], key="emp_excel")
        if emp_file is not None and st.button("Sync Employee Data"):
            st.session_state.employees = pd.read_excel(emp_file)
            st.success("Synced successfully!")
            st.rerun()
    with col_y:
        att_file = st.file_uploader("Upload Attendance Sheet", type=["xlsx"], key="att_excel")
        if att_file is not None and st.button("Sync Attendance Data"):
            st.session_state.attendance_logs = pd.read_excel(att_file)
            st.success("Synced successfully!")
            st.rerun()

# ==========================================
# 3. INDEED CV BANK & AI SCREENER WITH PREVIEW MODULE
# ==========================================
elif menu == "🌐 Indeed CV Bank & AI Screener":
    st.title("🌐 Indeed CV Bank & Position-Wise AI Screener")
    st.markdown("Upload PDF/Word CVs, preview candidate documents live, and manage screening pipelines.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📄 Document Preview & Screening Pipeline", "📥 Upload PDF / Word CV", "🌐 Sync from Indeed"])

    # TAB 1: DOCUMENT PREVIEW & SCREENING PIPELINE
    with tab1:
        st.subheader("📄 Candidate File Viewer & Live Document Preview")
        
        cv_df = st.session_state.cv_bank
        if cv_df.empty:
            st.info("No CVs found in the bank.")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                selected_pos = st.selectbox("📂 Select Position Folder", ["All Positions"] + list(cv_df['Position_Folder'].unique()))
            with col_f2:
                selected_status = st.selectbox("🎯 Select Screening Status", ["All Statuses", "Shortlisted", "Backup CV", "Rejected"])

            filtered_cvs = cv_df
            if selected_pos != "All Positions":
                filtered_cvs = filtered_cvs[filtered_cvs['Position_Folder'] == selected_pos]
            if selected_status != "All Statuses":
                filtered_cvs = filtered_cvs[filtered_cvs['AI_Status'] == selected_status]

            # Main View: Split Into Table and Live Document Preview Card
            col_left, col_right = st.columns([1.2, 1.8])

            with col_left:
                st.markdown("### 👥 Select Candidate Profile")
                st.dataframe(filtered_cvs[['Candidate_ID', 'Name', 'Position_Folder', 'AI_Status']], use_container_width=True)
                
                selected_candidate_name = st.selectbox("Choose Candidate to Preview Document", filtered_cvs['Name'].tolist())
                
                c_idx = cv_df[cv_df['Name'] == selected_candidate_name].index[0]
                c_data = cv_df.loc[c_idx]

                st.markdown("---")
                st.markdown("### ⚙️ Action: Change Candidate Status")
                new_status = st.radio("Set Status", ["Shortlisted", "Backup CV", "Rejected"], horizontal=True, key="preview_status_radio")
                if st.button("Save New Status"):
                    st.session_state.cv_bank.loc[c_idx, 'AI_Status'] = new_status
                    st.success(f"Status for {selected_candidate_name} updated to {new_status}!")
                    st.rerun()

            with col_right:
                st.markdown(f"### 📄 Live Resume Preview: **{c_data['Name']}**")
                st.markdown(f"**Document File:** `{c_data.get('File_Name', 'Uploaded_CV.pdf')}` | **Source:** `{c_data['Source']}` | **Match Score:** `{c_data['Match_Score']}%`")
                
                # Render the Document Preview Box
                resume_text = c_data.get('Resume_Content', 'No preview content available.')
                st.markdown(f'<div class="cv-preview-box">{resume_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

    # TAB 2: UPLOAD WORD / PDF FILE
    with tab2:
        st.subheader("📥 Upload PDF or Word (.docx) Candidate Resumes")
        
        with st.form("file_cv_form"):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                cand_name = st.text_input("Candidate Full Name")
                cand_position = st.selectbox("Assign Position Folder", ["Python Developer", "HR Executive", "Financial Analyst", "UI/UX Designer", "DevOps Engineer"])
            with col_u2:
                uploaded_cv_file = st.file_uploader("Upload Candidate CV File", type=["pdf", "docx", "txt"])
                target_jd = st.text_input("Target Position Keywords", "Python Streamlit SQL Developer")

            submit_cv = st.form_submit_button("Extract Text, Preview & Run AI Screener")

            if submit_cv and cand_name and uploaded_cv_file:
                # Extract text using helper
                extracted_content = extract_text_from_file(uploaded_cv_file)
                
                # Calculate AI score
                jd_words = set(target_jd.lower().split())
                res_words = set(extracted_content.lower().split())
                common_words = jd_words.intersection(res_words)
                score = min(int((len(common_words) / max(len(jd_words), 1)) * 130 + 50), 98) if extracted_content else 60

                if score >= 75:
                    ai_status = "Shortlisted"
                elif score >= 55:
                    ai_status = "Backup CV"
                else:
                    ai_status = "Rejected"

                new_cv = pd.DataFrame({
                    'Candidate_ID': [f"CV00{len(st.session_state.cv_bank)+1}"],
                    'Name': [cand_name],
                    'Position_Folder': [cand_position],
                    'Source': ['Document Upload'],
                    'File_Name': [uploaded_cv_file.name],
                    'Resume_Content': [extracted_content if extracted_content else "Text extraction empty."],
                    'Match_Score': [score],
                    'AI_Status': [ai_status]
                })

                st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, new_cv], ignore_index=True)
                st.success(f"File **{uploaded_cv_file.name}** parsed successfully and categorized into **{cand_position}**! Status: **{ai_status}**")
                st.rerun()

    # TAB 3: INDEED API SYNC
    with tab3:
        st.subheader("🌐 Sync Resumes from Indeed Job Board")
        indeed_role = st.selectbox("Select Active Indeed Job Posting", ["Python Developer", "HR Executive", "Financial Analyst", "UI/UX Designer"])
        
        if st.button("🚀 Sync Applicants from Indeed"):
            simulated_indeed = pd.DataFrame({
                'Candidate_ID': [f"IND0{len(st.session_state.cv_bank)+1}", f"IND0{len(st.session_state.cv_bank)+2}"],
                'Name': ['Liam Hemsworth', 'Scarlett Johansson'],
                'Position_Folder': [indeed_role, indeed_role],
                'Source': ['Indeed API', 'Indeed API'],
                'File_Name': [f'{indeed_role}_Applicant_1.pdf', f'{indeed_role}_Applicant_2.pdf'],
                'Resume_Content': [
                    f"SUMMARY:\nSpecialized {indeed_role} with 5 years experience in building scalable apps.",
                    f"SUMMARY:\nExperienced professional applying for {indeed_role} role with strong technical leadership skills."
                ],
                'Match_Score': [88, 54],
                'AI_Status': ['Shortlisted', 'Backup CV']
            })
            st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, simulated_indeed], ignore_index=True)
            st.success(f"Fetched candidates from Indeed for **{indeed_role}**!")
            st.rerun()

# ==========================================
# 4. CORE HR DIRECTORY MODULE
# ==========================================
elif menu == "👥 Core HR Directory":
    st.title("👥 Core HR Directory")
    st.markdown("---")
    st.dataframe(st.session_state.employees, use_container_width=True)

# ==========================================
# 5. ATTENDANCE & LEAVE AI ENGINE MODULE
# ==========================================
elif menu == "📅 Attendance & Leave AI Engine":
    st.title("📅 Attendance & Leave AI Engine")
    st.markdown("---")

# ==========================================
# 6. PERFORMANCE & ANALYTICS MODULE
# ==========================================
elif menu == "📈 Performance & Analytics":
    st.title("📈 Performance Analytics")
    st.markdown("---")

# ==========================================
# 7. PAYROLL MANAGEMENT MODULE
# ==========================================
elif menu == "💰 Payroll Management":
    st.title("💰 Payroll & Compensation Management")
    st.markdown("---")
    emp_df = st.session_state.employees.copy()
    if not emp_df.empty:
        emp_df['Monthly Salary'] = emp_df['Salary'] / 12
        st.dataframe(emp_df, use_container_width=True)
    else:
        st.warning("No employee data available.")
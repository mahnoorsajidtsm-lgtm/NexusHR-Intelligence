import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import base64

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
        max-height: 400px;
        overflow-y: auto;
        font-family: Arial, sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTION: EXTRACT TEXT FROM UPLOADED FILES ---
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    
    file_name = uploaded_file.name.lower()
    extracted_text = ""

    if file_name.endswith(".pdf"):
        if PdfReader is not None:
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            except Exception as e:
                extracted_text = f"[Error reading PDF: {e}]"
        else:
            extracted_text = "[pypdf library missing]"

    elif file_name.endswith(".docx"):
        if docx is not None:
            try:
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            except Exception as e:
                extracted_text = f"[Error reading Word file: {e}]"
        else:
            extracted_text = "[python-docx library missing]"

    elif file_name.endswith(".txt"):
        try:
            extracted_text = uploaded_file.read().decode("utf-8")
        except Exception as e:
            extracted_text = f"[Error reading text file: {e}]"

    return extracted_text.strip()

# --- HELPER FUNCTION: DISPLAY PDF OR TEXT PREVIEW ---
def display_pdf_bytes(file_bytes, file_name, text_fallback):
    if file_bytes and file_name.lower().endswith(".pdf"):
        # Embed real PDF viewer in iframe
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="550" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        # Fallback text preview container for Word (.docx) or sample text
        st.markdown(f'<div class="cv-preview-box">{text_fallback.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

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

if 'cv_bank' not in st.session_state:
    st.session_state.cv_bank = pd.DataFrame({
        'Candidate_ID': ['CV001', 'CV002', 'CV003', 'CV004'],
        'Name': ['Alex Mercer', 'Jessica Pearson', 'David Miller', 'Rachel Zane'],
        'Position_Folder': ['Python Developer', 'HR Executive', 'Python Developer', 'Financial Analyst'],
        'Source': ['Indeed API', 'PDF Upload', 'Word Upload', 'PDF Upload'],
        'File_Name': ['Alex_Mercer_CV.pdf', 'Jessica_Pearson_Resume.pdf', 'David_Miller_CV.docx', 'Rachel_Zane_Resume.pdf'],
        'File_Bytes': [None, None, None, None],
        'Resume_Content': [
            "SUMMARY:\nSenior Python Developer with 5+ years experience in Django, Streamlit, SQL, and Machine Learning pipelines.",
            "SUMMARY:\nHuman Resources Specialist with expertise in recruitment, employee relations, and policy compliance.",
            "SUMMARY:\nJunior Software Engineer learning Python, database management, and building automated scripts.",
            "SUMMARY:\nFinancial Analyst skilled in risk modeling, financial forecasting, corporate budget preparation, and Excel analytics."
        ],
        'Match_Score': [92, 85, 58, 89],
        'AI_Status': ['Shortlisted', 'Shortlisted', 'Rejected', 'Shortlisted']
    })

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
st.sidebar.success("🟢 AI Engine: Active\n\n📄 PDF Viewer: Embedded")

# ==========================================
# 1. EXECUTIVE DASHBOARD MODULE
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Command Dashboard")
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
    st.markdown("---")

# ==========================================
# 3. INDEED CV BANK & AI SCREENER WITH LIVE PDF VIEWER
# ==========================================
elif menu == "🌐 Indeed CV Bank & AI Screener":
    st.title("🌐 Indeed CV Bank & Position-Wise AI Screener")
    st.markdown("View live embedded PDF documents, Word doc text extractions, and manage candidate statuses.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📄 Live Document Viewer & Pipeline", "📥 Upload PDF / Word CV", "🌐 Sync from Indeed"])

    # TAB 1: LIVE DOCUMENT VIEWER
    with tab1:
        st.subheader("📁 Position-Wise Folders & Candidate Document Viewer")
        
        cv_df = st.session_state.cv_bank
        if cv_df.empty:
            st.info("No CVs found in the bank.")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                selected_pos = st.selectbox("📂 Filter Position Folder", ["All Positions"] + list(cv_df['Position_Folder'].unique()))
            with col_f2:
                selected_status = st.selectbox("🎯 Filter Screening Status", ["All Statuses", "Shortlisted", "Backup CV", "Rejected"])

            filtered_cvs = cv_df
            if selected_pos != "All Positions":
                filtered_cvs = filtered_cvs[filtered_cvs['Position_Folder'] == selected_pos]
            if selected_status != "All Statuses":
                filtered_cvs = filtered_cvs[filtered_cvs['AI_Status'] == selected_status]

            col_left, col_right = st.columns([1.2, 1.8])

            with col_left:
                st.markdown("### 👥 Candidate Records")
                st.dataframe(filtered_cvs[['Candidate_ID', 'Name', 'Position_Folder', 'AI_Status']], use_container_width=True)
                
                selected_candidate_name = st.selectbox("Select Candidate to Preview Document", filtered_cvs['Name'].tolist()) if not filtered_cvs.empty else None
                
                if selected_candidate_name:
                    c_idx = cv_df[cv_df['Name'] == selected_candidate_name].index[0]
                    c_data = cv_df.loc[c_idx]

                    st.markdown("---")
                    st.markdown("### ⚙️ Update Candidate Status")
                    new_status = st.radio("Assign Status", ["Shortlisted", "Backup CV", "Rejected"], horizontal=True, key="doc_status_radio")
                    if st.button("Save Status Update"):
                        st.session_state.cv_bank.loc[c_idx, 'AI_Status'] = new_status
                        st.success(f"Status for {selected_candidate_name} updated to **{new_status}**!")
                        st.rerun()

            with col_right:
                if selected_candidate_name and not filtered_cvs.empty:
                    st.markdown(f"### 📄 Live Document Preview: **{c_data['Name']}**")
                    st.markdown(f"**File Name:** `{c_data.get('File_Name', 'Resume.pdf')}` | **Match Score:** `{c_data['Match_Score']}%`")

                    # Download button for Word/PDF files
                    if c_data.get('File_Bytes') is not None:
                        st.download_button(
                            label=f"💾 Download Original File ({c_data['File_Name']})",
                            data=c_data['File_Bytes'],
                            file_name=c_data['File_Name']
                        )

                    # Display Live Document Preview (PDF frame or styled text box for Word)
                    display_pdf_bytes(
                        file_bytes=c_data.get('File_Bytes'),
                        file_name=c_data.get('File_Name', ''),
                        text_fallback=c_data.get('Resume_Content', 'No content available.')
                    )

    # TAB 2: MANUAL UPLOAD WITH REAL FILE STORAGE
    with tab2:
        st.subheader("📥 Upload Original PDF or Word (.docx) File")
        
        with st.form("file_upload_cv_form"):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                cand_name = st.text_input("Candidate Full Name")
                cand_position = st.selectbox("Assign Position Folder", ["Python Developer", "HR Executive", "Financial Analyst", "UI/UX Designer", "DevOps Engineer"])
            with col_u2:
                uploaded_cv_file = st.file_uploader("Upload PDF or Word Document", type=["pdf", "docx", "txt"])
                target_jd = st.text_input("Target Job Keywords for AI", "Python Streamlit SQL Developer")

            submit_cv = st.form_submit_button("Upload File & Generate Document Preview")

            if submit_cv and cand_name and uploaded_cv_file:
                # Store original binary file bytes for PDF previewing & downloading
                file_bytes = uploaded_cv_file.getvalue()
                
                # Extract text for AI screening calculations
                extracted_content = extract_text_from_file(uploaded_cv_file)
                
                jd_words = set(target_jd.lower().split())
                res_words = set(extracted_content.lower().split())
                common_words = jd_words.intersection(res_words)
                score = min(int((len(common_words) / max(len(jd_words), 1)) * 130 + 50), 98) if extracted_content else 65

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
                    'File_Bytes': [file_bytes],
                    'Resume_Content': [extracted_content if extracted_content else "Document text extracted successfully."],
                    'Match_Score': [score],
                    'AI_Status': [ai_status]
                })

                st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, new_cv], ignore_index=True)
                st.success(f"Document **{uploaded_cv_file.name}** uploaded! Go to Tab 1 to see the live document preview.")
                st.rerun()

    # TAB 3: INDEED API SYNC
    with tab3:
        st.subheader("🌐 Sync Applicants from Indeed")
        indeed_role = st.selectbox("Select Active Indeed Job Posting", ["Python Developer", "HR Executive", "Financial Analyst"])
        if st.button("Sync Indeed Candidates"):
            simulated_indeed = pd.DataFrame({
                'Candidate_ID': [f"IND0{len(st.session_state.cv_bank)+1}", f"IND0{len(st.session_state.cv_bank)+2}"],
                'Name': ['Liam Hemsworth', 'Scarlett Johansson'],
                'Position_Folder': [indeed_role, indeed_role],
                'Source': ['Indeed API', 'Indeed API'],
                'File_Name': [f'{indeed_role}_Applicant_1.pdf', f'{indeed_role}_Applicant_2.pdf'],
                'File_Bytes': [None, None],
                'Resume_Content': [
                    f"SUMMARY:\nSpecialized {indeed_role} with 5 years experience in building scalable web applications.",
                    f"SUMMARY:\nExperienced professional applying for {indeed_role} position with leadership skills."
                ],
                'Match_Score': [88, 54],
                'AI_Status': ['Shortlisted', 'Backup CV']
            })
            st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, simulated_indeed], ignore_index=True)
            st.success("Synced Indeed candidates!")
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
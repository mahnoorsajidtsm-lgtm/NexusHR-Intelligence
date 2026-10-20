import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import base64

# Optional file parser imports
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
    .main { background-color: #f8fafc; }
    .metric-card {
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
        font-family: Arial, sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    file_name = uploaded_file.name.lower()
    extracted_text = ""
    if file_name.endswith(".pdf") and PdfReader:
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text: extracted_text += text + "\n"
        except Exception as e:
            extracted_text = f"[Error reading PDF: {e}]"
    elif file_name.endswith(".docx") and docx:
        try:
            doc = docx.Document(uploaded_file)
            extracted_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            extracted_text = f"[Error reading Word file: {e}]"
    elif file_name.endswith(".txt"):
        try:
            extracted_text = uploaded_file.read().decode("utf-8")
        except Exception as e:
            extracted_text = f"[Error reading text file: {e}]"
    return extracted_text.strip()

def display_pdf_bytes(file_bytes, file_name, text_fallback):
    if file_bytes and file_name.lower().endswith(".pdf"):
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="550" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="cv-preview-box">{text_fallback.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

def calculate_leave_quota(is_confirmed, full_leaves, half_days, short_leaves, late_comings):
    total_allowed = 18 if is_confirmed else 2
    deduction_half = half_days * 0.5
    deduction_short = short_leaves * 0.25
    deduction_lates = (late_comings // 3) * 1.0
    total_deductions = full_leaves + deduction_half + deduction_short + deduction_lates
    remaining_balance = total_allowed - total_deductions
    return {
        'Allowed': total_allowed,
        'Half_Deduction': deduction_half,
        'Short_Deduction': deduction_short,
        'Late_Deduction': deduction_lates,
        'Total_Deducted': total_deductions,
        'Remaining_Balance': remaining_balance
    }

# --- INITIALIZE SESSION STATE ---
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame({
        'Emp_ID': ['EMP001', 'EMP002'],
        'Name': ['Sarah Jenkins', 'Ahmed Khan'],
        'Department': ['Engineering', 'Human Resources'],
        'Role': ['Backend Lead', 'HR Executive'],
        'Status': ['Active', 'Active'],
        'Salary': [95000, 75000],
        'Joining_Date': [date(2025, 1, 10), date(2026, 2, 1)],
        'Is_Confirmed': [True, False]
    })

if 'attendance_logs' not in st.session_state:
    st.session_state.attendance_logs = pd.DataFrame({
        'Emp_ID': ['EMP001', 'EMP002'],
        'Name': ['Sarah Jenkins', 'Ahmed Khan'],
        'Full_Leaves_Taken': [1, 0],
        'Half_Days': [2, 0],
        'Short_Leaves': [2, 1],
        'Late_Comings': [3, 1]
    })

if 'cv_bank' not in st.session_state:
    st.session_state.cv_bank = pd.DataFrame({
        'Candidate_ID': ['CV001', 'CV002', 'CV003', 'CV004'],
        'Name': ['Alex Mercer', 'Jessica Pearson', 'David Miller', 'Rachel Zane'],
        'Position_Folder': ['Python Developer', 'HR Executive', 'Python Developer', 'Financial Analyst'],
        'Source': ['Indeed API', 'PDF Upload', 'Word Upload', 'Indeed API'],
        'File_Name': ['Alex_Mercer_CV.pdf', 'Jessica_Pearson_Resume.pdf', 'David_Miller_CV.docx', 'Rachel_Zane_Resume.pdf'],
        'File_Bytes': [None, None, None, None],
        'Resume_Content': [
            "SUMMARY:\nSenior Python Developer with 5+ years experience in Django, Streamlit, SQL, and Machine Learning pipelines.",
            "SUMMARY:\nHuman Resources Specialist with expertise in recruitment, employee relations, and policy compliance.",
            "SUMMARY:\nJunior Software Engineer learning Python, database management, and automated scripting.",
            "SUMMARY:\nFinancial Analyst skilled in risk modeling, financial forecasting, and corporate budget management."
        ],
        'Match_Score': [92, 85, 58, 89],
        'AI_Status': ['Shortlisted', 'Shortlisted', 'Rejected', 'Backup CV']
    })

if 'training_records' not in st.session_state:
    st.session_state.training_records = pd.DataFrame({
        'Course_Name': ['Advanced Python Security', 'HR Compliance & Ethics', 'Leadership & OKRs'],
        'Category': ['Engineering', 'Human Resources', 'Management'],
        'Status': ['In Progress', 'Completed', 'Scheduled'],
        'Enrolled_Count': [12, 8, 15]
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
        "📈 Performance & Training", 
        "💰 Payroll Management"
    ]
)
st.sidebar.markdown("---")
st.sidebar.success("🟢 System Status: Online\n\n🔒 Enterprise Security: Active")

# ==========================================
# 1. EXECUTIVE DASHBOARD
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Command Dashboard")
    st.markdown("Comprehensive workforce intelligence, recruitment status, and payroll overview.")
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
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🏢 Department Workforce Distribution")
        if not emp_df.empty:
            dept_counts = emp_df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            fig_dept = px.pie(dept_counts, names='Department', values='Count', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_dept, use_container_width=True)
    with col_b:
        st.subheader("📁 Position-Wise CV Folders")
        if not cv_df.empty:
            folder_counts = cv_df['Position_Folder'].value_counts().reset_index()
            folder_counts.columns = ['Position Folder', 'Count']
            fig_folders = px.bar(folder_counts, x='Position Folder', y='Count', color='Position Folder', template='plotly_white')
            st.plotly_chart(fig_folders, use_container_width=True)

# ==========================================
# 2. EXCEL DATA IMPORT CENTER
# ==========================================
elif menu == "📂 Excel Data Import Center":
    st.title("📂 Excel Data Import Center")
    st.markdown("Upload your spreadsheets (`.xlsx`) to instantly sync employee records and attendance logs.")
    st.markdown("---")

    col_x, col_y = st.columns(2)
    with col_x:
        st.subheader("1. Employee Directory Sheet")
        emp_file = st.file_uploader("Upload Employee Excel", type=["xlsx"], key="emp_imp")
        if emp_file is not None:
            try:
                up_emp = pd.read_excel(emp_file)
                st.dataframe(up_emp.head(), use_container_width=True)
                if st.button("Sync Employee Data"):
                    st.session_state.employees = up_emp
                    st.success("Synced successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col_y:
        st.subheader("2. Attendance & Leaves Sheet")
        att_file = st.file_uploader("Upload Attendance Excel", type=["xlsx"], key="att_imp")
        if att_file is not None:
            try:
                up_att = pd.read_excel(att_file)
                st.dataframe(up_att.head(), use_container_width=True)
                if st.button("Sync Attendance Data"):
                    st.session_state.attendance_logs = up_att
                    st.success("Synced successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# 3. INDEED CV BANK & AI SCREENER
# ==========================================
elif menu == "🌐 Indeed CV Bank & AI Screener":
    st.title("🌐 Indeed CV Bank & Position-Wise AI Screener")
    st.markdown("Manage automated Indeed job board syncs, position folders, live document previews, and candidate statuses.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📄 Live Document Viewer & Pipeline", "📥 Upload PDF / Word CV", "🌐 Sync from Indeed"])

    with tab1:
        cv_df = st.session_state.cv_bank
        if cv_df.empty:
            st.info("No candidates found in CV bank.")
        else:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                sel_pos = st.selectbox("📂 Filter Position Folder", ["All Positions"] + list(cv_df['Position_Folder'].unique()))
            with col_f2:
                sel_status = st.selectbox("🎯 Filter Status", ["All Statuses", "Shortlisted", "Backup CV", "Rejected"])

            filtered = cv_df
            if sel_pos != "All Positions": filtered = filtered[filtered['Position_Folder'] == sel_pos]
            if sel_status != "All Statuses": filtered = filtered[filtered['AI_Status'] == sel_status]

            c_left, c_right = st.columns([1.2, 1.8])
            with c_left:
                st.markdown("### Candidate Records")
                st.dataframe(filtered[['Candidate_ID', 'Name', 'Position_Folder', 'AI_Status']], use_container_width=True)
                sel_cand = st.selectbox("Select Candidate for Review", filtered['Name'].tolist()) if not filtered.empty else None
                
                if sel_cand:
                    c_idx = cv_df[cv_df['Name'] == sel_cand].index[0]
                    c_data = cv_df.loc[c_idx]
                    st.markdown("---")
                    new_st = st.radio("Update Screening Status", ["Shortlisted", "Backup CV", "Rejected"], horizontal=True, key="stat_radio")
                    if st.button("Save Status"):
                        st.session_state.cv_bank.loc[c_idx, 'AI_Status'] = new_st
                        st.success(f"Updated status for {sel_cand} to {new_st}!")
                        st.rerun()

            with c_right:
                if sel_cand and not filtered.empty:
                    st.markdown(f"### 📄 Live Preview: **{c_data['Name']}**")
                    st.markdown(f"**File:** `{c_data.get('File_Name', 'Resume.pdf')}` | **Match Score:** `{c_data['Match_Score']}%`")
                    if c_data.get('File_Bytes') is not None:
                        st.download_button("💾 Download Original File", data=c_data['File_Bytes'], file_name=c_data['File_Name'])
                    display_pdf_bytes(c_data.get('File_Bytes'), c_data.get('File_Name', ''), c_data.get('Resume_Content', ''))

    with tab2:
        st.subheader("📥 Upload Original PDF or Word (.docx) CV")
        with st.form("up_form"):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                c_name = st.text_input("Candidate Full Name")
                c_pos = st.selectbox("Position Folder", ["Python Developer", "HR Executive", "Financial Analyst", "UI/UX Designer"])
            with col_u2:
                c_file = st.file_uploader("Upload CV Document", type=["pdf", "docx", "txt"])
                target_k = st.text_input("Target Keywords", "Python Streamlit SQL Developer")
            
            if st.form_submit_button("Upload & Run AI Screener") and c_name and c_file:
                f_bytes = c_file.getvalue()
                extracted = extract_text_from_file(c_file)
                jd_w = set(target_k.lower().split())
                res_w = set(extracted.lower().split())
                score = min(int((len(jd_w.intersection(res_w)) / max(len(jd_w), 1)) * 130 + 50), 98) if extracted else 65
                
                status = "Shortlisted" if score >= 75 else ("Backup CV" if score >= 55 else "Rejected")
                new_row = pd.DataFrame({
                    'Candidate_ID': [f"CV00{len(st.session_state.cv_bank)+1}"],
                    'Name': [c_name],
                    'Position_Folder': [c_pos],
                    'Source': ['Document Upload'],
                    'File_Name': [c_file.name],
                    'File_Bytes': [f_bytes],
                    'Resume_Content': [extracted or "Parsed successfully."],
                    'Match_Score': [score],
                    'AI_Status': [status]
                })
                st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, new_row], ignore_index=True)
                st.success(f"Uploaded successfully! AI Status assigned: **{status}**")
                st.rerun()

    with tab3:
        st.subheader("🌐 Indeed API Sync Simulator")
        ind_role = st.selectbox("Indeed Job Posting", ["Python Developer", "HR Executive", "Financial Analyst"])
        if st.button("🚀 Fetch Applicants from Indeed"):
            sim_ind = pd.DataFrame({
                'Candidate_ID': [f"IND0{len(st.session_state.cv_bank)+1}"],
                'Name': ['Liam Hemsworth'],
                'Position_Folder': [ind_role],
                'Source': ['Indeed API'],
                'File_Name': [f'{ind_role}_Applicant.pdf'],
                'File_Bytes': [None],
                'Resume_Content': [f"Specialized {ind_role} with 5 years experience."],
                'Match_Score': [88],
                'AI_Status': ['Shortlisted']
            })
            st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, sim_ind], ignore_index=True)
            st.success(f"Successfully synced Indeed applicants for {ind_role}!")
            st.rerun()

# ==========================================
# 4. CORE HR DIRECTORY
# ==========================================
elif menu == "👥 Core HR Directory":
    st.title("👥 Core HR Directory & Employee Records")
    st.markdown("Centralized employee management, organizational hierarchy, and probation status.")
    st.markdown("---")

    st.dataframe(st.session_state.employees, use_container_width=True)

    st.markdown("### ➕ Onboard New Employee")
    with st.form("onboard_form"):
        c1, c2 = st.columns(2)
        with c1:
            eid = f"EMP0{len(st.session_state.employees)+1:02d}"
            name = st.text_input("Full Name")
            dept = st.selectbox("Department", ["Engineering", "Human Resources", "Finance", "Marketing"])
            role = st.text_input("Job Role")
        with c2:
            sal = st.number_input("Annual Salary ($)", min_value=30000, value=65000)
            jdate = st.date_input("Joining Date", value=date.today())
            conf = st.checkbox("Confirmed Employee (18 Paid Leaves)", value=False)
        
        if st.form_submit_button("Onboard Staff") and name:
            new_emp = pd.DataFrame({
                'Emp_ID': [eid], 'Name': [name], 'Department': [dept], 'Role': [role],
                'Status': ['Active'], 'Salary': [sal], 'Joining_Date': [jdate], 'Is_Confirmed': [conf]
            })
            new_att = pd.DataFrame({
                'Emp_ID': [eid], 'Name': [name], 'Full_Leaves_Taken': [0],
                'Half_Days': [0], 'Short_Leaves': [0], 'Late_Comings': [0]
            })
            st.session_state.employees = pd.concat([st.session_state.employees, new_emp], ignore_index=True)
            st.session_state.attendance_logs = pd.concat([st.session_state.attendance_logs, new_att], ignore_index=True)
            st.success(f"Successfully onboarded {name}!")
            st.rerun()

# ==========================================
# 5. ATTENDANCE & LEAVE AI ENGINE
# ==========================================
elif menu == "📅 Attendance & Leave AI Engine":
    st.title("📅 Attendance & Leave Policy Management")
    st.markdown("Automated attendance tracking, half-day, short-leave, and late-coming rule enforcement.")
    st.markdown("---")

    st.info("""
    📋 **Policy Guidelines**:
    * **Quota:** 18 Paid Leaves (Confirmed) | 2 Paid Leaves (Probation)
    * **Deduction Rules:** 2 Half Days = 1 Full Day | 4 Short Leaves = 1 Full Day | 3 Late Comings = 1 Day Off
    """)

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if not emp_df.empty:
        sel_emp = st.selectbox("Select Employee", emp_df['Name'].tolist())
        emp_info = emp_df[emp_df['Name'] == sel_emp].iloc[0]
        att_idx = att_df[att_df['Name'] == sel_emp].index[0]
        att_info = att_df.loc[att_idx]

        with st.form("att_form"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: f_leaves = st.number_input("Full Leaves", value=int(att_info['Full_Leaves_Taken']))
            with c2: h_days = st.number_input("Half Days", value=int(att_info['Half_Days']))
            with c3: s_leaves = st.number_input("Short Leaves", value=int(att_info['Short_Leaves']))
            with c4: l_comings = st.number_input("Late Comings", value=int(att_info['Late_Comings']))

            if st.form_submit_button("Update Records"):
                st.session_state.attendance_logs.loc[att_idx, 'Full_Leaves_Taken'] = f_leaves
                st.session_state.attendance_logs.loc[att_idx, 'Half_Days'] = h_days
                st.session_state.attendance_logs.loc[att_idx, 'Short_Leaves'] = s_leaves
                st.session_state.attendance_logs.loc[att_idx, 'Late_Comings'] = l_comings
                st.success("Attendance logs updated!")
                st.rerun()

        res = calculate_leave_quota(emp_info['Is_Confirmed'], f_leaves, h_days, s_leaves, l_comings)
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Quota", f"{res['Allowed']} Days")
        with c2: st.metric("Late Deductions", f"{res['Late_Deduction']} Days")
        with c3: st.metric("Total Deducted", f"{res['Total_Deducted']} Days")
        with c4: st.metric("Remaining Balance", f"{res['Remaining_Balance']} Days")

# ==========================================
# 6. PERFORMANCE & TRAINING
# ==========================================
elif menu == "📈 Performance & Training":
    st.title("📈 Performance Appraisals & Employee Training")
    st.markdown("Set OKRs, track KPIs, and manage skill development courses.")
    st.markdown("---")

    tab_p1, tab_p2 = st.tabs(["🎯 Performance & OKRs", "📚 Training & Development"])

    with tab_p1:
        st.subheader("Employee Performance Tracking")
        emp_df = st.session_state.employees
        if not emp_df.empty:
            p_emp = st.selectbox("Select Employee for Review", emp_df['Name'].tolist())
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Quarterly KPI Score", "4.4 / 5.0")
            with c2: st.metric("Projects Completed", "12")
            with c3: st.metric("Core Values Rating", "Exceptional")
            st.text_area("Manager Review Notes", f"Performance review for {p_emp}: Consistently exceeds expectations and meets deliverables.")
            if st.button("Save Review"): st.success("Review saved successfully!")

    with tab_p2:
        st.subheader("Training Courses & Skill Development")
        st.dataframe(st.session_state.training_records, use_container_width=True)
        with st.form("train_form"):
            t_name = st.text_input("Course Title")
            t_cat = st.selectbox("Category", ["Engineering", "Human Resources", "Finance", "Leadership"])
            if st.form_submit_button("Add Training Course") and t_name:
                new_t = pd.DataFrame({'Course_Name': [t_name], 'Category': [t_cat], 'Status': ['Active'], 'Enrolled_Count': [0]})
                st.session_state.training_records = pd.concat([st.session_state.training_records, new_t], ignore_index=True)
                st.success(f"Course '{t_name}' created!")
                st.rerun()

# ==========================================
# 7. PAYROLL MANAGEMENT
# ==========================================
elif menu == "💰 Payroll Management":
    st.title("💰 Payroll & Compensation Management")
    st.markdown("Automated salary calculations, tax deductions, and disbursements.")
    st.markdown("---")

    emp_df = st.session_state.employees.copy()
    if not emp_df.empty:
        emp_df['Monthly Salary'] = emp_df['Salary'] / 12
        emp_df['Tax (15%)'] = emp_df['Monthly Salary'] * 0.15
        emp_df['Net Pay'] = emp_df['Monthly Salary'] - emp_df['Tax (15%)']
        st.dataframe(emp_df[['Emp_ID', 'Name', 'Department', 'Monthly Salary', 'Tax (15%)', 'Net Pay']], use_container_width=True)

        if st.button("🚀 Process Monthly Payroll Disbursal"):
            st.balloons()
            st.success("Payroll successfully processed and disbursed for all active staff!")
    else:
        st.warning("No employee records found.")
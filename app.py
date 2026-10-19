import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

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
    </style>
""", unsafe_allow_html=True)

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

# Pre-populate CV Bank so it never shows up blank
if 'cv_bank' not in st.session_state:
    st.session_state.cv_bank = pd.DataFrame({
        'Candidate_ID': ['CV001', 'CV002', 'CV003', 'CV004', 'CV005'],
        'Name': ['Alex Mercer', 'Jessica Pearson', 'David Miller', 'Rachel Zane', 'Marcus Vance'],
        'Position_Folder': ['Python Developer', 'HR Executive', 'Python Developer', 'Financial Analyst', 'Python Developer'],
        'Source': ['Indeed API', 'Manual Upload', 'Indeed API', 'Manual Upload', 'Indeed API'],
        'Resume_Summary': [
            'Experienced Python Developer skilled in Streamlit, SQL, and Machine Learning.',
            'HR professional with 4 years experience in recruitment, employee relations, and payroll.',
            'Junior developer learning Python and basic web apps.',
            'Financial Analyst skilled in Excel, risk assessment, and corporate finance.',
            'Backend engineer proficient in Python APIs and database architecture.'
        ],
        'Match_Score': [92, 85, 58, 89, 74],
        'AI_Status': ['Shortlisted', 'Shortlisted', 'Rejected', 'Shortlisted', 'Backup CV']
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
st.sidebar.success("🟢 AI Engine: Active\n\n📁 Position Folders: Synced")

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
    with col1:
        st.metric("Total Workforce", len(emp_df))
    with col2:
        st.metric("Total CV Bank", len(cv_df))
    with col3:
        shortlisted_cnt = len(cv_df[cv_df['AI_Status'] == 'Shortlisted'])
        st.metric("Shortlisted", shortlisted_cnt)
    with col4:
        backup_cnt = len(cv_df[cv_df['AI_Status'] == 'Backup CV'])
        st.metric("Backup CVs", backup_cnt)
    with col5:
        rejected_cnt = len(cv_df[cv_df['AI_Status'] == 'Rejected'])
        st.metric("Rejected", rejected_cnt)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if not cv_df.empty:
        st.subheader("📁 Position-Wise Candidate Distribution Across Folders")
        folder_counts = cv_df['Position_Folder'].value_counts().reset_index()
        folder_counts.columns = ['Position Folder', 'Candidate Count']
        fig_folders = px.bar(folder_counts, x='Position Folder', y='Candidate Count', color='Position Folder', template='plotly_white')
        st.plotly_chart(fig_folders, use_container_width=True)

# ==========================================
# 2. EXCEL DATA IMPORT CENTER
# ==========================================
elif menu == "📂 Excel Data Import Center":
    st.title("📂 Excel Data Import & Fetcher Center")
    st.markdown("Upload your existing Excel files (`.xlsx`) to sync records.")
    st.markdown("---")

    col_x, col_y = st.columns(2)
    with col_x:
        st.subheader("Import Employee Directory")
        emp_file = st.file_uploader("Upload Employee Sheet", type=["xlsx"], key="emp_excel")
        if emp_file is not None:
            uploaded_emp_df = pd.read_excel(emp_file)
            if st.button("Sync Employee Data"):
                st.session_state.employees = uploaded_emp_df
                st.success("Synced successfully!")
                st.rerun()

    with col_y:
        st.subheader("Import Attendance Sheet")
        att_file = st.file_uploader("Upload Attendance Sheet", type=["xlsx"], key="att_excel")
        if att_file is not None:
            uploaded_att_df = pd.read_excel(att_file)
            if st.button("Sync Attendance Data"):
                st.session_state.attendance_logs = uploaded_att_df
                st.success("Synced successfully!")
                st.rerun()

# ==========================================
# 3. INDEED CV BANK & AI SCREENER MODULE
# ==========================================
elif menu == "🌐 Indeed CV Bank & AI Screener":
    st.title("🌐 Indeed CV Bank & Position-Wise AI Screener")
    st.markdown("Manage incoming resumes linked with Indeed job boards, position-wise folders, and automated screening statuses.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📁 Position Folders & Screening Status", "📥 Manual CV Upload", "🌐 Sync from Indeed Job Board"])

    # TAB 1: POSITION FOLDERS & SCREENING STATUS
    with tab1:
        st.subheader("📁 Position-Wise Folders & Candidate Pipeline")
        
        cv_df = st.session_state.cv_bank
        if cv_df.empty:
            st.info("No CVs found in the bank.")
        else:
            # Filters
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                positions = ["All Positions"] + list(cv_df['Position_Folder'].unique())
                selected_pos = st.selectbox("📂 Filter by Position Folder", positions)
            with col_f2:
                statuses = ["All Statuses", "Shortlisted", "Backup CV", "Rejected"]
                selected_status = st.selectbox("🎯 Filter by Screening Status", statuses)

            filtered_cvs = cv_df
            if selected_pos != "All Positions":
                filtered_cvs = filtered_cvs[filtered_cvs['Position_Folder'] == selected_pos]
            if selected_status != "All Statuses":
                filtered_cvs = filtered_cvs[filtered_cvs['AI_Status'] == selected_status]

            st.dataframe(filtered_cvs[['Candidate_ID', 'Name', 'Position_Folder', 'Source', 'Match_Score', 'AI_Status']], use_container_width=True)

            st.markdown("### ⚙️ Update Candidate Screening Status")
            c_select = st.selectbox("Select Candidate", cv_df['Name'].tolist())
            new_screening_status = st.radio("Assign Status", ["Shortlisted", "Backup CV", "Rejected"], horizontal=True)

            if st.button("Update Screening Status"):
                idx = st.session_state.cv_bank[st.session_state.cv_bank['Name'] == c_select].index[0]
                st.session_state.cv_bank.loc[idx, 'AI_Status'] = new_screening_status
                st.success(f"Successfully updated {c_select} to **{new_screening_status}**!")
                st.rerun()

    # TAB 2: MANUAL UPLOAD
    with tab2:
        st.subheader("📥 Manually Upload Candidate CV")
        with st.form("manual_cv_form"):
            c_name = st.text_input("Candidate Full Name")
            c_position = st.selectbox("Position Folder", ["Python Developer", "HR Executive", "Financial Analyst", "UI/UX Designer", "DevOps Engineer"])
            c_resume = st.text_area("Candidate Resume Summary / Skills")
            c_jd = st.text_input("Target Job Description Keywords", "Python Streamlit SQL Developer")

            submit_cv = st.form_submit_button("Upload & Categorize with AI")
            if submit_cv and c_name and c_resume:
                jd_words = set(c_jd.lower().split())
                res_words = set(c_resume.lower().split())
                common_words = jd_words.intersection(res_words)
                score = min(int((len(common_words) / max(len(jd_words), 1)) * 130 + 50), 98)
                
                # AI Automatic categorization based on score
                if score >= 75:
                    ai_status = "Shortlisted"
                elif score >= 55:
                    ai_status = "Backup CV"
                else:
                    ai_status = "Rejected"

                new_cv_row = pd.DataFrame({
                    'Candidate_ID': [f"CV00{len(st.session_state.cv_bank)+1}"],
                    'Name': [c_name],
                    'Position_Folder': [c_position],
                    'Source': ['Manual Upload'],
                    'Resume_Summary': [c_resume],
                    'Match_Score': [score],
                    'AI_Status': [ai_status]
                })

                st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, new_cv_row], ignore_index=True)
                st.success(f"CV added to **{c_position}** folder! AI Score: {score}% | Status assigned: **{ai_status}**")
                st.rerun()

    # TAB 3: INDEED API SYNC
    with tab3:
        st.subheader("🌐 Indeed Job Board Sync & API Simulation")
        st.markdown("Automatically fetch candidate pools from active Indeed job postings and sort them position-wise.")

        indeed_role = st.selectbox("Select Indeed Job Posting", ["Python Developer", "HR Executive", "Financial Analyst", "UI/UX Designer"])
        
        if st.button("🚀 Fetch & Sync Indeed Applicant Pool"):
            with st.spinner("Fetching applicants from Indeed API..."):
                simulated_indeed_applicants = pd.DataFrame({
                    'Candidate_ID': [f"IND0{len(st.session_state.cv_bank)+1}", f"IND0{len(st.session_state.cv_bank)+2}"],
                    'Name': ['Liam Hemsworth', 'Scarlett Johansson'],
                    'Position_Folder': [indeed_role, indeed_role],
                    'Source': ['Indeed API', 'Indeed API'],
                    'Resume_Summary': [
                        f'Specialized {indeed_role} with 5 years experience in building robust scalable applications.',
                        f'Experienced professional applying for {indeed_role} position with strong background.'
                    ],
                    'Match_Score': [86, 52],
                    'AI_Status': ['Shortlisted', 'Backup CV']
                })
                st.session_state.cv_bank = pd.concat([st.session_state.cv_bank, simulated_indeed_applicants], ignore_index=True)
                st.success(f"Successfully fetched and categorized applicants from Indeed for **{indeed_role}**!")
                st.rerun()

# ==========================================
# 4. CORE HR DIRECTORY MODULE
# ==========================================
elif menu == "👥 Core HR Directory":
    st.title("👥 Core HR Directory")
    st.markdown("Manage employee records.")
    st.markdown("---")
    st.dataframe(st.session_state.employees, use_container_width=True)

# ==========================================
# 5. ATTENDANCE & LEAVE AI ENGINE MODULE
# ==========================================
elif menu == "📅 Attendance & Leave AI Engine":
    st.title("📅 Attendance & Leave AI Engine")
    st.markdown("---")
    st.info("Attendance tracking module active.")

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
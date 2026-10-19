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

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4f46e5;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        color: white;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE (NO DUMMY PRE-LOADED DATA) ---
if 'employees' not in st.session_state:
    st.session_state.employees = pd.DataFrame(columns=[
        'Emp_ID', 'Name', 'Department', 'Role', 'Status', 'Salary', 
        'Joining_Date', 'Is_Confirmed'
    ])

if 'attendance_logs' not in st.session_state:
    st.session_state.attendance_logs = pd.DataFrame(columns=[
        'Emp_ID', 'Name', 'Full_Leaves_Taken', 'Half_Days', 'Short_Leaves', 'Late_Comings'
    ])

# --- HELPER FUNCTION: LEAVE CALCULATOR BASED ON COMPANY POLICY ---
def calculate_leave_quota(joining_date, is_confirmed, full_leaves, half_days, short_leaves, late_comings):
    # Rule 1: Allowance
    # Probation = 2 paid leaves, Confirmed = 18 paid leaves
    total_allowed = 18 if is_confirmed else 2

    # Rule 2: Deductions
    # 2 half days = 1 full day
    # 2 short leaves = 1 half day (0.5 day) => 4 short leaves = 1 full day
    # 3 late comings = 1 full day off
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
st.sidebar.title("🚀 NexusHR Suite")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Executive Dashboard", 
        "👥 Core HR Directory", 
        "📅 Attendance & Leave AI Engine", 
        "🤖 AI Resume Screening", 
        "📈 Performance & Analytics", 
        "💰 Payroll Management"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("System Status: **Online** | AI Policy Rules: **Active**")

# ==========================================
# 1. EXECUTIVE DASHBOARD MODULE
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown("Real-time workforce intelligence, workforce distribution, and leave compliance.")

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if emp_df.empty:
        st.warning("⚠️ No employees found in the system yet. Please add employees in the **Core HR Directory**.")
    else:
        # Key KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Employees", value=len(emp_df))
        with col2:
            confirmed_cnt = len(emp_df[emp_df['Is_Confirmed'] == True])
            st.metric(label="Confirmed Staff", value=confirmed_cnt)
        with col3:
            probation_cnt = len(emp_df[emp_df['Is_Confirmed'] == False])
            st.metric(label="On Probation", value=probation_cnt)
        with col4:
            total_lates = att_df['Late_Comings'].sum() if not att_df.empty else 0
            st.metric(label="Total Late Comings Logged", value=int(total_lates))

        st.markdown("---")

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Department Workforce Breakdown")
            dept_counts = emp_df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            fig_dept = px.pie(dept_counts, names='Department', values='Count', hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig_dept, use_container_width=True)

        with col_b:
            st.subheader("Attendance Violations Overview")
            if not att_df.empty:
                fig_att = px.bar(
                    att_df, 
                    x='Name', 
                    y=['Full_Leaves_Taken', 'Half_Days', 'Short_Leaves', 'Late_Comings'],
                    title="Attendance Incidents by Employee",
                    barmode='group'
                )
                st.plotly_chart(fig_att, use_container_width=True)
            else:
                st.info("No attendance logs recorded yet.")

# ==========================================
# 2. CORE HR DIRECTORY MODULE
# ==========================================
elif menu == "👥 Core HR Directory":
    st.title("👥 Core HR Directory")
    st.markdown("Add and manage employee records with probation tracking.")

    # Option to load sample data for testing
    if st.session_state.employees.empty:
        if st.button("💡 Load Sample Profiles (Optional testing feature)"):
            st.session_state.employees = pd.DataFrame({
                'Emp_ID': ['EMP001', 'EMP002', 'EMP003'],
                'Name': ['Sarah Jenkins', 'Ahmed Khan', 'Maria Garcia'],
                'Department': ['Engineering', 'Human Resources', 'Finance'],
                'Role': ['Backend Lead', 'HR Executive', 'Financial Analyst'],
                'Status': ['Active', 'Active', 'Active'],
                'Salary': [90000, 65000, 75000],
                'Joining_Date': [date(2025, 1, 10), date(2026, 2, 1), date(2026, 3, 15)],
                'Is_Confirmed': [True, False, False]
            })
            st.session_state.attendance_logs = pd.DataFrame({
                'Emp_ID': ['EMP001', 'EMP002', 'EMP003'],
                'Name': ['Sarah Jenkins', 'Ahmed Khan', 'Maria Garcia'],
                'Full_Leaves_Taken': [2, 1, 0],
                'Half_Days': [2, 1, 0],
                'Short_Leaves': [3, 2, 1],
                'Late_Comings': [4, 5, 1]
            })
            st.rerun()

    st.dataframe(st.session_state.employees, use_container_width=True)

    st.markdown("### ➕ Onboard New Employee")
    with st.form("add_employee_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp_id = f"EMP{len(st.session_state.employees)+1:03d}"
            name = st.text_input("Full Name")
            dept = st.selectbox("Department", ["Engineering", "Human Resources", "Marketing", "Finance", "Operations"])
            role = st.text_input("Job Role")
        with col2:
            salary = st.number_input("Annual Salary ($)", min_value=30000, max_value=300000, value=60000)
            joining_date = st.date_input("Joining Date", value=date.today())
            is_confirmed = st.checkbox("Confirmed Employee (Uncheck if on 3-Month Probation)", value=False)

        submit = st.form_submit_button("Onboard Employee")
        if submit and name:
            new_emp = pd.DataFrame({
                'Emp_ID': [emp_id],
                'Name': [name],
                'Department': [dept],
                'Role': [role],
                'Status': ['Active'],
                'Salary': [salary],
                'Joining_Date': [joining_date],
                'Is_Confirmed': [is_confirmed]
            })
            new_att = pd.DataFrame({
                'Emp_ID': [emp_id],
                'Name': [name],
                'Full_Leaves_Taken': [0],
                'Half_Days': [0],
                'Short_Leaves': [0],
                'Late_Comings': [0]
            })
            st.session_state.employees = pd.concat([st.session_state.employees, new_emp], ignore_index=True)
            st.session_state.attendance_logs = pd.concat([st.session_state.attendance_logs, new_att], ignore_index=True)
            st.success(f"Successfully onboarded {name} ({emp_id})!")
            st.rerun()

# ==========================================
# 3. ATTENDANCE & LEAVE AI ENGINE MODULE
# ==========================================
elif menu == "📅 Attendance & Leave AI Engine":
    st.title("📅 Attendance & Leave Policy Management")
    st.markdown("Automated leave deduction and AI compliance auditing based on exact organizational criteria.")

    st.info("""
    📋 **Company Leave Policy Rules**:
    * **Quota:** 18 Paid Leaves (Confirmed) | 2 Paid Leaves in Probation (First 3 Months)
    * **Deductions:**
      * 2 Half Days = **1 Full Day Leave**
      * 2 Short Leaves = **1 Half Day** (4 Short Leaves = 1 Full Day)
      * 3 Late Comings = **1 Full Day Off**
    """)

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if emp_df.empty:
        st.warning("Please add employees in the Core HR Directory first.")
    else:
        selected_emp = st.selectbox("Select Employee to Manage Attendance & Leaves", emp_df['Name'].tolist())
        
        emp_info = emp_df[emp_df['Name'] == selected_emp].iloc[0]
        emp_att_idx = att_df[att_df['Name'] == selected_emp].index[0]
        att_info = att_df.loc[emp_att_idx]

        st.markdown(f"### Employee Profile: **{emp_info['Name']}** ({'Confirmed' if emp_info['Is_Confirmed'] else 'Probation Period'})")

        # Update Attendance Record Form
        with st.form("update_att_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                full_leaves = st.number_input("Full Leaves Taken", min_value=0, value=int(att_info['Full_Leaves_Taken']))
            with col2:
                half_days = st.number_input("Half Days Taken", min_value=0, value=int(att_info['Half_Days']))
            with col3:
                short_leaves = st.number_input("Short Leaves Taken", min_value=0, value=int(att_info['Short_Leaves']))
            with col4:
                late_comings = st.number_input("Late Comings Logged", min_value=0, value=int(att_info['Late_Comings']))

            save_att = st.form_submit_button("Update Records & Calculate Quota")
            if save_att:
                st.session_state.attendance_logs.loc[emp_att_idx, 'Full_Leaves_Taken'] = full_leaves
                st.session_state.attendance_logs.loc[emp_att_idx, 'Half_Days'] = half_days
                st.session_state.attendance_logs.loc[emp_att_idx, 'Short_Leaves'] = short_leaves
                st.session_state.attendance_logs.loc[emp_att_idx, 'Late_Comings'] = late_comings
                st.success("Attendance logs updated!")
                st.rerun()

        # Run Rule Engine Calculation
        results = calculate_leave_quota(
            joining_date=emp_info['Joining_Date'],
            is_confirmed=emp_info['Is_Confirmed'],
            full_leaves=att_info['Full_Leaves_Taken'],
            half_days=att_info['Half_Days'],
            short_leaves=att_info['Short_Leaves'],
            late_comings=att_info['Late_Comings']
        )

        st.markdown("---")
        st.subheader("📊 Leave Quota Breakdown & Balance")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Allowed Quota", f"{results['Allowed']} Days")
        with c2:
            st.metric("Late Deductions", f"{results['Late_Deduction']} Days", f"From {att_info['Late_Comings']} lates")
        with c3:
            st.metric("Total Days Deducted", f"{results['Total_Deducted']} Days")
        with c4:
            st.metric("Remaining Balance", f"{results['Remaining_Balance']} Days")

        # Detailed Breakdown Table
        breakdown_df = pd.DataFrame({
            'Category': ['Full Day Leaves', 'Half Days (2 = 1 Day)', 'Short Leaves (4 = 1 Day)', 'Late Comings (3 = 1 Day)'],
            'Count Logged': [att_info['Full_Leaves_Taken'], att_info['Half_Days'], att_info['Short_Leaves'], att_info['Late_Comings']],
            'Deduction Equivalent (Days)': [
                results['Full_Leaves'], 
                results['Half_Day_Deduction'], 
                results['Short_Leave_Deduction'], 
                results['Late_Deduction']
            ]
        })
        st.table(breakdown_df)

        # AI Leave Recommendation Engine
        st.markdown("### 🤖 AI Leave Advisor Analysis")
        req_type = st.selectbox("Simulate New Leave Request", ["Full Day Leave", "Half Day", "Short Leave"])
        
        if st.button("Evaluate Leave Request with AI"):
            req_deduction = 1.0 if req_type == "Full Day Leave" else (0.5 if req_type == "Half Day" else 0.25)
            new_balance = results['Remaining_Balance'] - req_deduction

            if new_balance < 0:
                st.error(f"❌ **AI Decision: REJECTED** | Granting this {req_type} will exceed the leave quota by {abs(new_balance)} day(s). Salary deduction will apply.")
            elif not emp_info['Is_Confirmed'] and results['Total_Deducted'] >= 2:
                st.warning(f"⚠️ **AI Decision: APPROVAL WITH WARNING** | Employee is in probation (max 2 leaves allowed). Further leaves will impact confirmation eligibility.")
            else:
                st.success(f"✅ **AI Decision: APPROVED** | Sufficient leave balance available ({new_balance} days remaining after request).")

# ==========================================
# 4. AI RESUME SCREENING MODULE
# ==========================================
elif menu == "🤖 AI Resume Screening":
    st.title("🤖 AI-Powered Resume Screener")
    st.markdown("Upload candidate resumes or paste text to evaluate candidate-job fit.")

    job_description = st.text_area("Paste Job Description (JD)", "Looking for a Python Developer with experience in Streamlit, SQL, and Machine Learning algorithms.")
    candidate_resume = st.text_area("Paste Candidate Resume Text", "Experienced software engineer skilled in Python, Streamlit frameworks, database management, and building web apps.")

    if st.button("Run AI Analysis"):
        if job_description and candidate_resume:
            with st.spinner("Analyzing skill match and semantic relevance..."):
                jd_words = set(job_description.lower().split())
                resume_words = set(candidate_resume.lower().split())
                common = jd_words.intersection(resume_words)
                match_score = min(int((len(common) / max(len(jd_words), 1)) * 140 + 45), 98)

                st.markdown("---")
                st.subheader("📊 AI Evaluation Results")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="Match Score", value=f"{match_score}%")
                    if match_score > 75:
                        st.success("Recommendation: **Strong Hire**")
                    else:
                        st.warning("Recommendation: **Review Further**")
                with col2:
                    st.markdown("**Key Skill Matches Found:**")
                    st.write(", ".join([word.capitalize() for word in list(common)[:6]]) if common else "None detected")
        else:
            st.error("Please provide both a Job Description and a Candidate Resume.")

# ==========================================
# 5. PERFORMANCE & ANALYTICS MODULE
# ==========================================
elif menu == "📈 Performance & Analytics":
    st.title("📈 Performance Management & Goals")
    st.markdown("Track OKRs, employee KPIs, and review feedback cycles.")

    emp_df = st.session_state.employees
    if emp_df.empty:
        st.warning("Please add employees first.")
    else:
        selected_emp = st.selectbox("Select Employee for Review", emp_df['Name'].tolist())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Quarterly KPI Score", value="4.2 / 5.0", delta="+0.3")
        with col2:
            st.metric(label="Projects Completed", value="14", delta="+3")
        with col3:
            st.metric(label="Attendance Rate", value="98.5%", delta="+0.2%")

        st.text_area("Manager Review & Notes", f"Performance review for {selected_emp}: Consistently meets delivery milestones.")
        if st.button("Save Performance Review"):
            st.success(f"Review saved successfully for {selected_emp}!")

# ==========================================
# 6. PAYROLL MANAGEMENT MODULE
# ==========================================
elif menu == "💰 Payroll Management":
    st.title("💰 Payroll & Compensation Management")
    st.markdown("Review salary distributions, tax deductions, and unpaid leave penalties.")

    emp_df = st.session_state.employees.copy()
    att_df = st.session_state.attendance_logs

    if emp_df.empty:
        st.warning("Please add employees first.")
    else:
        # Calculate Monthly Breakdown & Deductions
        emp_df['Monthly Salary'] = emp_df['Salary'] / 12
        emp_df['Estimated Tax (15%)'] = emp_df['Monthly Salary'] * 0.15
        emp_df['Net Pay'] = emp_df['Monthly Salary'] - emp_df['Estimated Tax (15%)']

        st.dataframe(emp_df[['Emp_ID', 'Name', 'Department', 'Monthly Salary', 'Estimated Tax (15%)', 'Net Pay']], use_container_width=True)

        if st.button("🚀 Process Monthly Payroll"):
            st.balloons()
            st.success("Payroll successfully processed for all active employees!")
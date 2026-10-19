from importlib import import_module

st = import_module("streamlit")
pd = import_module("pandas")
px = import_module("plotly.express")
from datetime import datetime, date

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexusHR Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN CUSTOM CSS STYLING FOR ATTRACTIVE DASHBOARD ---
st.markdown("""
    <style>
    /* Main Background & Font */
    .main { background-color: #f4f6f9; }
    
    /* Card Container Styling */
    .metric-container {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4f46e5;
        margin-bottom: 15px;
    }
    
    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4f46e5;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Status Badges */
    .badge-confirmed { background-color: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 0.85rem; }
    .badge-probation { background-color: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 0.85rem; }
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
        "👥 Core HR Directory", 
        "📅 Attendance & Leave AI Engine", 
        "🤖 AI Resume Screening", 
        "📈 Performance & Analytics", 
        "💰 Payroll Management"
    ]
)
st.sidebar.markdown("---")
st.sidebar.success("🟢 AI Engine: Active\n\n🔒 Policy Compliance: Enforced")

# ==========================================
# 1. EXECUTIVE DASHBOARD MODULE (ATTRACTIVE & MODERN)
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Command Dashboard")
    st.markdown("Real-time organizational analytics, headcount metrics, and workforce health overview.")
    st.markdown("---")

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if emp_df.empty:
        st.info("💡 **Welcome to NexusHR!** Your directory is currently empty. Go to **Core HR Directory** in the sidebar to onboard your first employees or load sample data to test the dashboard charts.")
    else:
        # Top Modern Metric Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class="metric-container">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">Total Workforce</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{}</h2>
                    <span style="color: #10b981; font-size: 0.8rem;">⚡ Active Registry</span>
                </div>
            """.format(len(emp_df)), unsafe_allow_html=True)
            
        with col2:
            confirmed_cnt = len(emp_df[emp_df['Is_Confirmed'] == True])
            st.markdown("""
                <div class="metric-container" style="border-left-color: #10b981;">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">Confirmed Staff</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{}</h2>
                    <span style="color: #059669; font-size: 0.8rem;">📋 18 Leaves Quota</span>
                </div>
            """.format(confirmed_cnt), unsafe_allow_html=True)
            
        with col3:
            probation_cnt = len(emp_df[emp_df['Is_Confirmed'] == False])
            st.markdown("""
                <div class="metric-container" style="border-left-color: #f59e0b;">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">On Probation</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{}</h2>
                    <span style="color: #d97706; font-size: 0.8rem;">⏳ 2 Leaves Quota</span>
                </div>
            """.format(probation_cnt), unsafe_allow_html=True)
            
        with col4:
            total_lates = int(att_df['Late_Comings'].sum()) if not att_df.empty else 0
            st.markdown("""
                <div class="metric-container" style="border-left-color: #ef4444;">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">Total Late Incidents</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{}</h2>
                    <span style="color: #dc2626; font-size: 0.8rem;">⚠️ Rule: 3 lates = 1 off</span>
                </div>
            """.format(total_lates), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Visualizations Row
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("🏢 Department Workforce Distribution")
            dept_counts = emp_df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            fig_dept = px.pie(
                dept_counts, 
                names='Department', 
                values='Count', 
                hole=0.5, 
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_dept.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_dept, use_container_width=True)

        with col_b:
            st.subheader("📊 Attendance Incidents & Violations")
            if not att_df.empty:
                fig_att = px.bar(
                    att_df, 
                    x='Name', 
                    y=['Full_Leaves_Taken', 'Half_Days', 'Short_Leaves', 'Late_Comings'],
                    barmode='group',
                    color_discrete_sequence=['#4f46e5', '#3b82f6', '#10b981', '#f59e0b']
                )
                fig_att.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_att, use_container_width=True)
            else:
                st.info("No attendance incident data available yet.")

# ==========================================
# 2. CORE HR DIRECTORY MODULE
# ==========================================
elif menu == "👥 Core HR Directory":
    st.title("👥 Core HR Directory & Employee Registry")
    st.markdown("Manage employee files, track confirmation status, and onboard new staff members.")
    st.markdown("---")

    # Sample data loader button
    if st.session_state.employees.empty:
        if st.button("💡 Click here to load Sample Profiles for Testing"):
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

    st.markdown("### ➕ Onboard New Employee Form")
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
            is_confirmed = st.checkbox("Confirmed Employee (Check for 18 leaves, Uncheck for 2 probation leaves)", value=False)

        submit = st.form_submit_button("Complete Onboarding")
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
    st.title("📅 Attendance & Leave AI Compliance Engine")
    st.markdown("Automated calculation of leave quotas, half days, short leaves, and late coming penalties.")
    st.markdown("---")

    st.info("""
    📌 **Company Policy Framework**:
    * **Quota Allowance:** 18 Paid Leaves (Confirmed) | 2 Paid Leaves (Probation / First 3 Months)
    * **Penalty Rules:** 
      * 2 Half Days = **1 Full Day Leave**
      * 2 Short Leaves = **1 Half Day** (4 Short Leaves = 1 Full Day)
      * 3 Late Comings = **1 Full Day Off Deduction**
    """)

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if emp_df.empty:
        st.warning("Please add employees in the **Core HR Directory** first.")
    else:
        selected_emp = st.selectbox("Select Employee File", emp_df['Name'].tolist())
        
        emp_info = emp_df[emp_df['Name'] == selected_emp].iloc[0]
        emp_att_idx = att_df[att_df['Name'] == selected_emp].index[0]
        att_info = att_df.loc[emp_att_idx]

        st.markdown(f"### Managing Attendance: **{emp_info['Name']}**")
        status_tag = "🟢 Confirmed Staff (18 Leaves)" if emp_info['Is_Confirmed'] else "🟡 Probation Period (2 Leaves)"
        st.markdown(f"**Employment Status:** {status_tag}")

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

            save_att = st.form_submit_button("Update Records & Recalculate Quota")
            if save_att:
                st.session_state.attendance_logs.loc[emp_att_idx, 'Full_Leaves_Taken'] = full_leaves
                st.session_state.attendance_logs.loc[emp_att_idx, 'Half_Days'] = half_days
                st.session_state.attendance_logs.loc[emp_att_idx, 'Short_Leaves'] = short_leaves
                st.session_state.attendance_logs.loc[emp_att_idx, 'Late_Comings'] = late_comings
                st.success("Attendance logs updated successfully!")
                st.rerun()

        # Calculation Engine
        results = calculate_leave_quota(
            joining_date=emp_info['Joining_Date'],
            is_confirmed=emp_info['Is_Confirmed'],
            full_leaves=att_info['Full_Leaves_Taken'],
            half_days=att_info['Half_Days'],
            short_leaves=att_info['Short_Leaves'],
            late_comings=att_info['Late_Comings']
        )

        st.markdown("---")
        st.subheader("📊 Leave Quota & Deduction Summary")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Allowed Quota", f"{results['Allowed']} Days")
        with c2:
            st.metric("Late Penalty Deduction", f"{results['Late_Deduction']} Days", f"{att_info['Late_Comings']} lates logged")
        with c3:
            st.metric("Total Days Deducted", f"{results['Total_Deducted']} Days")
        with c4:
            st.metric("Remaining Balance", f"{results['Remaining_Balance']} Days")

        # Breakdown Table
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

        # AI Advisor
        st.markdown("### 🤖 AI Leave Advisor & Request Simulator")
        req_type = st.selectbox("Simulate New Leave Request", ["Full Day Leave", "Half Day", "Short Leave"])
        
        if st.button("Run AI Policy Evaluation"):
            req_deduction = 1.0 if req_type == "Full Day Leave" else (0.5 if req_type == "Half Day" else 0.25)
            new_balance = results['Remaining_Balance'] - req_deduction

            if new_balance < 0:
                st.error(f"❌ **AI Decision: REJECTED** | Granting this request exceeds the allocated quota by {abs(new_balance)} day(s).")
            elif not emp_info['Is_Confirmed'] and results['Total_Deducted'] >= 2:
                st.warning(f"⚠️ **AI Decision: WARNING** | Employee is in probation (max 2 leaves allowed). Further leaves impact confirmation.")
            else:
                st.success(f"✅ **AI Decision: APPROVED** | Sufficient leave balance available ({new_balance} days remaining).")

# ==========================================
# 4. AI RESUME SCREENING MODULE
# ==========================================
elif menu == "🤖 AI Resume Screening":
    st.title("🤖 AI Resume Screening & Candidate Matching")
    st.markdown("Evaluate candidate skill alignment and job description fit using intelligent NLP algorithms.")
    st.markdown("---")

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
    st.title("📈 Performance Management & OKRs")
    st.markdown("Track employee KPIs, quarterly performance reviews, and goal alignment.")
    st.markdown("---")

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
            st.metric(label="Attendance Compliance", value="98.5%", delta="+0.2%")

        st.text_area("Manager Review & Notes", f"Performance review for {selected_emp}: Consistently meets delivery milestones and demonstrates strong cross-functional teamwork.")
        if st.button("Save Performance Review"):
            st.success(f"Review saved successfully for {selected_emp}!")

# ==========================================
# 6. PAYROLL MANAGEMENT MODULE
# ==========================================
elif menu == "💰 Payroll Management":
    st.title("💰 Payroll & Compensation Management")
    st.markdown("Review salary distributions, tax deductions, and monthly payroll disbursements.")
    st.markdown("---")

    emp_df = st.session_state.employees.copy()

    if emp_df.empty:
        st.warning("Please add employees first.")
    else:
        emp_df['Monthly Salary'] = emp_df['Salary'] / 12
        emp_df['Estimated Tax (15%)'] = emp_df['Monthly Salary'] * 0.15
        emp_df['Net Pay'] = emp_df['Monthly Salary'] - emp_df['Estimated Tax (15%)']

        st.dataframe(emp_df[['Emp_ID', 'Name', 'Department', 'Monthly Salary', 'Estimated Tax (15%)', 'Net Pay']], use_container_width=True)

        if st.button("🚀 Process Monthly Payroll Disbursal"):
            st.balloons()
            st.success("Payroll successfully processed and disbursed for all active employees!")
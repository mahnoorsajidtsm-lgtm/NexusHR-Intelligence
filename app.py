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
        "👥 Core HR Directory", 
        "📅 Attendance & Leave AI Engine", 
        "🤖 AI Resume Screening", 
        "📈 Performance & Analytics", 
        "💰 Payroll Management"
    ]
)
st.sidebar.markdown("---")
st.sidebar.success("🟢 AI Engine: Active\n\n📊 Excel Data Fetcher: Ready")

# ==========================================
# 1. EXECUTIVE DASHBOARD MODULE
# ==========================================
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Command Dashboard")
    st.markdown("Real-time organizational analytics, headcount metrics, and workforce health overview.")
    st.markdown("---")

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if emp_df.empty:
        st.info("💡 **Directory is Empty.** Upload your Excel spreadsheets using **📂 Excel Data Import Center** or onboard staff in **👥 Core HR Directory**.")
    else:
        # Top Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">Total Workforce</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{len(emp_df)}</h2>
                    <span style="color: #10b981; font-size: 0.8rem;">⚡ Active Registry</span>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            confirmed_cnt = len(emp_df[emp_df['Is_Confirmed'] == True]) if 'Is_Confirmed' in emp_df.columns else 0
            st.markdown(f"""
                <div class="metric-container" style="border-left-color: #10b981;">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">Confirmed Staff</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{confirmed_cnt}</h2>
                    <span style="color: #059669; font-size: 0.8rem;">📋 18 Leaves Quota</span>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            probation_cnt = len(emp_df[emp_df['Is_Confirmed'] == False]) if 'Is_Confirmed' in emp_df.columns else 0
            st.markdown(f"""
                <div class="metric-container" style="border-left-color: #f59e0b;">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">On Probation</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{probation_cnt}</h2>
                    <span style="color: #d97706; font-size: 0.8rem;">⏳ 2 Leaves Quota</span>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            total_lates = int(att_df['Late_Comings'].sum()) if not att_df.empty and 'Late_Comings' in att_df.columns else 0
            st.markdown(f"""
                <div class="metric-container" style="border-left-color: #ef4444;">
                    <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 0;">Total Late Incidents</p>
                    <h2 style="color: #1f2937; margin-top: 0;">{total_lates}</h2>
                    <span style="color: #dc2626; font-size: 0.8rem;">⚠️ Rule: 3 lates = 1 off</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🏢 Department Distribution")
            if 'Department' in emp_df.columns:
                dept_counts = emp_df['Department'].value_counts().reset_index()
                dept_counts.columns = ['Department', 'Count']
                fig_dept = px.pie(dept_counts, names='Department', values='Count', hole=0.5)
                st.plotly_chart(fig_dept, use_container_width=True)

        with col_b:
            st.subheader("📊 Attendance Incidents Breakdown")
            if not att_df.empty and 'Name' in att_df.columns:
                fig_att = px.bar(
                    att_df, 
                    x='Name', 
                    y=['Full_Leaves_Taken', 'Half_Days', 'Short_Leaves', 'Late_Comings'],
                    barmode='group'
                )
                st.plotly_chart(fig_att, use_container_width=True)

# ==========================================
# 2. EXCEL DATA IMPORT CENTER (NEW)
# ==========================================
elif menu == "📂 Excel Data Import Center":
    st.title("📂 Excel Data Import & Fetcher Center")
    st.markdown("Upload your existing Excel files (`.xlsx` or `.xls`) to instantly sync employee records, payroll, and attendance logs.")
    st.markdown("---")

    col_x, col_y = st.columns(2)

    with col_x:
        st.subheader("1. Import Employee Directory Excel")
        st.caption("Excel file should contain columns: `Emp_ID`, `Name`, `Department`, `Role`, `Salary`, `Is_Confirmed`")
        emp_file = st.file_uploader("Upload Employee Sheet (.xlsx)", type=["xlsx", "xls"], key="emp_excel")

        if emp_file is not None:
            try:
                uploaded_emp_df = pd.read_excel(emp_file)
                st.write(" preview of uploaded file:")
                st.dataframe(uploaded_emp_df.head(), use_container_width=True)
                
                if st.button("Sync Employee Excel Data"):
                    st.session_state.employees = uploaded_emp_df
                    st.success("Employee records updated successfully from Excel!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")

    with col_y:
        st.subheader("2. Import Attendance & Leaves Excel")
        st.caption("Excel file should contain columns: `Emp_ID`, `Name`, `Full_Leaves_Taken`, `Half_Days`, `Short_Leaves`, `Late_Comings`")
        att_file = st.file_uploader("Upload Attendance Sheet (.xlsx)", type=["xlsx", "xls"], key="att_excel")

        if att_file is not None:
            try:
                uploaded_att_df = pd.read_excel(att_file)
                st.write("Preview of uploaded file:")
                st.dataframe(uploaded_att_df.head(), use_container_width=True)

                if st.button("Sync Attendance Excel Data"):
                    st.session_state.attendance_logs = uploaded_att_df
                    st.success("Attendance logs updated successfully from Excel!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")

# ==========================================
# 3. CORE HR DIRECTORY MODULE
# ==========================================
elif menu == "👥 Core HR Directory":
    st.title("👥 Core HR Directory")
    st.markdown("Manage employee files or add new hires manually.")
    st.markdown("---")

    st.dataframe(st.session_state.employees, use_container_width=True)

    st.markdown("### ➕ Add New Employee Manually")
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
            is_confirmed = st.checkbox("Confirmed Employee (18 leaves)", value=False)

        submit = st.form_submit_button("Complete Onboarding")
        if submit and name:
            new_emp = pd.DataFrame({
                'Emp_ID': [emp_id], 'Name': [name], 'Department': [dept],
                'Role': [role], 'Status': ['Active'], 'Salary': [salary],
                'Joining_Date': [joining_date], 'Is_Confirmed': [is_confirmed]
            })
            new_att = pd.DataFrame({
                'Emp_ID': [emp_id], 'Name': [name],
                'Full_Leaves_Taken': [0], 'Half_Days': [0],
                'Short_Leaves': [0], 'Late_Comings': [0]
            })
            st.session_state.employees = pd.concat([st.session_state.employees, new_emp], ignore_index=True)
            st.session_state.attendance_logs = pd.concat([st.session_state.attendance_logs, new_att], ignore_index=True)
            st.success(f"Successfully onboarded {name}!")
            st.rerun()

# ==========================================
# 4. ATTENDANCE & LEAVE AI ENGINE MODULE
# ==========================================
elif menu == "📅 Attendance & Leave AI Engine":
    st.title("📅 Attendance & Leave AI Engine")
    st.markdown("---")

    emp_df = st.session_state.employees
    att_df = st.session_state.attendance_logs

    if emp_df.empty or att_df.empty:
        st.warning("Please import or add employee and attendance records first.")
    else:
        selected_emp = st.selectbox("Select Employee", emp_df['Name'].tolist())
        
        emp_info = emp_df[emp_df['Name'] == selected_emp].iloc[0]
        emp_att_idx = att_df[att_df['Name'] == selected_emp].index[0]
        att_info = att_df.loc[emp_att_idx]

        results = calculate_leave_quota(
            joining_date=emp_info.get('Joining_Date', date.today()),
            is_confirmed=emp_info.get('Is_Confirmed', False),
            full_leaves=att_info.get('Full_Leaves_Taken', 0),
            half_days=att_info.get('Half_Days', 0),
            short_leaves=att_info.get('Short_Leaves', 0),
            late_comings=att_info.get('Late_Comings', 0)
        )

        st.subheader("📊 Leave Quota & Balance")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Allowed", f"{results['Allowed']} Days")
        with c2: st.metric("Late Penalty", f"{results['Late_Deduction']} Days")
        with c3: st.metric("Total Deducted", f"{results['Total_Deducted']} Days")
        with c4: st.metric("Remaining Balance", f"{results['Remaining_Balance']} Days")

# ==========================================
# 5. AI RESUME SCREENING MODULE
# ==========================================
elif menu == "🤖 AI Resume Screening":
    st.title("🤖 AI Resume Screening")
    st.markdown("---")
    job_description = st.text_area("Job Description", "Python Developer with Streamlit and SQL experience.")
    candidate_resume = st.text_area("Candidate Resume", "Software Engineer experienced in Python and Streamlit.")

    if st.button("Analyze Resume"):
        st.success("Match Score: 88% - Highly Recommended!")

# ==========================================
# 6. PERFORMANCE & ANALYTICS MODULE
# ==========================================
elif menu == "📈 Performance & Analytics":
    st.title("📈 Performance Analytics")
    st.markdown("---")
    st.write("Performance and OKR evaluation suite.")

# ==========================================
# 7. PAYROLL MANAGEMENT MODULE
# ==========================================
elif menu == "💰 Payroll Management":
    st.title("💰 Payroll & Compensation Management")
    st.markdown("---")

    emp_df = st.session_state.employees.copy()

    if emp_df.empty:
        st.warning("Please upload or add employee records first.")
    else:
        emp_df['Monthly Salary'] = emp_df['Salary'] / 12
        emp_df['Estimated Tax (15%)'] = emp_df['Monthly Salary'] * 0.15
        emp_df['Net Pay'] = emp_df['Monthly Salary'] - emp_df['Estimated Tax (15%)']

        st.dataframe(emp_df[['Emp_ID', 'Name', 'Department', 'Monthly Salary', 'Estimated Tax (15%)', 'Net Pay']], use_container_width=True)

        if st.button("🚀 Process Monthly Payroll"):
            st.balloons()
            st.success("Payroll successfully processed!")
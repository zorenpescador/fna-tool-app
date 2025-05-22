import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# === Future Value Calculator (Compounding Monthly) ===
def future_value_monthly(pmt, annual_rate, months):
    r = annual_rate / 12
    if r == 0:
        return pmt * months
    return pmt * (((1 + r) ** months - 1) / r)

# === Required Monthly Saving to Reach Target ===
def required_monthly_saving(target, rate, months):
    r = rate / 12
    if r == 0:
        return target / months
    return target * r / (((1 + r) ** months - 1))

# === Education Fund Calculation ===
def calculate_education_fund(child_age, college_age, current_annual_tuition, tuition_inflation, college_years):
    years_until_college = max(0, college_age - child_age)
    tuition_projection = []
    total_fund_needed = 0

    for year in range(college_years):
        year_of_college = years_until_college + year
        projected_tuition = current_annual_tuition * ((1 + tuition_inflation) ** year_of_college)
        tuition_projection.append(projected_tuition)
        total_fund_needed += projected_tuition

    return {
        "years_until_college": years_until_college,
        "tuition_projection": tuition_projection,
        "total_fund_needed": total_fund_needed
    }

def generate_pdf(data, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_title("FNA Summary Report")
    pdf.cell(200, 10, txt=f"FNA Summary for {name}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)

    for key, value in data.items():
        label = key.replace("_", " ").capitalize()
        pdf.cell(200, 10, txt=f"{label}: ₱{value:,.2f}", ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# === Streamlit App ===
def run_streamlit_app():
    st.title("📊 FNA Tool by Zoren Pescador - UH ManulifePH")

    with st.form("fna_form"):
        st.subheader("👨‍👩‍👧 Basic Info & Budget")
        name = st.text_input("Full Name")
        age = st.number_input("Your Age", 18, 100, 30)
        income = st.number_input("Monthly Income (₱)", 0.0, value=50000.0)
        expenses = st.number_input("Monthly Expenses (₱)", 0.0, value=20000.0)
        savings = st.number_input("Existing Savings (₱)", 0.0, value=100000.0)

        st.subheader("🛡️ Life Insurance")
        insurance = st.number_input("Life Insurance Coverage (₱)", 0.0, value=250000.0)

        st.subheader("🩺 Health Insurance Plan")
        current_health_coverage = st.number_input("Your Current Health Coverage (₱)", 0.0, value=100000.0)
        desired_coverage_per_person = st.number_input("Desired Health Coverage per Person (₱)", 0.0, value=500000.0)
        num_dependents = st.slider("Number of People to Cover (including you)", 1, 10, 4)

        st.subheader("💰 Savings")
        emergency_fund_needed = expenses * 6

        st.subheader("🎓 Educational Plan")
        child_age = st.number_input("Child's Current Age", 0, 17, 5)
        college_age = st.number_input("Target College Start Age", 15, 25, 18)
        current_annual_tuition = st.number_input("Current Annual Tuition (₱)", 10000.0, 1000000.0, 60000.0)
        tuition_inflation = st.slider("Annual Tuition Inflation Rate (%)", 0.0, 10.0, 5.0) / 100
        college_years = st.slider("Years of College", 2, 6, 4)

        st.subheader("🧓 Retirement Plan")
        retirement_age = st.slider("Target Retirement Age", 50, 70, 60)
        years_in_retirement = st.slider("Years in Retirement", 10, 30, 20)
        inflation_rate = st.slider("Expected Inflation Rate (%)", 0.0, 10.0, 1.5) / 100
        monthly_retirement_saving = st.number_input("How much can you save monthly for retirement? (₱)", 0.0, value=8000.0)

        submitted = st.form_submit_button("Generate Report")

    if submitted:
        needs = income * 0.50
        wants = income * 0.30
        savings_goal = income * 0.20
        recommended_life_coverage = income * 12 * 10
        insurance_gap = max(0, recommended_life_coverage - insurance)

        years_to_retirement = max(0, retirement_age - age)
        months_to_retirement = years_to_retirement * 12
        annual_expenses_now = expenses * 12
        inflation_multiplier = (1 + inflation_rate) ** years_to_retirement
        inflated_annual_expenses = annual_expenses_now * inflation_multiplier
        total_retirement_fund = inflated_annual_expenses * years_in_retirement
        fund_4 = future_value_monthly(monthly_retirement_saving, 0.04, months_to_retirement)
        fund_8 = future_value_monthly(monthly_retirement_saving, 0.08, months_to_retirement)
        fund_10 = future_value_monthly(monthly_retirement_saving, 0.10, months_to_retirement)

        edu = calculate_education_fund(child_age, college_age, current_annual_tuition, tuition_inflation, college_years)
        months_to_college = edu['years_until_college'] * 12
        monthly_needed_no_growth = edu['total_fund_needed'] / months_to_college if months_to_college > 0 else 0
        monthly_needed_with_growth = required_monthly_saving(edu['total_fund_needed'], 0.06, months_to_college)

        total_desired_health = desired_coverage_per_person * num_dependents
        health_coverage_gap = max(0, total_desired_health - current_health_coverage)

        st.subheader(f"📋 FNA Summary for {name}")
        st.write("### 📌 Monthly Budget Breakdown")
        st.write("The 50-30-20 rule is a simple, effective budgeting framework designed to help people manage their money wisely without complex calculations.")
        st.write(f"- Needs: ₱{needs:.2f}")
        st.write(f"- Wants: ₱{wants:.2f}")
        st.write(f"- Savings Goal: ₱{savings_goal:.2f}")
        st.write("### 🛟 Emergency Fund")
        st.write(f"- Recommended: ₱{emergency_fund_needed:.2f}")

        st.write("### 🛡️ Life Insurance")
        st.write(f"- Current Coverage: ₱{insurance:.2f}")
        st.write(f"- Recommended: ₱{recommended_life_coverage:.2f}")
        st.write(f"- Gap: ₱{insurance_gap:.2f}")

        st.write("### 🩺 Health Insurance Summary")
        st.write(f"- Total Desired Health Coverage: ₱{total_desired_health:,.2f}")
        st.write(f"- Current Health Coverage: ₱{current_health_coverage:,.2f}")
        st.write(f"**🩺 Health Coverage Gap: ₱{health_coverage_gap:,.2f}**")

        st.subheader("🎓 Educational Plan Summary")
        st.write(f"- Years Until College: {edu['years_until_college']}")
        for i, cost in enumerate(edu['tuition_projection'], 1):
            st.write(f"Year {i} Tuition: ₱{cost:,.2f}")
        st.write(f"**Total Education Fund Needed: ₱{edu['total_fund_needed']:,.2f}**")
        st.write(f"📌 Monthly Savings Needed (No Compounding): ₱{monthly_needed_no_growth:,.2f}")
        st.write(f"📈 Monthly Savings Needed (6% Growth): ₱{monthly_needed_with_growth:,.2f}")

        st.write("### 🧓 Retirement Planning")
        st.write(f"- Years to Retirement: {years_to_retirement}")
        st.write(f"- Inflation-Adjusted Annual Expenses: ₱{inflated_annual_expenses:.2f}")
        st.write(f"- Total Retirement Fund Needed: ₱{total_retirement_fund:.2f}")
        st.write(f"- Monthly Saving: ₱{monthly_retirement_saving:.2f}")
        st.write(f"**Projected Retirement Fund:**")
        st.write(f"• 4%: ₱{fund_4:.2f}")
        st.write(f"• 8%: ₱{fund_8:.2f}")
        st.write(f"• 10%: ₱{fund_10:.2f}")
        st.write(f"• Supports ₱{fund_4 / years_in_retirement:.2f}/year at 4%")
        st.write(f"• Supports ₱{fund_8 / years_in_retirement:.2f}/year at 8%")
        st.write(f"• Supports ₱{fund_10 / years_in_retirement:.2f}/year at 10%")

        # Retirement Fund Growth Chart
        st.subheader("📈 Retirement Fund Growth Projection")
        years_range = list(range(1, years_to_retirement + 1))
        fund_4_list = [future_value_monthly(monthly_retirement_saving, 0.04, y * 12) for y in years_range]
        fund_8_list = [future_value_monthly(monthly_retirement_saving, 0.08, y * 12) for y in years_range]
        fund_10_list = [future_value_monthly(monthly_retirement_saving, 0.10, y * 12) for y in years_range]
        target_line = [total_retirement_fund] * len(years_range)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_range, y=fund_4_list, mode='lines', name='4% Return'))
        fig.add_trace(go.Scatter(x=years_range, y=fund_8_list, mode='lines', name='8% Return'))
        fig.add_trace(go.Scatter(x=years_range, y=fund_10_list, mode='lines', name='10% Return'))
        fig.add_trace(go.Scatter(x=years_range, y=target_line, mode='lines', name='Target Retirement Fund', line=dict(dash='dash')))

        fig.update_layout(
            title="Projected Retirement Fund vs Goal",
            xaxis_title="Years Until Retirement",
            yaxis_title="Projected Fund Value (₱)",
            legend_title="Growth Rate",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Collect results into a dictionary
        pdf_data = {
        "needs": needs,
        "wants": wants,
        "savings_goal": savings_goal,
        "emergency_fund_needed": emergency_fund_needed,
        "recommended_life_coverage": recommended_life_coverage,
        "insurance_gap": insurance_gap,
        "total_desired_health": total_desired_health,
        "health_coverage_gap": health_coverage_gap,
        "total_education_fund": edu['total_fund_needed'],
        "retirement_fund_target": total_retirement_fund,
        "fund_4": fund_4,
        "fund_8": fund_8,
        "fund_10": fund_10
        }

        pdf_file = generate_pdf(pdf_data, name)
        st.download_button("📄 Download PDF Summary", data=open(pdf_file, "rb"), file_name="fna_summary.pdf")

run_streamlit_app()

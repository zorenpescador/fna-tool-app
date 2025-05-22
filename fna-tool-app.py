# Reinjecting the final working app code (with PDF and chart) after reset

fixed_app_code = """
import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import datetime
import os

# === Future Value Calculator ===
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

# === PDF Generator ===
def generate_pdf(data, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.set_title("FNA Summary Report")
    pdf.cell(200, 10, txt=f"FNA Summary for {name}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)
    for key, value in data.items():
        label = key.replace("_", " ").capitalize()
        if isinstance(value, (int, float)):
            formatted_value = f"₱{value:,.2f}"
        elif isinstance(value, list):
            formatted_value = ", ".join([f"₱{v:,.2f}" if isinstance(v, (int, float)) else str(v) for v in value])
        else:
            formatted_value = str(value)
        pdf.cell(200, 10, txt=f"{label}: {formatted_value}", ln=True)
    fd, path = tempfile.mkstemp(suffix=".pdf")
    pdf.output(path)
    return path

# === Streamlit App ===
def run_streamlit_app():
    st.title("📊 FNA Tool by Zoren Pescador - UH ManulifePH")

    with st.form("fna_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Your Age", 18, 100, 30)
        income = st.number_input("Monthly Income (₱)", 0.0, value=50000.0)
        expenses = st.number_input("Monthly Expenses (₱)", 0.0, value=20000.0)
        savings = st.number_input("Existing Savings (₱)", 0.0, value=100000.0)
        insurance = st.number_input("Life Insurance Coverage (₱)", 0.0, value=250000.0)
        current_health_coverage = st.number_input("Current Health Coverage (₱)", 0.0, value=100000.0)
        desired_coverage_per_person = st.number_input("Desired Health Coverage per Person (₱)", 0.0, value=500000.0)
        num_dependents = st.slider("People to Cover (incl. you)", 1, 10, 4)
        child_age = st.number_input("Child's Age", 0, 17, 5)
        college_age = st.number_input("College Start Age", 15, 25, 18)
        current_annual_tuition = st.number_input("Current Annual Tuition (₱)", 10000.0, 1000000.0, 60000.0)
        tuition_inflation = st.slider("Tuition Inflation Rate (%)", 0.0, 10.0, 5.0) / 100
        college_years = st.slider("Years of College", 2, 6, 4)
        retirement_age = st.slider("Target Retirement Age", 50, 70, 60)
        years_in_retirement = st.slider("Years in Retirement", 10, 30, 20)
        inflation_rate = st.slider("Inflation Rate (%)", 0.0, 10.0, 1.5) / 100
        monthly_retirement_saving = st.number_input("Monthly Retirement Saving (₱)", 0.0, value=8000.0)
        submitted = st.form_submit_button("Generate Report")

    if submitted:
        needs = income * 0.50
        wants = income * 0.30
        savings_goal = income * 0.20
        emergency_fund_needed = expenses * 6
        recommended_life_coverage = income * 12 * 10
        insurance_gap = max(0, recommended_life_coverage - insurance)
        years_to_retirement = max(0, retirement_age - age)
        months_to_retirement = years_to_retirement * 12
        annual_expenses_now = expenses * 12
        inflated_annual_expenses = annual_expenses_now * ((1 + inflation_rate) ** years_to_retirement)
        total_retirement_fund = inflated_annual_expenses * years_in_retirement
        fund_4 = future_value_monthly(monthly_retirement_saving, 0.04, months_to_retirement)
        fund_8 = future_value_monthly(monthly_retirement_saving, 0.08, months_to_retirement)
        fund_10 = future_value_monthly(monthly_retirement_saving, 0.10, months_to_retirement)
        edu = calculate_education_fund(child_age, college_age, current_annual_tuition, tuition_inflation, college_years)
        months_to_college = edu['years_until_college'] * 12
        monthly_needed_with_growth = required_monthly_saving(edu['total_fund_needed'], 0.06, months_to_college)
        total_desired_health = desired_coverage_per_person * num_dependents
        health_coverage_gap = max(0, total_desired_health - current_health_coverage)

        st.subheader(f"📋 Summary for {name}")
        st.write(f"• Needs: ₱{needs:,.2f} | Wants: ₱{wants:,.2f} | Savings: ₱{savings_goal:,.2f}")
        st.write(f"• Life Insurance Gap: ₱{insurance_gap:,.2f} | Health Gap: ₱{health_coverage_gap:,.2f}")
        st.write(f"• Total Education Fund: ₱{edu['total_fund_needed']:,.2f} | Monthly Save: ₱{monthly_needed_with_growth:,.2f}")
        st.write(f"• Retirement Goal: ₱{total_retirement_fund:,.2f}")
        st.write(f"• Retirement Fund at 4%: ₱{fund_4:,.2f} | 8%: ₱{fund_8:,.2f} | 10%: ₱{fund_10:,.2f}")

        years_range = list(range(1, years_to_retirement + 1))
        fund_4_list = [future_value_monthly(monthly_retirement_saving, 0.04, y * 12) for y in years_range]
        fund_8_list = [future_value_monthly(monthly_retirement_saving, 0.08, y * 12) for y in years_range]
        fund_10_list = [future_value_monthly(monthly_retirement_saving, 0.10, y * 12) for y in years_range]
        target_line = [total_retirement_fund] * len(years_range)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years_range, y=fund_4_list, mode='lines', name='4% Return'))
        fig.add_trace(go.Scatter(x=years_range, y=fund_8_list, mode='lines', name='8% Return'))
        fig.add_trace(go.Scatter(x=years_range, y=fund_10_list, mode='lines', name='10% Return'))
        fig.add_trace(go.Scatter(x=years_range, y=target_line, mode='lines', name='Target Fund', line=dict(dash='dash')))
        fig.update_layout(title="Retirement Fund Growth", xaxis_title="Years", yaxis_title="₱", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

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

        pdf_path = generate_pdf(pdf_data, name)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF Summary", data=f, file_name="fna_summary.pdf")
        os.remove(pdf_path)

run_streamlit_app()
"""

# Write to downloadable file
with open("/mnt/data/fna_app_fixed.py", "w") as f:
    f.write(fixed_app_code)

"/mnt/data/fna_app_fixed.py"

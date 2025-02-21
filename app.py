import streamlit as st
from google.generativeai import GenerativeModel, configure
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("API Key not found. Please set GEMINI_API_KEY in .env")
    st.stop()

# Configure Gemini API
configure(api_key=API_KEY)
model = GenerativeModel("gemini-1.5-flash")

# Function to get advanced investment advice
def get_investment_advice(amount, risk, goal, horizon, income, tax_bracket, existing_investments, monthly_expenses):
    try:
        prompt = f"""
            I am an investor in India with the following details:
            - Investment Amount: ₹{amount}
            - Risk Tolerance: {risk}
            - Goal: {goal}
            - Investment Horizon: {horizon} years
            - Annual Income: ₹{income}
            - Tax Bracket: {tax_bracket}%
            - Existing Investments: {existing_investments}
            - Monthly Expenses: ₹{monthly_expenses}

            Provide a detailed investment strategy for the Indian market, including:
            - A portfolio allocation (equities and debt) with specific percentages and fund examples, considering my income and expenses.
            - Tax-saving options under Indian tax laws (e.g., ELSS under Section 80C up to ₹1.5 lakh, municipal bonds), tailored to my tax bracket and income.
            - Sector analysis for growth (e.g., technology, healthcare, industrials) with fund recommendations suitable for my risk and horizon.
            - Stable funds (e.g., large-cap, bluechip) that perform well during market downturns, aligning with my financial profile.
            Format your response as:
            **Portfolio Allocation:**
            - [Asset Type]: [Percentage] - [Fund Examples]
            **Tax Savings:**
            - [Option]: [Details]
            **Sector Growth:**
            - [Sector]: [Growth Potential] - [Fund Examples]
            **Stable Funds:**
            - [Fund]: [Reasoning]
            Use Indian mutual funds and securities available in 2025. Provide reasoning based on my financial situation.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error fetching advice: {str(e)}"

# Function to simplify the advice
def simplify_advice(detailed_advice):
    try:
        prompt = f"""
            Simplify this detailed investment advice for a beginner in India:
            {detailed_advice}
            Provide a short, easy-to-understand version in simple language, keeping key points like:
            - Where to put the money (e.g., stocks, savings).
            - How to save on taxes.
            - What grows well.
            - What stays safe.
            Format it as:
            **Simple Plan:**
            - [Key Point]: [Simple Explanation]
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Couldn’t simplify the advice. Please try again."

# Function to create income allocation pie chart
def create_income_chart(income, monthly_expenses, investment_amount):
    annual_expenses = monthly_expenses * 12
    savings_and_investments = income - annual_expenses
    if savings_and_investments < investment_amount:
        investment_amount = savings_and_investments  # Adjust if investment exceeds savings
    remaining_savings = savings_and_investments - investment_amount

    labels = ['Expenses', 'Investments', 'Remaining Savings']
    values = [annual_expenses, investment_amount, remaining_savings]
    colors = ['#FF9999', '#66B2FF', '#99FF99']

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3, marker=dict(colors=colors))])
    fig.update_layout(title_text="How Your Annual Income Breaks Down", title_x=0.5)
    return fig

# Streamlit UI
st.title("Advanced GenAI Financial Assistant for India")

st.write("Provide your financial details below for a personalized investment strategy tailored to Indian markets. Hover over the '?' icons for explanations.")

with st.form(key="investment_form"):
    # Basic Investment Details
    st.subheader("Investment Details")
    amount = st.number_input(
        "Investment Amount (₹)", 
        min_value=0, 
        step=1000, 
        help="The amount of money you want to invest right now, e.g., ₹5,00,000. This is the lump sum you’re ready to put into investments."
    )
    risk = st.selectbox(
        "Risk Tolerance", 
        ["Low", "Medium", "High"], 
        help="How comfortable you are with the value of your investment going up and down. 'Low' means you prefer safety, 'Medium' is a balance, and 'High' means you’re okay with bigger risks for potentially higher returns."
    )
    goal = st.text_input(
        "Goal", 
        help="What you’re saving for, e.g., retirement, buying a house, or your child’s education. This helps decide the best investment plan."
    )
    horizon = st.slider(
        "Investment Horizon (Years)", 
        min_value=1, 
        max_value=30, 
        value=10, 
        help="How long you plan to keep your money invested before using it, e.g., 10 years. Longer horizons can handle more risk, while shorter ones need safer options."
    )

    # Financial Profile
    st.subheader("Financial Profile")
    income = st.number_input(
        "Annual Income (₹)", 
        min_value=0, 
        step=10000, 
        help="Your total yearly income before taxes, e.g., ₹15,00,000. This helps us figure out your tax savings and investment capacity."
    )
    tax_bracket = st.selectbox(
        "Tax Bracket (%)", 
        [10, 20, 30, 40], 
        help="The percentage of your income you pay as tax, based on Indian tax slabs. For example, 30% applies to income above ₹15 lakh (2025 slabs). This affects tax-saving options."
    )
    existing_investments = st.text_area(
        "Existing Investments", 
        help="List any investments you already have, e.g., '₹2 lakh in Fixed Deposit, ₹1 lakh in mutual funds', or write 'None'. This helps avoid overlap and plan better."
    )
    monthly_expenses = st.number_input(
        "Monthly Expenses (₹)", 
        min_value=0, 
        step=1000, 
        help="How much you spend each month, e.g., ₹50,000. This shows how much income you can spare for investing after covering your costs."
    )

    submit_button = st.form_submit_button(label="Get Investment Advice")

if submit_button:
    if amount <= 0 or not goal or income <= 0 or monthly_expenses <= 0:
        st.warning("Please fill in all fields with valid values.")
    else:
        with st.spinner("Generating your personalized investment strategy..."):
            detailed_advice = get_investment_advice(
                amount, risk.lower(), goal, horizon, income, tax_bracket, 
                existing_investments if existing_investments else "None", monthly_expenses
            )
            st.session_state['detailed_advice'] = detailed_advice  # Store in session state
            st.markdown("### Your Detailed Investment Strategy")
            st.markdown(detailed_advice)

            # Show income allocation chart
            st.markdown("### How Your Income Breaks Down")
            fig = create_income_chart(income, monthly_expenses, amount)
            st.plotly_chart(fig)

        # Add "Make It Simple" button
        if 'detailed_advice' in st.session_state:
            if st.button("Make It Simple"):
                with st.spinner("Simplifying your strategy..."):
                    simple_advice = simplify_advice(st.session_state['detailed_advice'])
                    st.markdown("### Simplified Investment Plan")
                    st.markdown(simple_advice)

st.markdown("""
    *Disclaimer*: This advice is generated based on general market trends and Indian tax laws as of 2025. 
    Consult a financial advisor for personalized recommendations. Do not share sensitive personal data.
""")
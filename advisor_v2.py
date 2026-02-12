import json
import os
from datetime import datetime

# =========================
# SIMPLE SETTINGS
# =========================
DATA_FOLDER = "saved_profiles"
REPORT_FOLDER = "reports"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

DISCLAIMER = (
    "\nDISCLAIMER: This tool is for educational purposes only and is NOT financial advice.\n"
    "Always do your own research or talk to a licensed advisor.\n"
)

# =========================
# BASIC HELPER FUNCTIONS
# =========================
def header(title):
    print("\n" + "="*55)
    print(title)
    print("="*55)

def pause():
    input("\nPress Enter to continue...")

def ask_number(text, default=None, min_val=None):
    while True:
        raw = input(f"{text} [{default}]: ").strip()
        if raw == "" and default is not None:
            return float(default)
        try:
            val = float(raw)
            if min_val is not None and val < min_val:
                print(f"Must be at least {min_val}.")
                continue
            return val
        except:
            print("Please type a number.")

def ask_yes_no(text, default=False):
    hint = " [Y/n]" if default else " [y/N]"
    while True:
        raw = input(text + hint + ": ").strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Type y or n.")

def pick_from_list(title, options):
    print("\n" + title)
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")
    while True:
        raw = input("Choose a number: ").strip()
        if raw.isdigit():
            num = int(raw)
            if 1 <= num <= len(options):
                return options[num - 1]
        print("Pick a valid number.")

# =========================
# SAVE / LOAD PROFILES
# =========================
def save_profile(profile):
    name = profile.get("name", "User").strip() or "User"
    path = os.path.join(DATA_FOLDER, f"{name}.json")
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"✅ Saved profile: {name}")

def load_profile(name):
    path = os.path.join(DATA_FOLDER, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def list_profiles():
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    return [f.replace(".json", "") for f in files]

# =========================
# FEATURE 1: RISK QUIZ
# =========================
def risk_quiz(profile):
    header("Risk Quiz")

    score = 0

    q1 = pick_from_list(
        "If your investments dropped 20%, what would you do?",
        ["Sell everything", "Sell some", "Hold", "Buy more"]
    )
    score += ["Sell everything", "Sell some", "Hold", "Buy more"].index(q1)

    q2 = pick_from_list(
        "How long will you invest for?",
        ["1-3 years", "3-7 years", "7-15 years", "15+ years"]
    )
    score += ["1-3 years", "3-7 years", "7-15 years", "15+ years"].index(q2)

    q3 = pick_from_list(
        "How stable is your income?",
        ["Not stable", "Somewhat stable", "Stable", "Very stable"]
    )
    score += ["Not stable", "Somewhat stable", "Stable", "Very stable"].index(q3)

    # Decide style
    if score <= 3:
        style = "Conservative"
    elif score <= 6:
        style = "Balanced"
    elif score <= 9:
        style = "Growth"
    else:
        style = "Aggressive"

    profile["risk_score"] = score
    profile["risk_style"] = style

    print(f"\nYour risk score: {score}")
    print(f"Your risk style: {style}")

    return profile

# =========================
# FEATURE 2: MINI FINANCIAL PLAN
# =========================
def mini_financial_plan(profile, mode):
    header("Mini Financial Plan")

    income = profile["monthly_income"]
    expenses = profile["monthly_expenses"]
    savings = profile["cash_savings"]
    debt = profile["total_debt"]
    debt_apr = profile["debt_apr"]

    surplus = income - expenses

    # emergency fund target
    emergency_3 = expenses * 3
    emergency_6 = expenses * 6

    # simple budget suggestion (50/30/20 rule)
    needs = income * 0.50
    wants = income * 0.30
    save_invest = income * 0.20

    # debt strategy
    if debt_apr >= 8:
        debt_strategy = "Avalanche (pay highest interest debt first)"
    else:
        debt_strategy = "Snowball (pay smallest balance first)"

    # investing allocation based on risk style
    style = profile.get("risk_style", "Balanced")
    if style == "Conservative":
        allocation = "40% Stocks / 50% Bonds / 10% Cash"
    elif style == "Balanced":
        allocation = "60% Stocks / 35% Bonds / 5% Cash"
    elif style == "Growth":
        allocation = "80% Stocks / 15% Bonds / 5% Cash"
    else:
        allocation = "90% Stocks / 5% Bonds / 5% Cash"

    warnings = []
    if surplus < 0:
        warnings.append("Your expenses are higher than your income. Cut spending or increase income first.")
    if savings < expenses:
        warnings.append("You have less than 1 month of savings. Build emergency fund first.")
    if debt > 0 and debt_apr >= 10:
        warnings.append("High-interest debt detected. Paying it off is usually the best 'investment'.")

    # Print the plan
    print(f"Monthly Surplus: ${surplus:,.2f}")
    print(f"Emergency Fund Goal: ${emergency_3:,.2f} to ${emergency_6:,.2f}")
    print(f"Suggested Budget (50/30/20):")
    print(f" - Needs: ${needs:,.2f}")
    print(f" - Wants: ${wants:,.2f}")
    print(f" - Save/Invest: ${save_invest:,.2f}")
    print(f"Debt Strategy: {debt_strategy}")
    print(f"Suggested Portfolio Allocation (based on {style}): {allocation}")

    if warnings:
        print("\nImportant Warnings:")
        for w in warnings:
            print(" - " + w)

    # Explanation modes (simple)
    print("\nExplanation Mode:", mode)
    if mode == "Beginner":
        print("This plan starts with safety (emergency fund), then debt, then investing.")
    elif mode == "Intermediate":
        print("This plan prioritizes match > emergency fund > high-interest debt > investing.")
    else:
        print("This plan considers opportunity cost, inflation, and risk management.")

    profile["latest_plan"] = {
        "surplus": surplus,
        "emergency_fund": (emergency_3, emergency_6),
        "budget_50_30_20": (needs, wants, save_invest),
        "debt_strategy": debt_strategy,
        "allocation": allocation,
        "warnings": warnings
    }

    return profile

# =========================
# FEATURE 3: PORTFOLIO SIMULATOR
# =========================
def portfolio_simulator(profile, mode):
    header("Portfolio Growth Simulator")

    years = int(ask_number("How many years do you want to invest?", default=10, min_val=1))
    monthly = ask_number("Monthly contribution ($)", default=200, min_val=0)
    starting = ask_number("Starting balance ($)", default=0, min_val=0)

    scenario = pick_from_list("Choose a market scenario", ["Low", "Base", "High"])
    if scenario == "Low":
        annual_return = 0.04
    elif scenario == "Base":
        annual_return = 0.07
    else:
        annual_return = 0.10

    inflation = 0.03
    include_bad_year = True

    months = years * 12
    balance = starting
    total_contrib = 0

    monthly_return = (1 + annual_return) ** (1/12) - 1

    bad_month = 18 if include_bad_year and months > 24 else None

    for m in range(1, months + 1):
        balance += monthly
        total_contrib += monthly

        # "bad year" shock (one-time drop)
        if bad_month and m == bad_month:
            balance *= 0.75

        balance *= (1 + monthly_return)

    real_balance = balance / ((1 + inflation) ** years)

    print("\nSimulation Results:")
    print(f"Total Contributions: ${total_contrib:,.2f}")
    print(f"Ending Balance (normal): ${balance:,.2f}")
    print(f"Ending Balance (inflation-adjusted): ${real_balance:,.2f}")
    print(f"Bad year included: Yes")

    print("\nExplanation Mode:", mode)
    if mode == "Beginner":
        print("Inflation-adjusted means how much it would feel like in today's dollars.")
    elif mode == "Intermediate":
        print("This assumes steady returns plus one downturn to show emotional realism.")
    else:
        print("This is a simplified model; real markets vary, but it helps planning behavior.")

    profile["latest_simulation"] = {
        "years": years,
        "monthly": monthly,
        "starting": starting,
        "scenario": scenario,
        "annual_return": annual_return,
        "ending_nominal": balance,
        "ending_real": real_balance,
        "total_contributions": total_contrib
    }

    return profile

# =========================
# FEATURE 4: GOAL PLANNER
# =========================
def goal_planner(profile, mode):
    header("Goal-Based Planning")

    goal_type = pick_from_list("Choose a goal type", ["Emergency Fund", "Down Payment", "Car", "Retirement", "Custom"])
    target = ask_number("Goal target amount ($)", default=10000, min_val=0)
    years = int(ask_number("How many years to reach it?", default=3, min_val=1))

    monthly_needed = target / (years * 12)

    print("\nGoal Result:")
    print(f"Goal: {goal_type}")
    print(f"Target: ${target:,.2f}")
    print(f"Time: {years} years")
    print(f"Monthly needed (simple): ${monthly_needed:,.2f}")

    if mode == "Beginner":
        print("This is just goal ÷ months. It’s the easiest baseline.")
    elif mode == "Intermediate":
        print("This ignores investment growth. Investing could reduce the monthly amount.")
    else:
        print("A real plan would model expected returns, inflation, and uncertainty.")

    profile["latest_goal"] = {
        "goal_type": goal_type,
        "target": target,
        "years": years,
        "monthly_needed": monthly_needed
    }

    return profile

# =========================
# FEATURE 5: EXPORT REPORT
# =========================
def export_report(profile, mode):
    header("Export Report")

    name = profile.get("name", "User")
    filename = os.path.join(REPORT_FOLDER, f"{name}_report.txt")

    lines = []
    lines.append("AI Wealth Advisor v2 - Report")
    lines.append(f"Name: {name}")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Mode: {mode}")
    lines.append("="*55)

    lines.append("\nPROFILE:")
    for k in ["age","monthly_income","monthly_expenses","cash_savings","total_debt","debt_apr"]:
        lines.append(f"- {k}: {profile.get(k)}")

    if "risk_score" in profile:
        lines.append("\nRISK:")
        lines.append(f"- risk_score: {profile.get('risk_score')}")
        lines.append(f"- risk_style: {profile.get('risk_style')}")

    if "latest_plan" in profile:
        lines.append("\nLATEST PLAN:")
        for k,v in profile["latest_plan"].items():
            lines.append(f"- {k}: {v}")

    if "latest_simulation" in profile:
        lines.append("\nLATEST SIMULATION:")
        for k,v in profile["latest_simulation"].items():
            lines.append(f"- {k}: {v}")

    if "latest_goal" in profile:
        lines.append("\nLATEST GOAL:")
        for k,v in profile["latest_goal"].items():
            lines.append(f"- {k}: {v}")

    lines.append("\nDISCLAIMER: Educational only. Not financial advice.")

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Report saved to: {filename}")

# =========================
# MAIN MENU
# =========================
def main():
    header("AI Wealth Advisor v2 (Simple One-File Version)")
    print(DISCLAIMER)

    profile = None
    mode = "Beginner"

    while True:
        header("MAIN MENU")
        print("1) Create Profile")
        print("2) Load Profile")
        print("3) Set Explanation Mode")
        print("4) Run Risk Quiz")
        print("5) Build Mini Financial Plan")
        print("6) Run Portfolio Simulator")
        print("7) Goal Planner")
        print("8) Export Report")
        print("9) Exit")

        choice = input("Pick a number: ").strip()

        if choice == "1":
            header("Create Profile")
            name = input("Name: ").strip() or "User"
            age = ask_number("Age", default=22, min_val=13)

            income = ask_number("Monthly income ($)", default=3500, min_val=0)
            expenses = ask_number("Monthly expenses ($)", default=2500, min_val=0)
            savings = ask_number("Cash savings ($)", default=500, min_val=0)
            debt = ask_number("Total debt ($)", default=0, min_val=0)
            apr = ask_number("Average debt APR (%)", default=0, min_val=0)

            profile = {
                "name": name,
                "age": age,
                "monthly_income": income,
                "monthly_expenses": expenses,
                "cash_savings": savings,
                "total_debt": debt,
                "debt_apr": apr
            }
            save_profile(profile)
            pause()

        elif choice == "2":
            header("Load Profile")
            name = input("Type profile name: ").strip()
            loaded = load_profile(name)
            if loaded:
                profile = loaded
                print(f"✅ Loaded {name}")
            else:
                print("❌ Profile not found.")
                print("Saved profiles:", list_profiles())
            pause()

        elif choice == "3":
            mode = pick_from_list("Choose explanation mode", ["Beginner", "Intermediate", "Advanced"])
            print(f"✅ Mode set to {mode}")
            pause()

        elif choice == "4":
            if not profile:
                print("Create or load a profile first.")
            else:
                profile = risk_quiz(profile)
                save_profile(profile)
            pause()

        elif choice == "5":
            if not profile:
                print("Create or load a profile first.")
            else:
                profile = mini_financial_plan(profile, mode)
                save_profile(profile)
            pause()

        elif choice == "6":
            if not profile:
                print("Create or load a profile first.")
            else:
                profile = portfolio_simulator(profile, mode)
                save_profile(profile)
            pause()

        elif choice == "7":
            if not profile:
                print("Create or load a profile first.")
            else:
                profile = goal_planner(profile, mode)
                save_profile(profile)
            pause()

        elif choice == "8":
            if not profile:
                print("Create or load a profile first.")
            else:
                export_report(profile, mode)
            pause()

        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Pick a valid number (1-9).")
            pause()

if __name__ == "__main__":
    main()



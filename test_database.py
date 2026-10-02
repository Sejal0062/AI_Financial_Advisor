from database.database import FinancialDatabase


database = FinancialDatabase()

print("Database connected successfully.")


# ============================================================
# GET EXISTING TEST USER
# ============================================================

user = database.get_user(1)

if user is None:

    print("Test user was not found.")

else:

    user_id = user[0]

    print("\nUSER")
    print("-" * 40)
    print("ID:", user[0])
    print("Name:", user[1])
    print("Email:", user[2])


    # ========================================================
    # FINANCIAL PROFILE
    # ========================================================

    profile = database.get_financial_profile(user_id)

    print("\nFINANCIAL PROFILE")
    print("-" * 40)

    print(profile)


    # ========================================================
    # FINANCIAL GOALS
    # ========================================================

    goals = database.get_goals(user_id)

    print("\nFINANCIAL GOALS")
    print("-" * 40)

    for goal in goals:

        print(goal)


    # ========================================================
    # TRANSACTIONS
    # ========================================================

    transactions = database.get_transactions(user_id)

    print("\nTRANSACTIONS")
    print("-" * 40)

    for transaction in transactions:

        print(transaction)


    # ========================================================
    # AGENT ACTIVITY
    # ========================================================

    activities = database.get_agent_activity(user_id)

    print("\nAGENT ACTIVITY")
    print("-" * 40)

    for activity in activities:

        print(activity)


print("\n")
print("=" * 60)
print("DATABASE READ TEST COMPLETED")
print("=" * 60)
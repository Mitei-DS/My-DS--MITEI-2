import streamlit as st

# Use st.session_state to store data across user interactions.
# This prevents the 'accounts' list from being reset on every button click.
if 'accounts' not in st.session_state:
    st.session_state.accounts = []
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

def create_account(account_number, password):
    """Creates a new account in the session state."""
    # Check if account number already exists
    for account in st.session_state.accounts:
        if account['account_number'] == account_number:
            st.error("❌ Account number already exists. Please choose another.")
            return False
    
    # Check if the password is a valid 4-digit number
    if not password.isdigit() or len(password) != 5:
        st.error("❌ Invalid password. Must be a 5-digit number.")
        return False
        
    # Add new account as a dictionary to the list
    new_account = {
        'account_number': account_number,
        'password': password,
        'balance': 0
    }
    st.session_state.accounts.append(new_account)
    st.success("✅ Account created successfully! You can now log in.")
    return True

def login(account_number, password):
    """Authenticates the user and stores them in session state."""
    for account in st.session_state.accounts:
        if account['account_number'] == account_number:
            if account['password'] == password:
                st.session_state.logged_in_user = account
                st.success("✅ Login successful!")
                return True
            else:
                st.error("❌ Incorrect password.")
                return False
    st.error("❌ Account not found.")
    return False

def deposit(account_number, amount):
    """Adds funds to the user's account in session state."""
    if amount > 0:
        st.session_state.logged_in_user['balance'] += amount
        st.success(f"✅ Successfully deposited ${amount}. New balance: ${st.session_state.logged_in_user['balance']}")
    else:
        st.error("❌ Deposit amount must be positive.")

def withdraw(account_number, amount):
    """Removes funds from the user's account."""
    if amount > st.session_state.logged_in_user['balance']:
        st.error("❌ Insufficient funds.")
    elif amount <= 0:
        st.error("❌ Withdrawal amount must be positive.")
    else:
        st.session_state.logged_in_user['balance'] -= amount
        st.success(f"✅ Successfully withdrew ${amount}. New balance: ${st.session_state.logged_in_user['balance']}")

def send_money(from_account, to_account_number, amount):
    """Sends money from the logged-in user to another account."""
    if amount > from_account['balance']:
        st.error("❌ Insufficient funds to send.")
        return False
    if amount <= 0:
        st.error("❌ Amount to send must be positive.")
        return False

    for account in st.session_state.accounts:
        if account['account_number'] == to_account_number:
            from_account['balance'] -= amount
            account['balance'] += amount
            st.success(f"✅ Successfully sent ${amount} to account {to_account_number}.")
            st.session_state.logged_in_user = from_account # Update the sender's balance
            return True
            
    st.error("❌ Recipient account not found.")
    return False

# --- App Layout and Logic ---

st.title("🏦 Mitei Bank App")

# Main Page Layout
if st.session_state.logged_in_user is None:
    # Login and Create Account Page
    st.subheader("Login or Create an Account")
    
    with st.form("login_form"):
        st.write("Login")
        login_account_number = st.text_input("Account Number")
        login_password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        if login_button:
            login(login_account_number, login_password)

    with st.form("create_account_form"):
        st.write("Create Account")
        create_account_number = st.text_input("New Account Number")
        create_password = st.text_input("New Password (5 digits)", type="password")
        create_button = st.form_submit_button("Create Account")
        if create_button:
            create_account(create_account_number, create_password)

else:
    # Logged-in User Page
    st.subheader(f"Welcome, Account #{st.session_state.logged_in_user['account_number']}!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="Current Balance", value=f"${st.session_state.logged_in_user['balance']:,}")
        
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in_user = None
            st.success("👋 Logged out successfully.")
            st.rerun()

    st.markdown("---")
    
    # Operations
    st.subheader("Account Operations")
    
    option = st.selectbox(
        "Select an operation:",
        ("Deposit", "Withdraw", "Send Money", "Check Balance")
    )

    if option == "Check Balance":
        st.write("") # Add a small spacer
        st.info(f"Your current balance is: **${st.session_state.logged_in_user['balance']}**")
    
    elif option == "Deposit":
        with st.form("deposit_form"):
            deposit_amount = st.number_input("Enter amount to deposit:", min_value=0.100, format="%f")
            deposit_button = st.form_submit_button("Deposit")
            if deposit_button:
                deposit(st.session_state.logged_in_user['account_number'], deposit_amount)
    
    elif option == "Withdraw":
        with st.form("withdraw_form"):
            withdraw_amount = st.number_input("Enter amount to withdraw:", min_value=0.100, format="%f")
            withdraw_button = st.form_submit_button("Withdraw")
            if withdraw_button:
                withdraw(st.session_state.logged_in_user['account_number'], withdraw_amount)
    
    elif option == "Send Money":
        with st.form("send_form"):
            recipient_account = st.text_input("Enter recipient's account number:")
            send_amount = st.number_input("Enter amount to send:", min_value=0.0, format="%f")
            send_button = st.form_submit_button("Send")
            if send_button:
                send_money(st.session_state.logged_in_user, recipient_account, send_amount)

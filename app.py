import streamlit as st
import psycopg2
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Client Query Management",
    page_icon="🌐",
    layout="wide",
)

# =========================================================
# GLOBAL STYLING (Fonts, Colors, Layout)
# =========================================================
st.markdown(
    """
    <style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-grad-1: #050817;
        --bg-grad-2: #081529;
        --accent-1: #00D4FF;
        --accent-2: #FF6EC7;
        --accent-soft: rgba(0,212,255,0.13);
        --muted: #9AA7BF;
        --card-bg: rgba(255, 255, 255, 0.03);
        --card-border: rgba(255, 255, 255, 0.08);
        --danger: #ff4b6a;
        --success: #3ddc84;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #182848 0, #050817 45%);
    }

    /* Main content container */
    .main .block-container {
        padding: 2.2rem 2.4rem 3rem 2.4rem;
        border-radius: 18px;
        background: linear-gradient(
            145deg,
            rgba(9, 11, 25, 0.96),
            rgba(5, 10, 35, 0.99)
        );
        box-shadow: 0 18px 45px rgba(0,0,0,0.8);
        border: 1px solid rgba(255, 255, 255, 0.03);
    }

    /* Header */
    .cq-header {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 0.25rem;
    }

    .cq-logo {
        width: 64px;
        height: 64px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: conic-gradient(from 200deg, var(--accent-1), var(--accent-2), #7f5af0, var(--accent-1));
        color: #020617;
        font-weight: 800;
        font-size: 26px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.85);
    }

    .cq-title-main {
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        color: #E5F4FF;
        margin: 0;
    }

    .cq-subtitle {
        font-size: 0.95rem;
        color: var(--muted);
        margin-top: 0.2rem;
    }

    /* Section titles */
    h2, h3 {
        color: #E5F4FF !important;
        letter-spacing: 0.02em;
    }

    /* Horizontal rule */
    hr {
        border: 0;
        border-top: 1px solid rgba(148, 163, 184, 0.35);
        margin: 0.75rem 0 1.4rem 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #03091a);
        border-right: 1px solid rgba(148,163,184,0.3);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stRadio > div {
        background: radial-gradient(circle at top left, rgba(15,23,42,0.9), rgba(15,23,42,0.9));
        border-radius: 12px !important;
        border: 1px solid rgba(148,163,184,0.55) !important;
        color: #E5F4FF !important;
        box-shadow: inset 0 0 0 1px rgba(15,23,42,0.75);
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-1) !important;
        box-shadow: 0 0 0 1px var(--accent-1);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
        color: #020617;
        font-weight: 600;
        border-radius: 999px;
        border: none;
        padding: 0.45rem 1.4rem;
        box-shadow: 0 12px 20px rgba(15,23,42,0.8);
        letter-spacing: 0.02em;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 26px rgba(15,23,42,1);
    }

    /* KPI Cards */
    .kpi-card {
        background: radial-gradient(circle at top left, rgba(15, 23, 42, 0.95), rgba(2,6,23,0.98));
        border-radius: 16px;
        padding: 0.8rem 1rem;
        border: 1px solid rgba(148,163,184,0.5);
        box-shadow: 0 8px 22px rgba(0,0,0,0.8);
    }

    .kpi-label {
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .kpi-value {
        color: #E5F4FF;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 0.1rem;
    }

    /* Dataframes */
    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148,163,184,0.35);
    }

    /* Info pills */
    .pill {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148,163,184,0.5);
        font-size: 0.78rem;
        color: var(--muted);
        gap: 0.35rem;
    }

    .pill-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: var(--accent-1);
    }

    .pill-dot.green { background: var(--success); }
    .pill-dot.red { background: var(--danger); }

    /* Tip card */
    .tip-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid var(--card-border);
    }

    .tip-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #E5F4FF;
        margin-bottom: 0.35rem;
    }

    .tip-body {
        font-size: 0.82rem;
        color: var(--muted);
        line-height: 1.4;
    }

    @media (max-width: 768px) {
        .cq-header {
            flex-direction: row;
            align-items: center;
        }
        .cq-title-main {
            font-size: 1.55rem;
        }
        .main .block-container {
            padding: 1.3rem 1.1rem 2rem 1.1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# DATABASE CONNECTION
# =========================================================
def init_connection():
    return psycopg2.connect(
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
    )

# =========================================================
# AUTH / HASHING
# =========================================================
def make_hashes(password: str) -> str:
    return hashlib.sha256(str(password).encode()).hexdigest()


def check_hashes(password: str, hashed_text: str) -> bool:
    return make_hashes(password) == hashed_text


def login_user(username: str, password: str, role: str) -> bool:
    try:
        conn = init_connection()
        with conn:
            with conn.cursor() as c:
                c.execute(
                    "SELECT username, hashed_password, role FROM users WHERE username=%s AND role=%s",
                    (username, role),
                )
                data = c.fetchone()
        if data and check_hashes(password, data[1]):
            return True
    except Exception as e:
        st.error(f"Database Error (login): {e}")
    return False


def add_user(username: str, password: str, role: str) -> bool:
    try:
        conn = init_connection()
        hashed_pswd = make_hashes(password)
        with conn:
            with conn.cursor() as c:
                c.execute(
                    "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
                    (username, hashed_pswd, role),
                )
        return True
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

# =========================================================
# QUERY HELPERS
# =========================================================
def create_query(email: str, mobile: str, heading: str, desc: str):
    try:
        conn = init_connection()
        now = datetime.now()
        with conn:
            with conn.cursor() as c:
                c.execute(
                    """
                    INSERT INTO queries (mail_id, mobile_number, query_heading, query_description, status, query_created_time)
                    VALUES (%s, %s, %s, %s, 'Open', %s)
                    RETURNING query_id
                    """,
                    (email, mobile, heading, desc, now),
                )
                query_id = c.fetchone()[0]
        return query_id
    except Exception as e:
        st.error(f"Error creating query: {e}")
        return None


def close_query(query_id: int) -> bool:
    try:
        conn = init_connection()
        now = datetime.now()
        with conn:
            with conn.cursor() as c:
                c.execute(
                    "UPDATE queries SET status='Closed', query_closed_time=%s WHERE query_id=%s",
                    (now, query_id),
                )
        return True
    except Exception as e:
        st.error(f"Error closing query: {e}")
        return False

# =========================================================
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# =========================================================
# MAIN APP
# =========================================================
def main():
    # ---------- Header ----------
    col_logo, col_text = st.columns([0.16, 1.8])
    with col_logo:
        st.markdown('<div class="cq-logo">CQ</div>', unsafe_allow_html=True)
    with col_text:
        st.markdown(
            """
            <div class="cq-header">
                <div>
                    <div class="cq-title-main">Client Query Management</div>
                    <div class="cq-subtitle">
                        Centralized hub to raise, track, and resolve client issues with clarity and speed.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------- SIDEBAR AUTH ----------
    if st.session_state["logged_in"]:
        st.sidebar.markdown(f"### 👤 {st.session_state['username']}")
        st.sidebar.caption(f"Role: {st.session_state['role']}")
        st.sidebar.markdown(
            '<div class="pill"><span class="pill-dot green"></span>Session active</div>',
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["role"] = None
            st.session_state["username"] = None
            st.rerun()
    else:
        st.sidebar.markdown("## 🔐 Account")
        auth_choice = st.sidebar.radio(" ", ["Login", "Register"], label_visibility="collapsed")

        if auth_choice == "Register":
            st.sidebar.subheader("Create a new account")
            new_user = st.sidebar.text_input("Username")
            new_password = st.sidebar.text_input("Password", type="password")
            role_choice = st.sidebar.radio(
                "Register as",
                ["Client", "Support", "Admin"],
                horizontal=False,
            )
            if st.sidebar.button("Sign Up"):
                if not new_user or not new_password:
                    st.sidebar.warning("Please fill all fields.")
                else:
                    ok = add_user(new_user, new_password, role_choice)
                    if ok:
                        st.sidebar.success("Account created. Please login.")
        else:
            st.sidebar.subheader("Login")
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            role_choice = st.sidebar.radio(
                "Login as",
                ["Client", "Support", "Admin"],
                horizontal=False,
            )
            if st.sidebar.button("Login"):
                if login_user(username, password, role_choice):
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = role_choice
                    st.session_state["username"] = username
                    st.sidebar.success("Login successful.")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid username, password, or role.")

    # ---------- CONTENT BASED ON LOGIN ----------
    if not st.session_state["logged_in"]:
        # Logged-out landing content
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("### Welcome to your support cockpit")
            st.write(
                """
                - 🎯 **Clients** can raise tickets and track their status in one place.  
                - 🛠️ **Support & Admin** get a live dashboard to manage, close, and analyze queries.  

                Use the panel on the left to **register** or **login** and start managing queries.
                """
            )
        with col_right:
            st.markdown(
                """
                <div class="tip-card">
                    <div class="tip-title">Getting started</div>
                    <div class="tip-body">
                        • Create a <b>Client</b> account if you only raise tickets. <br/>
                        • Create a <b>Support</b> or <b>Admin</b> account to manage and close tickets. <br/>
                        • All changes are reflected instantly in the shared dashboard.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    # ---------- LOGGED IN: DASHBOARDS ----------
    # open one connection for duration of dashboard usage
    try:
        conn = init_connection()
    except Exception as e:
        st.error(f"Unable to connect to database: {e}")
        return

    # ========== CLIENT DASHBOARD ==========
    if st.session_state["role"] == "Client":
        st.markdown("## 📨 Raise a New Query")

        form_col, tip_col = st.columns([2.1, 1])
        with form_col:
            with st.form("query_form"):
                email = st.text_input("Email ID")
                mobile = st.text_input("Mobile Number")
                heading = st.text_input("Query Heading")
                desc = st.text_area("Describe your issue in detail", height=160)

                submit = st.form_submit_button("Submit Ticket")

                if submit:
                    if not (email and mobile and heading and desc):
                        st.warning("Please fill all fields before submitting.")
                    else:
                        qid = create_query(email, mobile, heading, desc)
                        if qid:
                            st.success(f"Your ticket has been created. Ticket ID: #{qid}")
                            st.balloons()

        with tip_col:
            st.markdown(
                """
                <div class="tip-card">
                    <div class="tip-title">Tips for faster resolution</div>
                    <div class="tip-body">
                        • Use a clear, short heading (e.g., <i>Login issue - OTP not received</i>). <br/>
                        • Mention your browser / device if it's a UI problem. <br/>
                        • Add any error messages exactly as you see them.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown("### 🕒 Recent Tickets")
        try:
            df = pd.read_sql(
                "SELECT * FROM queries ORDER BY query_id DESC LIMIT 10",
                conn,
            )
            if df.empty:
                st.info("No tickets found yet. Create your first ticket above.")
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading recent tickets: {e}")

    # ========== SUPPORT / ADMIN DASHBOARD ==========
    else:
        st.markdown("## 📊 Support Dashboard")

        try:
            df = pd.read_sql("SELECT * FROM queries", conn)
        except Exception as e:
            st.error(f"Error loading queries: {e}")
            conn.close()
            return

        # Handle no data
        if df.empty:
            st.info("No queries found in the system yet.")
            conn.close()
            return

        # KPI row
        total_queries = len(df)
        open_queries = len(df[df["status"] == "Open"])
        closed_queries = len(df[df["status"] == "Closed"])

        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Total Queries</div>
                    <div class="kpi-value">{total_queries}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Open / Pending</div>
                    <div class="kpi-value">{open_queries}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Closed / Resolved</div>
                    <div class="kpi-value">{closed_queries}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        tab_manage, tab_analytics = st.tabs(["🗂️ Manage Queries", "📈 Analytics"])

        # ----- Manage Tab -----
        with tab_manage:
            st.subheader("Ticket List & Actions")
            filter_col, _ = st.columns([1, 3])
            with filter_col:
                status_filter = st.selectbox("Filter by status", ["All", "Open", "Closed"])
            if status_filter == "All":
                view_df = df
            else:
                view_df = df[df["status"] == status_filter]

            st.dataframe(view_df, use_container_width=True)

            st.markdown("#### 🛠️ Close a Ticket")
            action_col1, action_col2 = st.columns([2, 1])
            with action_col1:
                q_id = st.number_input("Enter Query ID", min_value=1, step=1)
            with action_col2:
                if st.button("Mark as Closed"):
                    if close_query(int(q_id)):
                        st.success(f"Ticket #{int(q_id)} marked as closed.")
                        st.rerun()

        # ----- Analytics Tab -----
        with tab_analytics:
            st.subheader("Insights & Trends")

            # Pie chart: status distribution
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            fig_pie = px.pie(
                status_counts,
                values="count",
                names="status",
                title="Query Status Distribution",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # Bar chart: top query headings
            if "query_heading" in df.columns:
                top_headings = df["query_heading"].value_counts().head(7).reset_index()
                top_headings.columns = ["heading", "count"]
                fig_bar = px.bar(
                    top_headings,
                    x="heading",
                    y="count",
                    title="Most Frequent Issue Types",
                    labels={"heading": "Issue Type", "count": "Count"},
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    conn.close()


if __name__ == "__main__":
    main()

import streamlit as st
import psycopg2
import pandas as pd
import hashlib
from datetime import datetime, date, timedelta
import plotly.graph_objects as go

# ================= CONFIG =================
DB_CONFIG = {
    "dbname": "CQMS",
    "user": "postgres",
    "password": "12345678",
    "host": "127.0.0.1",
    "port": "5432"
}

st.set_page_config(
    page_title="Client Query Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= VIBRANT THEME & STYLES =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { min-height: 100vh; background: linear-gradient(135deg, #FFF5F5 0%, #FFF9F0 50%, #FFFEF5 100%); color: #2D1B1B; }
.main .block-container { background: #FFFFFF; padding: 32px 40px; border-radius: 16px; box-shadow: 0 8px 32px rgba(250, 92, 92, 0.08); }
.app-title { display: flex; gap: 16px; align-items: center; padding: 20px 24px; border-radius: 16px; margin-bottom: 24px; background: linear-gradient(135deg, #FA5C5C 0%, #FD8A6B 100%); box-shadow: 0 8px 24px rgba(250, 92, 92, 0.25); }
.logo-circle { width: 56px; height: 56px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: #FA5C5C; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #2D1B1B 0%, #3D2828 100%); padding-top: 24px; border-right: 2px solid #FA5C5C; }
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] .stRadio > label, section[data-testid="stSidebar"] .stTextInput > label, section[data-testid="stSidebar"] .stSelectbox > label { color: #FEC288 !important; font-weight: 600; }
section[data-testid="stSidebar"] input { background: rgba(255, 255, 255, 0.1) !important; border: 1px solid rgba(254, 194, 136, 0.3) !important; color: #FFFFFF !important; }
section[data-testid="stSidebar"] .stButton > button { background: linear-gradient(135deg, #FA5C5C 0%, #FD8A6B 100%); color: white; border: none; font-weight: 600; }
section[data-testid="stSidebar"] hr { border-color: rgba(254, 194, 136, 0.2) !important; }
.card { padding: 20px; border-radius: 12px; background: #FFFFFF; box-shadow: 0 4px 16px rgba(253, 138, 107, 0.08); border-left: 4px solid #FD8A6B; }
.stButton > button, .stDownloadButton > button { background: linear-gradient(135deg, #FA5C5C 0%, #FD8A6B 50%, #FEC288 100%); color: white; border: none; border-radius: 10px; padding: 0.65rem 1.4rem; font-weight: 700; font-size: 15px; box-shadow: 0 4px 12px rgba(250, 92, 92, 0.2); transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; }
.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(250, 92, 92, 0.35); }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { border-radius: 8px !important; padding: 8px 12px !important; border: 2px solid #FEC288 !important; background: #FFFEF9 !important; color: #2D1B1B !important; font-size: 14px !important; transition: all 0.25s ease; }
.stSelectbox { position: relative; z-index: 999; overflow: visible !important; }
.stSelectbox > div, .stSelectbox > div > div { overflow: visible !important; }
.stSelectbox > div > div > div { height: 38px !important; padding: 8px 12px !important; border: 2px solid #FEC288 !important; border-radius: 8px !important; background: #FFFEF9 !important; color: #2D1B1B !important; font-size: 14px !important; }
.stSelectbox [data-baseweb="popover"], .stSelectbox [role="listbox"] { z-index: 9999 !important; }
[data-testid="column"], .row-widget, .element-container { overflow: visible !important; }
.stTextInput > label, .stTextArea > label, .stSelectbox > label { color: #3D2828 !important; font-weight: 600; font-size: 14px; }
.stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(253, 138, 107, 0.1); }
.stDataFrame table thead tr { background: linear-gradient(135deg, #FA5C5C 0%, #FD8A6B 100%); }
.stDataFrame table thead th { color: white !important; font-weight: 700; padding: 14px !important; }
.stDataFrame table tbody tr:nth-child(even) { background-color: #FFF9F5; }
.stDataFrame table tbody tr:hover { background-color: #FFF3ED; }
.stMetric { background: linear-gradient(135deg, #FFF5F5 0%, #FFF9F0 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #FA5C5C; box-shadow: 0 4px 12px rgba(250, 92, 92, 0.08); }
.stMetric [data-testid="stMetricValue"] { color: #FA5C5C !important; font-size: 32px; font-weight: 800; }
.stExpander { border-radius: 12px; border: 2px solid #FEC288; background: #FFFEF9; margin-bottom: 12px; }
.stExpander summary { background: linear-gradient(135deg, #FFF5F5 0%, #FFF9F0 100%); padding: 16px; font-weight: 600; }
.badge { padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 13px; display: inline-block; text-transform: uppercase; }
.badge-open { background: linear-gradient(135deg, #FA5C5C 0%, #FD8A6B 100%); color: white; }
.badge-closed { background: linear-gradient(135deg, #FEC288 0%, #FBEF76 100%); color: #3D2828; }
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def safe_rerun():
    try:
        st.rerun()
    except:
        st.stop()

def db():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

def ensure_schema():
    conn = db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("ALTER TABLE queries ADD COLUMN IF NOT EXISTS support_notes TEXT, ADD COLUMN IF NOT EXISTS closed_by VARCHAR(100), ADD COLUMN IF NOT EXISTS requirement TEXT;")
            conn.commit()
            cur.close()
        except:
            pass
        finally:
            conn.close()

def login_user(u, p, r):
    conn = db()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT hashed_password FROM users WHERE username=%s AND role=%s", (u, r))
        row = cur.fetchone()
        cur.close()
        return row and hash_pw(p) == row[0]
    except:
        return False
    finally:
        conn.close()

def add_user(u, p, r):
    conn = db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO users VALUES(%s,%s,%s) ON CONFLICT(username) DO NOTHING", (u, hash_pw(p), r))
            conn.commit()
            cur.close()
        except:
            pass
        finally:
            conn.close()

def create_query(e, m, h, d, req):
    conn = db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO queries (mail_id,mobile_number,query_heading,query_description,requirement,status,query_created_time) VALUES(%s,%s,%s,%s,%s,'Open',%s)", (e, m, h, d, req, datetime.now()))
            conn.commit()
            cur.close()
        except:
            pass
        finally:
            conn.close()

def close_query(qid, user, note):
    conn = db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE queries SET status='Closed', query_closed_time=%s, support_notes=%s, closed_by=%s WHERE query_id=%s", (datetime.now(), note, user, qid))
            conn.commit()
            cur.close()
        except:
            pass
        finally:
            conn.close()

@st.cache_data(ttl=30)
def all_queries():
    conn = db()
    if not conn:
        return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM queries", conn)
        if not df.empty:
            df = df.drop_duplicates("query_id")
            df["status"] = df["status"].str.title()
            df["query_created_time"] = pd.to_datetime(df["query_created_time"])
            df["query_closed_time"] = pd.to_datetime(df["query_closed_time"], errors="coerce")
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# ================= SESSION =================
if "logged" not in st.session_state:
    st.session_state.logged = False
    st.session_state.user = None
    st.session_state.role = None

# ================= HEADER =================
st.markdown('<div class="app-title"><div class="logo-circle">CQMS</div><div><div style="font-size:24px; font-weight:800; color:#FFFFFF;">Client Query Management System</div><div style="font-size:14px; color:rgba(255,255,255,0.95); margin-top:4px; font-weight:500;">Enterprise-Grade Ticket Management Platform</div></div></div>', unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### Account Management")
    if not st.session_state.logged:
        mode = st.radio("Action", ["Login", "Register"], label_visibility="collapsed")
        u = st.text_input("Email", key="auth_email")
        p = st.text_input("Password", type="password", key="auth_password")
        r = st.radio("Role", ["Client", "Support", "Admin"], key="auth_role")
        if st.button(mode, use_container_width=True):
            if mode == "Login":
                if login_user(u, p, r):
                    st.session_state.logged, st.session_state.user, st.session_state.role = True, u, r
                    safe_rerun()
                else:
                    st.error("Invalid credentials")
            else:
                add_user(u, p, r)
                st.success("Account created")
    else:
        st.markdown(f"**Role:** {st.session_state.role}")
        st.markdown(f"**User:** {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged = False
            safe_rerun()

# ================= PUBLIC =================
if not st.session_state.logged:
    st.markdown('<div class="card"><h2 style="color:#FA5C5C;">Welcome to CQMS</h2><p>Secure enterprise query management system for professional ticket tracking.</p></div>', unsafe_allow_html=True)
    st.stop()

# ================= MAIN =================
ensure_schema()
df = all_queries()
role = st.session_state.role

with st.sidebar:
    st.markdown("---")
    st.markdown("### Navigation")
    if role == "Client":
        page = st.radio("Menu", ["Create Ticket", "My Tickets"], label_visibility="collapsed")
    elif role == "Support":
        page = st.radio("Menu", ["Dashboard", "Support"], label_visibility="collapsed")
    else:
        page = st.radio("Menu", ["Dashboard", "Admin"], label_visibility="collapsed")

# ================= KPIs =================
if role in ("Support", "Admin"):
    tc = int(df["query_id"].nunique()) if not df.empty else 0
    oc = int(df[df.status == "Open"]["query_id"].nunique()) if not df.empty else 0
    cc = int(df[df.status == "Closed"]["query_id"].nunique()) if not df.empty else 0
    st.markdown("### Key Performance Indicators")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", tc)
    c2.metric("Open", oc)
    c3.metric("Closed", cc)
    st.markdown("---")

# ================= DASHBOARD =================
if page == "Dashboard" and role in ("Support", "Admin"):
    st.markdown("### Analytics Dashboard")
    if df.empty:
        st.info("No query data available.")
    else:
        df["month"] = df["query_created_time"].dt.to_period("M").astype(str)
        m = df.groupby("month")["query_id"].nunique().reset_index(name="count")
        fig1 = go.Figure(data=[go.Bar(x=m["month"], y=m["count"], marker_color="#FA5C5C")])
        fig1.update_layout(title={'text': "Monthly Query Volume", 'font': {'color': '#000000', 'size': 18}}, 
                          xaxis={'title': {'text': 'Month', 'font': {'color': '#000000', 'size': 14}}, 'tickfont': {'color': '#000000', 'size': 12}}, 
                          yaxis={'title': {'text': 'Count', 'font': {'color': '#000000', 'size': 14}}, 'tickfont': {'color': '#000000', 'size': 12}}, 
                          plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        
        c = df.groupby(["month", "status"])["query_id"].nunique().reset_index(name="count")
        fig2 = go.Figure()
        for status in c["status"].unique():
            d = c[c["status"] == status]
            col = "#FA5C5C" if status == "Open" else "#FEC288"
            fig2.add_trace(go.Bar(x=d["month"], y=d["count"], name=status, marker_color=col))
        fig2.update_layout(title={'text': "Monthly Queries by Status", 'font': {'color': '#000000', 'size': 18}}, 
                          xaxis={'title': {'text': 'Month', 'font': {'color': '#000000', 'size': 14}}, 'tickfont': {'color': '#000000', 'size': 12}}, 
                          yaxis={'title': {'text': 'Count', 'font': {'color': '#000000', 'size': 14}}, 'tickfont': {'color': '#000000', 'size': 12}}, 
                          barmode='group', plot_bgcolor='rgba(255,255,255,0.9)', paper_bgcolor='rgba(0,0,0,0)', 
                          legend={'font': {'color': '#000000'}})
        st.plotly_chart(fig2, use_container_width=True)

# ================= CLIENT =================
if role == "Client" and page == "Create Ticket":
    st.markdown("### Submit New Ticket")
    with st.form("new"):
        h = st.text_input("Heading *", key="th")
        d = st.text_area("Description *", height=150, key="td")
        r = st.text_input("Requirements", key="tr")
        m = st.text_input("Contact", key="tm")
        if st.form_submit_button("Submit", use_container_width=True):
            if not h or not d:
                st.error("Heading and Description required")
            else:
                create_query(st.session_state.user, m, h, d, r)
                st.success("Ticket submitted!")
                safe_rerun()

if role == "Client" and page == "My Tickets":
    st.markdown("### My Tickets")
    my = df[df.mail_id == st.session_state.user]
    if my.empty:
        st.info("No tickets yet")
    else:
        for _, q in my.sort_values("query_created_time", ascending=False).iterrows():
            s = q.status or "Open"
            b = f'<span class="badge badge-{"open" if s.lower()=="open" else "closed"}">{s}</span>'
            with st.expander(f"Ticket #{q.query_id} - {q.query_heading}"):
                st.markdown(b, unsafe_allow_html=True)
                st.markdown(f"**Description:** {q.query_description}")
                st.markdown(f"**Created:** {q.query_created_time.strftime('%B %d, %Y at %I:%M %p')}")
                if s.lower() == "closed" and hasattr(q, "support_notes") and q.support_notes:
                    st.success(q.support_notes)

# ================= SUPPORT =================
if role == "Support" and page == "Support":
    st.markdown("### Support Management")
    st.markdown("#### Filter")
    cm, cy = st.columns(2)
    with cm:
        fm = st.selectbox("Month", list(range(1, 13)), index=datetime.now().month-1, format_func=lambda x: datetime(2000, x, 1).strftime('%B'), key="sm")
    with cy:
        fy = st.selectbox("Year", list(range(datetime.now().year-5, datetime.now().year+1)), index=5, key="sy")
    sd = datetime(fy, fm, 1)
    ed = datetime(fy, fm+1, 1) - timedelta(days=1) if fm < 12 else datetime(fy+1, 1, 1) - timedelta(days=1)
    sdf = df[(df.query_created_time >= sd) & (df.query_created_time <= ed) & (df.status == "Open")]
    c1, c2 = st.columns(2)
    c1.metric("Open (Period)", sdf["query_id"].nunique() if not sdf.empty else 0)
    c2.metric("Total Open", df[df.status == "Open"]["query_id"].nunique() if not df.empty else 0)
    if sdf.empty:
        st.info("No open tickets")
    else:
        st.dataframe(sdf[["query_id", "mail_id", "query_heading", "query_created_time"]], use_container_width=True)
        st.markdown("#### Close Ticket")
        qid = st.selectbox("Select", sdf.query_id, format_func=lambda x: f"Ticket #{x}", key="sq")
        note = st.text_area("Notes *", height=120, key="sn")
        if st.button("Close", key="cb"):
            if note and len(note.strip()) >= 10:
                close_query(qid, st.session_state.user, note.strip())
                st.success(f"Ticket #{qid} closed")
                safe_rerun()
            else:
                st.warning("Provide notes (min 10 chars)")

# ================= ADMIN =================
if role == "Admin" and page == "Admin":
    st.markdown("### Admin Panel")
    st.markdown("#### Filter")
    am, ay = st.columns(2)
    with am:
        fm = st.selectbox("Month", list(range(1, 13)), index=datetime.now().month-1, format_func=lambda x: datetime(2000, x, 1).strftime('%B'), key="am")
    with ay:
        fy = st.selectbox("Year", list(range(datetime.now().year-5, datetime.now().year+1)), index=5, key="ay")
    sd = datetime(fy, fm, 1)
    ed = datetime(fy, fm+1, 1) - timedelta(days=1) if fm < 12 else datetime(fy+1, 1, 1) - timedelta(days=1)
    adf = df[(df.query_created_time >= sd) & (df.query_created_time <= ed)]
    st.markdown(f"#### All Queries ({len(adf)} records)")
    st.dataframe(adf, use_container_width=True, height=400)
    st.download_button("📥 Export CSV", adf.to_csv(index=False), f"cqms_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
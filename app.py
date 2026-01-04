# app.py
import streamlit as st
import psycopg2
import pandas as pd
import hashlib
from datetime import datetime, date, timedelta
import plotly.express as px

# ================= CONFIG =================
DB_CONFIG = {
    "dbname": "query_system",
    "user": "postgres",
    "password": "lord818720",
    "host": "localhost",
    "port": "5432"
}

st.set_page_config("Client Query Management", "🌐", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
* { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at top left,#0b1221,#02030a); }
.main .block-container {
  padding:2rem; border-radius:14px;
  background:linear-gradient(145deg,rgba(8,10,20,.85),rgba(3,6,20,.95));
}
</style>
""", unsafe_allow_html=True)

# ================= UTILS =================
def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        st.session_state["_reload"] = not st.session_state.get("_reload", False)
        st.stop()

def db():
    return psycopg2.connect(**DB_CONFIG)

def hash_pw(p): 
    return hashlib.sha256(p.encode()).hexdigest()

# ================= SCHEMA =================
def ensure_schema():
    conn=db(); cur=conn.cursor()
    cur.execute("""
        ALTER TABLE queries
        ADD COLUMN IF NOT EXISTS support_notes TEXT,
        ADD COLUMN IF NOT EXISTS closed_by VARCHAR(100),
        ADD COLUMN IF NOT EXISTS requirement TEXT;
    """)
    conn.commit(); conn.close()

# ================= AUTH =================
def login_user(u,p,r):
    conn=db(); cur=conn.cursor()
    cur.execute("SELECT hashed_password FROM users WHERE username=%s AND role=%s",(u,r))
    row=cur.fetchone(); conn.close()
    return row and hash_pw(p)==row[0]

def add_user(u,p,r):
    conn=db(); cur=conn.cursor()
    cur.execute("""
      INSERT INTO users VALUES(%s,%s,%s)
      ON CONFLICT(username) DO NOTHING
    """,(u,hash_pw(p),r))
    conn.commit(); conn.close()

# ================= QUERIES =================
def create_query(e,m,h,d,req):
    conn=db(); cur=conn.cursor()
    cur.execute("""
      INSERT INTO queries
      (mail_id,mobile_number,query_heading,query_description,requirement,status,query_created_time)
      VALUES(%s,%s,%s,%s,%s,'Open',%s)
    """,(e,m,h,d,req,datetime.now()))
    conn.commit(); conn.close()

def close_query(qid,user,note):
    conn=db(); cur=conn.cursor()
    cur.execute("""
      UPDATE queries SET
      status='Closed',
      query_closed_time=%s,
      support_notes=%s,
      closed_by=%s
      WHERE query_id=%s
    """,(datetime.now(),note,user,qid))
    conn.commit(); conn.close()

@st.cache_data(ttl=30)
def all_queries():
    conn=db()
    df=pd.read_sql("SELECT * FROM queries",conn)
    conn.close()
    if df.empty: 
        return df
    df=df.drop_duplicates("query_id")
    df["status"]=df["status"].str.title()
    df["query_created_time"]=pd.to_datetime(df["query_created_time"])
    df["query_closed_time"]=pd.to_datetime(df["query_closed_time"],errors="coerce")
    return df

# ================= SESSION =================
if "logged" not in st.session_state:
    st.session_state.logged=False
    st.session_state.user=None
    st.session_state.role=None

# ================= HEADER =================
st.markdown("""
<h2 style="color:#E5F4FF">Client Query Management System</h2>
<p style="color:#9AA7BF">Secure role-based ticket platform</p><hr>
""", unsafe_allow_html=True)

# ================= SIDEBAR (AUTH ONLY) =================
with st.sidebar:
    st.subheader("🔐 Account")

    if not st.session_state.logged:
        mode=st.radio("",["Login","Register"])
        u=st.text_input("Email")
        p=st.text_input("Password",type="password")
        r=st.radio("Role",["Client","Support","Admin"])
        if st.button(mode):
            if mode=="Login":
                if login_user(u,p,r):
                    st.session_state.logged=True
                    st.session_state.user=u
                    st.session_state.role=r
                    safe_rerun()
                else:
                    st.error("Invalid credentials")
            else:
                add_user(u,p,r)
                st.success("Account created")
    else:
        st.success(f"{st.session_state.role} : {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged=False
            safe_rerun()

# ================= PUBLIC BLOCK =================
if not st.session_state.logged:
    st.markdown("""
    ### 👋 Welcome

    This is a **secure query management system**.

    🔐 Please log in to:
    - Create and track queries
    - Access support dashboards
    - View analytics (authorized roles only)

    **No data is visible publicly.**
    """)
    st.stop()

# ================= AFTER LOGIN =================
ensure_schema()
df=all_queries()
role=st.session_state.role

# ================= NAVIGATION (ROLE BASED) =================
with st.sidebar:
    st.markdown("---")
    if role=="Client":
        page=st.radio("Menu",["Create Ticket","My Tickets"])
    elif role=="Support":
        page=st.radio("Menu",["Dashboard","Support"])
    else:  # Admin
        page=st.radio("Menu",["Dashboard","Admin"])

# ================= KPIs (ONLY SUPPORT & ADMIN) =================
if role in ("Support","Admin"):
    c1,c2,c3=st.columns(3)
    c1.metric("Total",df["query_id"].nunique())
    c2.metric("Open",df[df.status=="Open"]["query_id"].nunique())
    c3.metric("Closed",df[df.status=="Closed"]["query_id"].nunique())

# ================= DASHBOARD =================
if page=="Dashboard" and role in ("Support","Admin"):
    df["month"]=df["query_created_time"].dt.to_period("M").astype(str)
    monthly=df.groupby("month")["query_id"].nunique().reset_index(name="count")
    st.plotly_chart(px.bar(monthly,x="month",y="count",title="Monthly Queries"),use_container_width=True)

    clustered=df.groupby(["month","status"])["query_id"].nunique().reset_index(name="count")
    st.plotly_chart(
        px.bar(clustered,x="month",y="count",color="status",
               barmode="group",title="Monthly Queries by Status"),
        use_container_width=True
    )

# ================= CLIENT =================
if role=="Client" and page=="Create Ticket":
    with st.form("new"):
        h=st.text_input("Heading")
        d=st.text_area("Description")
        r=st.text_input("Requirement")
        m=st.text_input("Mobile")
        if st.form_submit_button("Submit"):
            create_query(st.session_state.user,m,h,d,r)
            st.success("Ticket submitted")
            safe_rerun()

if role=="Client" and page=="My Tickets":
    my=df[df.mail_id==st.session_state.user]
    for _,q in my.iterrows():
        with st.expander(f"#{q.query_id} {q.query_heading} [{q.status}]"):
            st.write(q.query_description)
            st.write("Requirement:",q.requirement)
            if q.support_notes:
                st.info(q.support_notes)

# ================= SUPPORT =================
if role=="Support" and page=="Support":
    since=st.date_input("Since",date.today()-timedelta(days=30))
    sdf=df[(df.query_created_time>=pd.to_datetime(since))&(df.status=="Open")]
    st.dataframe(sdf[["query_id","mail_id","query_heading","requirement"]])

    if not sdf.empty:
        qid=st.selectbox("Close Ticket",sdf.query_id)
        note=st.text_area("Support note")
        if st.button("Close"):
            close_query(qid,st.session_state.user,note)
            st.success("Closed")
            safe_rerun()

# ================= ADMIN =================
if role=="Admin" and page=="Admin":
    since=st.date_input("Since",date.today()-timedelta(days=90))
    adf=df[df.query_created_time>=pd.to_datetime(since)]
    st.dataframe(adf)
    st.download_button("Export CSV",adf.to_csv(index=False),"queries.csv")

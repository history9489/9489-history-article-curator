import streamlit as st
import requests
import urllib.parse
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PTES 9489 History Library",
    page_icon="📚",
    layout="wide"
)

# --- CONFIGURATION VARIABLES ---
# GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/export?format=csv"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Kckp2mug8-bUlGroArM5bM9guK2jmt2w9XAfQPKuIl4/export?format=csv"
# Form link where teachers submit new links (Sheet updates automatically)
GOOGLE_FORM_SUBMIT_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" 

# --- SYLLABUS DATA STRUCTURE ---
SYLLABUS_OPTIONS = {
    "Modern Europe (1750–1921)": [
        "France, 1774–1814",
        "Industrial Revolution in Britain",
        "Liberalism and nationalism in Germany",
        "The Russian Revolution"
    ],
    "The Origin & Development of Cold War": [
        "Origins of the Cold War",
        "Historian Interpretation",
        "Dictatorship Rule"
    ],
    "Stalin Russia (1924-1941)": [
        "Stalin's Rise To Power",
        "Dictatorship Rule"
    ],
    "Hitler's Germany (1929-1941)": [
        "Hitler's Rise To Power",
        "Dictatorship Rule"
    ]
}

# --- METADATA ENGINES ---
def fetch_open_access_articles(query):
    url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&rows=5"
    articles = []
    try:
        response = requests.get(url, headers={"User-Agent": "History9489Portal/1.0 (mailto:ptes@education.edu.bn)"})
        if response.status_code == 200:
            data = response.json()
            items = data.get("message", {}).get("items", [])
            for item in items:
                title = item.get("title", ["Untitled"])[0]
                abstract = item.get("abstract", f"Academic paper published by {item.get('publisher', 'Unknown Publisher')}.")
                abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "")
                link = item.get("URL", "#")
                articles.append({"title": title, "summary": abstract[:250] + "...", "link": link})
    except Exception as e:
        st.error(f"Error fetching articles: {e}")
    return articles

def fetch_internal_worksheets(component, subtopic):
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        df.columns = df.columns.str.strip()
        required_columns = ['Component', 'Topic', 'The URL link', 'Resource Name']
        
        if all(col in df.columns for col in required_columns):
            matched_df = df[
                (df['Component'].str.strip().str.lower() == component.strip().lower()) & 
                (df['Topic'].str.strip().str.lower() == subtopic.strip().lower())
            ]
            return matched_df.to_dict('records')
        return []
    except Exception as e:
        return []

# --- APPLICATION INTERFACE STRUCTURE ---
st.title("📚 PTES 9489 History Library")

# Setup two isolated views using Streamlit Tabs
tab_student, tab_admin = st.tabs(["📖 Student Library Hub", "🔐 Lecturer Admin Portal"])

# ==================== TAB 1: STUDENT VIEW ====================
with tab_student:
    st.write("Select your module category to gather online readings and internal department materials.")
    
    # Sidebar Filtering Controls
    st.sidebar.header("📋 Syllabus Filter")
    selected_component = st.sidebar.selectbox("Select Component Option", list(SYLLABUS_OPTIONS.keys()))
    selected_subtopic = st.sidebar.selectbox("Select Core Subject Topic", SYLLABUS_OPTIONS[selected_component])

    st.subheader("🔍 Refine Search Query")
    search_keyword = st.text_input("Modify keywords to fine-tune your resource matching:", value=selected_subtopic)

    col1, col2 = st.columns(2)
    with col1:
        search_articles = st.button("🚀 Fetch Syllabus Articles", use_container_width=True)
    with col2:
        search_worksheets = st.button("📝 Find Worksheets & Sheets Data", use_container_width=True)

    st.markdown("---")

    if search_articles:
        st.subheader(f"📖 Academic Materials for: *{search_keyword}*")
        with st.spinner("Scanning open archives..."):
            results = fetch_open_access_articles(search_keyword)
            if results:
                for article in results:
                    with st.container():
                        st.markdown(f"### 📄 {article['title']}")
                        st.write(f"**Preview Summary:** {article['summary']}")
                        st.markdown(f"[🔗 Read Full Article]({article['link']})")
                        st.markdown("---")
            else:
                st.warning("No global open-access materials matching this term were located.")

    if search_worksheets:
        st.subheader(f"🧩 Target Worksheets for: *{search_keyword}*")
        
        st.markdown("### 🏫 Department Google Workspace Resources")
        with st.spinner("Accessing department Google Sheet..."):
            internal_results = fetch_internal_worksheets(selected_component, search_keyword)
            
            if internal_results:
                st.success(f"Found {len(internal_results)} custom resource link(s) for this specific topic!")
                # Loops perfectly whether there are 1, 5, or 20 resource records
                for row in internal_results:
                    name = row.get('Resource Name', 'Worksheet Handout')
                    url = row.get('The URL link', '#')
                    desc = row.get('Description', 'No description provided.')
                    st.markdown(f"* 👉 **[{name}]({url})** — *{desc}*")
            else:
                st.info("No customized internal worksheets found for this exact subtopic yet.")
                
        st.markdown("---")
        st.markdown("### 🌐 External Live Web Resources")
        encoded_query = urllib.parse.quote(f"{search_keyword} history 9489 worksheet filetype:pdf OR quiz")
        st.markdown(f"* 👉 [Search Open Source PDF Worksheets via DuckDuckGo](https://duckduckgo.com/?q={encoded_query})")

# ==================== TAB 2: SECURE ADMIN VIEW ====================
with tab_admin:
    st.subheader("🔐 Lecturer Administration Access")
    
    # Password verification framework using Streamlit Secrets
    admin_password_input = st.text_input("Enter Department Authorization Password:", type="password")
    
    # Verifies entry matches your application secret string
    if admin_password_input == st.secrets.get("ADMIN_PASSWORD"):
        st.success("Authorization Verified. Welcome back, Educator.") 
        st.markdown("### 📤 Upload New Worksheet or Article Metadata Link")
        st.write("To add interactive forms, sheets links, or drive files to the library collection, use the secure link utility below.")
        
        st.info("💡 Make sure your Google Drive PDF or Microsoft Form sharing permission is explicitly configured to 'Anyone with link can view' before adding it!")
        
        # Provides clean, embedded gateway out to the form repository
        st.markdown(f"""
        <a href="{GOOGLE_FORM_SUBMIT_URL}" target="_blank">
            <button style="background-color:#28a745; color:white; border:none; padding:12px 24px; border-radius:4px; font-size:16px; cursor:pointer;">
                ➕ Open Content Management Form
            </button>
        </a>
        """, unsafe_allow_html=True)
        
    elif admin_password_input != "":
        st.error("Access Denied. Incorrect administration password provided.")

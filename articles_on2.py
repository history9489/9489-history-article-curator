import streamlit as st
import requests
import urllib.parse
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PTES 9489 History Library",
    page_icon="📚",
    layout="wide"
)

# --- 2. GOOGLE SHEETS CONNECTION CONFIGURATION ---
@st.cache_resource
def init_connection():
    try:
        creds_dict = dict(st.secrets["gspread_creds"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        return None

gc = init_connection()

# --- 3. UNIFIED GLOBAL 11-OPTION TOPICS MATRIX ---
UNIFIED_HISTORY_TOPICS = [
    "Modern Europe (1750–1921), The France (1774–1814)",
    "Modern Europe (1750–1921), The Britain Industrial Revolution",
    "Modern Europe (1750–1921), The Germany Liberalism & Nationalism",
    "Modern Europe (1750–1921), The Russian Revolution",
    "The Origin & Development of Cold War",
    "The Historian Interpretation of Cold War",
    "Stalin's Russia (1924-1941), Rise to power",
    "Stalin's Russia (1924-1941), Dictatorship Rules",
    "Hitler's Germany (1929-1941), Rise to power",
    "Hitler's Germany (1929-1941), Dictatorship Rules",
    "Other Additional Materials"
]

# Behind-the-scenes search optimizer
SEARCH_QUERY_MAP = {
    "Modern Europe (1750–1921), The France (1774–1814)": "France 1774-1814 history",
    "Modern Europe (1750–1921), The Britain Industrial Revolution": "Britain Industrial Revolution history",
    "Modern Europe (1750–1921), The Germany Liberalism & Nationalism": "Germany Liberalism Nationalism history",
    "Modern Europe (1750–1921), The Russian Revolution": "Russian Revolution 1917 history",
    "The Origin & Development of Cold War": "Origins of the Cold War",
    "The Historian Interpretation of Cold War": "Cold War historian interpretations",
    "Stalin's Russia (1924-1941), Rise to power": "Stalin Rise to power Russia",
    "Stalin's Russia (1924-1941), Dictatorship Rules": "Stalin Dictatorship Rule USSR",
    "Hitler's Germany (1929-1941), Rise to power": "Hitler Rise to power Germany",
    "Hitler's Germany (1929-1941), Dictatorship Rules": "Hitler Dictatorship Rule Germany",
    "Other Additional Materials": "Cambridge International history 9489"
}

MATERIAL_TYPES_CRITERIA = [
    "References to selected Topic (pdf)",
    "Assignment Worksheet (Doc/Forms)",
    "Primary Source Material Context",
    "Lecture Slides / Overview Notes",
    "Quiz Form",
    "URL Links to Worksheets",
    "URL to Slides and Video"
]

# --- 4. HELPER FUNCTIONS FOR LIVE APIS & DATABASE EXTRACTION ---
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

def extract_database_resources(selected_topic):
    """
    Fetches records from Google Sheets database and filters them 
    dynamically matching the parsed Component and Topic values.
    """
    if not gc:
        return []
    
    try:
        sheet = gc.open("PTES History 9489 Database").sheet1
        all_records = sheet.get_all_records()
        if not all_records:
            return []
            
        # Parse the unified component/topic string for dynamic comparison
        if ", " in selected_topic:
            comp_part, topic_part = selected_topic.split(", ", 1)
        else:
            comp_part, topic_part = "General / Additional", selected_topic
            
        filtered_resources = []
        for row in all_records:
            # Safely get sheet column parameters
            sheet_comp = str(row.get("Component", "")).strip().lower()
            sheet_topic = str(row.get("Topic", "")).strip().lower()
            
            # If the row details align with selected query, grab it!
            if (comp_part.strip().lower() in sheet_comp and topic_part.strip().lower() in sheet_topic) or \
               (selected_topic.strip().lower() in sheet_comp or selected_topic.strip().lower() in sheet_topic):
                filtered_resources.append({
                    "material_type": row.get("Resource Name", "General Reference"),
                    "url": row.get("The URL Link", "#"),
                    "description": row.get("Description", "No description provided.")
                })
        return filtered_resources
    except Exception as e:
        st.error(f"Database query error: {e}")
        return []

# --- 5. UNIFIED INTERFACE STRUCTURE ---
tab_students, tab_lecturer = st.tabs(["🎓 Student Discovery Hub", "🔒 Lecturer Reference Log Entry"])

# ==========================================
#   TAB 1: STUDENT DISCOVERY HUB (WITH EXTRACTION ENGINE)
# ==========================================
with tab_students:
    st.title("📚 PTES 9489 History Library")
    st.write("Gather open-access historical data and teacher resources matching your Cambridge 9489 syllabus parameters.")

    # Single dropdown parameter
    selected_student_topic = st.selectbox(
        "Select Syllabus Component & Topic Focus:",
        UNIFIED_HISTORY_TOPICS,
        key="student_unified_select"
    )

    search_keyword = SEARCH_QUERY_MAP.get(selected_student_topic, "Cambridge International history 9489")

    # Three-column action button array
    col1, col2, col3 = st.columns(3)
    with col1:
        search_articles = st.button("🚀 Fetch Syllabus Articles", use_container_width=True)
    with col2:
        search_worksheets = st.button("📝 Find Online Worksheets", use_container_width=True)
    with col3:
        extract_local_data = st.button("📂 Pull Local Database Resources", use_container_width=True)

    st.markdown("---")

    # ACTION 1: Run Live Crossref Academic Search
    if search_articles:
        st.subheader(f"📖 Academic Materials for: *{selected_student_topic}*")
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
                st.warning("No open-access summaries matching this precise subtopic were found.")

    # ACTION 2: Run Live Interactive Online Web Lookup
    if search_worksheets:
        st.subheader(f"🧩 Target Worksheets for: *{selected_student_topic}*")
        encoded_query = urllib.parse.quote(f"{search_keyword} history 9489 worksheet filetype:pdf OR quiz")
        ddg_search_url = f"https://duckduckgo.com/?q={encoded_query}"
        quizizz_url = f"https://quizizz.com/admin/search/{urllib.parse.quote(search_keyword)}"
        
        st.info("Click below to access dynamic external worksheet frameworks curated for this topic:")
        st.markdown(f"""
        * 👉 [Search Open Source PDF Worksheets & Handouts via DuckDuckGo]({ddg_search_url})
        * 👉 [Check for Interactive Live Revision Quizzes on Quizizz]({quizizz_url})
        """)

    # ACTION 3: Run Cloud Google Sheets Data Extraction
    if extract_local_data:
        st.subheader(f"📂 Verified Cohort Reference Resources: *{selected_student_topic}*")
        with st.spinner("Accessing school cloud database..."):
            local_resources = extract_database_resources(selected_student_topic)
            if local_resources:
                st.success(f"Successfully retrieved {len(local_resources)} materials linked by your lecturers!")
                st.markdown("<br>", unsafe_allow_html=True)
                for res in local_resources:
                    with st.chat_message("user", avatar="🎓"):
                        st.markdown(f"### 📎 Category: **{res['material_type']}**")
                        st.write(f"**Resource Context & Instructions:** {res['description']}")
                        st.markdown(f"👉 **[Access Document URL Link]({res['url']})**")
            else:
                st.info("No curated local resources are logged in the database for this specific syllabus segment yet.")

# ==========================================
#   TAB 2: LECTURER PORTAL (SECURED & CLEAN MATCHING)
# ==========================================
with tab_lecturer:
    st.title("🔒 Lecturer Administration Portal")
    
    password_input = st.text_input("Enter Access Verification Key Code:", type="password")
    
    if password_input and password_input == st.secrets.get("ADMIN_PASSWORD"):
        st.success("Verification Access Granted.")
        st.markdown("---")
        
        st.header("📥 History Reference Log Entry")
        st.write("Publish reference worksheets, context slides, and quiz links into the cohort library database.")
        
        with st.form("lecturer_unified_form", clear_on_submit=True):
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                unified_topic = st.selectbox(
                    "Select Syllabus Component & Core Subject:",
                    UNIFIED_HISTORY_TOPICS,
                    key="lecturer_combined_topic"
                )
                
                material_criteria = st.selectbox(
                    "Select Material Type or Category:",
                    MATERIAL_TYPES_CRITERIA,
                    key="lecturer_material_criteria"
                )
            
            with col_right:
                resource_description = st.text_area(
                    "Resource Description context Entry:",
                    placeholder="Type descriptive instructions, details or guidelines here...",
                    height=155,
                    key="lecturer_description"
                )
            
            resource_url = st.text_input(
                "Material Document URL Link:",
                placeholder="https://drive.google.com/file/d/... or https://quizizz.com/..."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("⚡ UPLOAD References/URL append into Database", use_container_width=True)
            
            if submit_btn:
                if resource_url and resource_description:
                    if gc:
                        try:
                            # Splits unified topic directly back into separate sheet columns
                            if ", " in unified_topic:
                                comp_part, topic_part = unified_topic.split(", ", 1)
                            else:
                                comp_part, topic_part = "General / Additional", unified_topic
                            
                            row_to_append = [
                                comp_part,           # Column A: Component
                                topic_part,          # Column B: Topic
                                material_criteria,   # Column C: Resource Name
                                resource_url,        # Column D: The URL Link
                                resource_description # Column E: Description
                            ]
                            
                            sheet = gc.open("PTES History 9489 Database").sheet1
                            sheet.append_row(row_to_append)
                            st.success("Successfully logged aligned parameters into your Google Sheet backend columns!")
                        except Exception as e:
                            st.error(f"Failed to append row parameters: {e}")
                    else:
                        st.error("Database connection is offline. Verify your Cloud Secrets keys.")
                else:
                    st.warning("Ensure that both Description and Document URL Link fields are fully filled.")
                    
    elif password_input != "":
        st.error("Access Code Incorrect. Verification Failure.")

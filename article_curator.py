import streamlit as st
import requests
import urllib.parse
import gspread
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
# Shared completely between both Tab 1 and Tab 2 to prevent any mapping confusion
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

MATERIAL_TYPES_CRITERIA = [
    "References to selected Topic (pdf)",
    "Assignment Worksheet (Doc/Forms)",
    "Primary Source Material Context",
    "Lecture Slides / Overview Notes",
    "Quiz Form",
    "URL Links to Worksheets",
    "URL to Slides and Video"
]

# --- 4. HELPER FUNCTIONS FOR LIVE APIS ---
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

# --- 5. UNIFIED INTERFACE STRUCTURE (TABS ONLY, NO SIDEBAR) ---
tab_students, tab_lecturer = st.tabs(["🎓 Student Discovery Hub", "🔒 Lecturer Reference Log Entry"])

# ==========================================
#   TAB 1: STUDENT DISCOVERY HUB (MAIN INTERFACE MERGE)
# ==========================================
with tab_students:
    st.title("📚 PTES 9489 History Library")
    st.write("Gather open-access historical data and resources matching your Cambridge 9489 syllabus parameters.")

    # Main dashboard selection using your explicit 11 options
    selected_student_topic = st.selectbox(
        "Select Syllabus Component & Topic Focus:",
        UNIFIED_HISTORY_TOPICS,
        key="student_unified_select"
    )

    # Automatically extract a clean keyword for the live API query
    if ", " in selected_student_topic:
        api_search_keyword = selected_student_topic.split(", ", 1)[1]
    else:
        api_search_keyword = selected_student_topic

    st.subheader("🔍 Refine Search Query")
    search_keyword = st.text_input(
        "Modify keywords to fine-tune your live API resource matching:", 
        value=api_search_keyword,
        key="student_keyword_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        search_articles = st.button("🚀 Fetch Syllabus Articles", use_container_width=True)
    with col2:
        search_worksheets = st.button("📝 Find Online Worksheets", use_container_width=True)

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
                st.warning("No open-access summaries matching this precise subtopic were found.")

    if search_worksheets:
        st.subheader(f"🧩 Target Worksheets for: *{search_keyword}*")
        encoded_query = urllib.parse.quote(f"{search_keyword} history 9489 worksheet filetype:pdf OR quiz")
        ddg_search_url = f"https://duckduckgo.com/?q={encoded_query}"
        quizizz_url = f"https://quizizz.com/admin/search/{urllib.parse.quote(search_keyword)}"
        
        st.info("Click below to access dynamic external worksheet frameworks curated for this topic:")
        st.markdown(f"""
        * 👉 [Search Open Source PDF Worksheets & Handouts via DuckDuckGo]({ddg_search_url})
        * 👉 [Check for Interactive Live Revision Quizzes on Quizizz]({quizizz_url})
        """)

# ==========================================
#   TAB 2: LECTURER PORTAL (SECURED & CLEAN MATCHING)
# ==========================================
with tab_lecturer:
    st.title("🔒 Lecturer Administration Portal")
    
    # Securely queries your deployment panel secrets directly
    password_input = st.text_input("Enter Access Verification Key Code:", type="password")
    
    if password_input and password_input == st.secrets.get("ADMIN_PASSWORD"):
        st.success("Verification Access Granted.")
        st.markdown("---")
        
        st.header("📥 History Reference Log Entry")
        st.write("Publish reference worksheets, context slides, and quiz links into the cohort library database.")
        
        with st.form("lecturer_unified_form", clear_on_submit=True):
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                # Parameter Bar 1: Uses the identical 11 choices matching Tab 1
                unified_topic = st.selectbox(
                    "Select Syllabus Component & Core Subject:",
                    UNIFIED_HISTORY_TOPICS,
                    key="lecturer_combined_topic"
                )
                
                # Parameter Bar 3: Material criteria dropdown
                material_criteria = st.selectbox(
                    "Select Material Type / Criteria (Resource Name):",
                    MATERIAL_TYPES_CRITERIA,
                    key="lecturer_material_criteria"
                )
            
            with col_right:
                # Parameter Bar 2: Context Description box
                resource_description = st.text_area(
                    "Resource Description context Entry:",
                    placeholder="Type descriptive instructions, details or guidelines here...",
                    height=155,
                    key="lecturer_description"
                )
            
            # Parameter Bar 4: Link target text field
            resource_url = st.text_input(
                "State the material document or URL Link:",
                placeholder="https://drive.google.com/file/d/... or https://quizizz.com/..."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("⚡ UPLOAD References append to Database", use_container_width=True)
            
            if submit_btn:
                if resource_url and resource_description:
                    if gc:
                        try:
                            # DATABASE HEADERS ALIGNMENT LOGIC:
                            # Intelligently splits the single string choice to fit Column A and Column B
                            if ", " in unified_topic:
                                comp_part, topic_part = unified_topic.split(", ", 1)
                            else:
                                comp_part, topic_part = "General / Additional", unified_topic
                            
                            # Maps cleanly across Column A, B, C, D, E of your worksheet database
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

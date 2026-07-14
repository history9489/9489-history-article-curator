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

# --- 3. GLOBAL SYLLABUS DATA STRUCTURE (STUDENT DISCOVERY) ---
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

# --- UNIFIED LECTURER COMBINED PARAMETERS (11 DEFINITE OPTIONS) ---
LECTURER_COMBINED_TOPICS = [
    "Modern Europe, France (1774–1814)",
    "Modern Europe, Britain Industrial Revolution",
    "Modern Europe, Germany Liberalism & Nationalism",
    "Modern Europe, Russian Revolution",
    "Cold War, Origin of Cold War",
    "Cold War, Historian Interpretation",
    "Stalin Russia, Rise to Power",
    "Stalin Russia, Dictatorship Rules",
    "Hitler Germany, Rise to Power",
    "Hitler Germany, Dictatorship Rules",
    "Other Additional Materials"
]

# --- PARAMETER BAR 3: MATERIAL TYPES CRITERIA ---
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

# --- 5. UNIFIED INTERFACE STRUCTURE (TABS) ---
tab_students, tab_lecturer = st.tabs(["🎓 Student Discovery Hub", "🔒 Lecturer Reference Log Entry"])

# ==========================================
#   TAB 1: STUDENT DISCOVERY HUB (ORIGINAL)
# ==========================================
with tab_students:
    st.title("📚 PTES 9489 History Library")
    st.write("Select your topic category to gather online readings and worksheets.")

    # Sidebar Filters remain active for students' easy structured exploration
    st.sidebar.header("📋 Syllabus Filter")
    selected_component = st.sidebar.selectbox(
        "Select Component Option", 
        list(SYLLABUS_OPTIONS.keys()), 
        key="student_component"
    )
    selected_subtopic = st.sidebar.selectbox(
        "Select Core Subject Topic", 
        SYLLABUS_OPTIONS[selected_component], 
        key="student_subtopic"
    )

    st.subheader("🔍 Refine Search Query")
    search_keyword = st.text_input("Modify keywords to fine-tune your resource matching:", value=selected_subtopic)

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
#   TAB 2: LECTURER PORTAL (NEW SIMPLIFIED SINGLE-SELECT LAYOUT)
# ==========================================
with tab_lecturer:
    st.title("🔒 Lecturer Administration Portal")
    password_input = st.text_input("Enter Access Verification Key Code:", type="password")
    
    if password_input == st.secrets.get("ADMIN_PASSWORD", "Brunei9489"):
        st.success("Verification Clearance Verified.")
        st.markdown("---")
        
        st.header("📥 History Reference Log Entry")
        st.write("Publish reference worksheets, context slides, and quiz links into the cohort library database.")
        
        with st.form("lecturer_unified_form", clear_on_submit=True):
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                # Parameter Bar 1: Combined 11 definite choices
                unified_topic = st.selectbox(
                    "Parameter Bar 1: Select Syllabus Component & Core Subject:",
                    LECTURER_COMBINED_TOPICS,
                    key="lecturer_combined_topic"
                )
                
                # Parameter Bar 3: Expanded Material Criteria List
                material_criteria = st.selectbox(
                    "Parameter Bar 3: Select Material Type / Criteria:",
                    MATERIAL_TYPES_CRITERIA,
                    key="lecturer_material_criteria"
                )
            
            with col_right:
                # Parameter Bar 2: Context Description
                resource_description = st.text_area(
                    "Parameter Bar 2: Resource Description context Parameter:",
                    placeholder="Type descriptive instructions, details or guidelines here...",
                    height=155,
                    key="lecturer_description"
                )
            
            # File URL Link Target web row
            resource_url = st.text_input(
                "Parameter Bar 4: Material Document URL Link (Google Drive, Quizizz, Web Link):",
                placeholder="https://drive.google.com/file/d/... or https://quizizz.com/..."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Form submission button
            submit_btn = st.form_submit_button("⚡ Append Reference Parameters to Database", use_container_width=True)
            
            if submit_btn:
                if resource_url and resource_description:
                    if gc:
                        try:
                            # Safely write the merged parameters to your Google Sheet database
                            sheet = gc.open("PTES History 9489 Database").sheet1
                            sheet.append_row([unified_topic, material_criteria, resource_description, resource_url])
                            st.success("Successfully logged unified reference details to the Google Sheet backend!")
                        except Exception as e:
                            st.error(f"Failed to append row parameters: {e}")
                    else:
                        st.error("Database connection is offline. Verify your Cloud Secrets keys.")
                else:
                    st.warning("Ensure that both the Resource Description and target Document URL Link fields are fully filled.")
                    
    elif password_input != "":
        st.error("Access Code Incorrect. Verification Failure.")

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. PAGE SETUP & TITLES ---
st.set_page_config(page_title="PTES History 9489 Hub", page_icon="📚", layout="wide")

st.title("📚 PTES History 9489 Academic Hub")
st.markdown("##### Access core history materials, components, and course assignments cleanly.")
st.markdown("---")

# --- 2. DATABASE / GOOGLE SHEETS CONNECTION ---
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
        st.error(f"Database Connection Error: {str(e)}")
        return None

gc = init_connection()

# --- 3. CORE APPLICATION INTERFACE ---
tab_students, tab_lecturer = st.tabs(["🎓 Student Materials Hub", "🔒 Lecturer Admin Portal"])

# ==========================================
#   TAB 1: STUDENT INTERFACE (HISTORY 9489)
# ==========================================
with tab_students:
    st.header("History 9489 Curriculum Materials")
    st.write("Select one of the core academic components below to view your reading files and worksheets:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📂 Component 1: International Options (Modern International Relations)", expanded=True):
            st.info("Access core text documents, timeline sheets, and historical sources here.")
            
        with st.expander("📂 Component 2: European Options (Modern Europe Documents)", expanded=False):
            st.info("Access European history study guides and essay review tasks.")

    with col2:
        with st.expander("📂 Component 3: American Options (History of the USA)", expanded=False):
            st.info("Access domestic policy modules and civil crisis documents.")
            
        with st.expander("📂 Component 4: Historical Interpretations & Source Investigations", expanded=False):
            st.info("Access source analysis templates and advanced evaluation criteria.")

# ==========================================
#   TAB 2: LECTURER UPLOAD INTERFACE (MATCHING YOUR DESIGN)
# ==========================================
with tab_lecturer:
    st.header("🔒 Lecturer Administration Portal")
    
    # Password protection layer before showing your custom interface
    password_input = st.text_input("Enter Lecturer Access Code:", type="password")
    
    if password_input == st.secrets.get("ADMIN_PASSWORD", "Brunei9489"):
        st.success("Access Granted.")
        st.markdown("---")
        
        # Exact matching header text from your image_3662e0.png layout
        st.subheader("📥 History Reference Log Entry")
        st.write("Incorporate text files, notes, or assignment worksheet variables directly into the cohort backend.")
        
        # Your exact drawn-up interface form layout
        with st.form("lecturer_log_form", clear_on_submit=True):
            col_left, col_right = st.columns([3, 2])
            
            with col_left:
                component_option = st.selectbox(
                    "Select Component Option:",
                    [
                        "Modern Europe (1750–1921)", 
                        "International Options (1870–1945)", 
                        "History of the USA (1840–1980)",
                        "Historical Interpretations"
                    ]
                )
                
                subject_topic = st.selectbox(
                    "Select Core Subject Topic:",
                    [
                        "France, 1774–1814",
                        "The Industrial Revolution, c. 1750–1850",
                        "The League of Nations and International Relations",
                        "The Origins of the Cold War",
                        "Other Specified Topic Syllabus Block"
                    ]
                )
                
                material_type = st.selectbox(
                    "Select Material Type Parameters:",
                    [
                        "References to selected Topic (pdf)",
                        "Assignment Worksheet (Doc/Forms)",
                        "Primary Source Material Context",
                        "Lecture Slides / Overview Notes"
                    ]
                )
            
            with col_right:
                resource_description = st.text_area(
                    "Resource Description Parameter:",
                    placeholder="Type clear descriptive context here...",
                    height=220
                )
            
            # Full width input matching the target web link field
            resource_url = st.text_input(
                "Resource URL Target Web Link:",
                placeholder="https://drive.google.com/file/d/..."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Action button customized to mirror your layout exactly
            submit_btn = st.form_submit_button("⚡ Append Reference Parameters to Database", use_container_width=True)
            
            if submit_btn:
                if resource_url and resource_description:
                    if gc:
                        try:
                            sheet = gc.open("PTES History 9489 Database").sheet1
                            sheet.append_row([component_option, subject_topic, material_type, resource_description, resource_url])
                            st.success("Successfully logged parameter references to the data repository!")
                        except Exception as e:
                            st.error(f"Failed to record information to spreadsheet backend: {e}")
                    else:
                        st.error("Database cloud link status is offline.")
                else:
                    st.warning("Please provide both a clear text context description and a functional target web link URL.")
                    
    elif password_input != "":
        st.error("Incorrect Lecturer Code. Access Denied.")

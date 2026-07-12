import streamlit as st
import requests
import urllib.parse

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PTES 9489 History Case Studies",
    page_icon="📚",
    layout="wide"
)

# --- APPLICATION PURPOSE EXPLANATION ---
# This dashboard aggregates open-access historical data and maps it 
# to specific Cambridge 9489 syllabus components, saving study time.

# --- SYLLABUS DATA STRUCTURE ---
SYLLABUS_OPTIONS = {
    "Modern Europe (1750–1921)": [
        "France, 1774–1814",
        "Industrial Revolution in Britain",
        "Liberalism and nationalism in Germany",
        "The Russian Revolution"
    ],
    "History of the USA (1820–1941)": [
        "Origins of the Civil War",
        "Civil War and Reconstruction",
        "The Gilded Age and Progressive Era",
        "The Great Crash and New Deal"
    ],
    "International History (1870–1945)": [
        "Empire and emergence of world powers",
        "The League of Nations and international relations",
        "China and Japan 1912-45"
    ]
}

# --- HELPER FUNCTIONS FOR LIVE APIS ---
def fetch_open_access_articles(query):
    """
    Fetches open-access research summaries and metadata using the Crossref API.
    Crossref is an open database of academic papers.
    """
    url = f"https://api.crossref.org/works?query={urllib.parse.quote(query)}&rows=5"
    articles = []
    try:
        response = requests.get(url, headers={"User-Agent": "History9489Portal/1.0 (mailto:ptes@education.edu.bn)"})
        if response.status_code == 200:
            data = response.json()
            items = data.get("message", {}).get("items", [])
            for item in items:
                title = item.get("title", ["Untitled"])[0]
                # Fallback to publisher if abstract is missing
                abstract = item.get("abstract", f"Academic paper published by {item.get('publisher', 'Unknown Publisher')}.")
                # Clean simple tags out of abstract if they exist
                abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "")
                link = item.get("URL", "#")
                articles.append({"title": title, "summary": abstract[:250] + "...", "link": link})
    except Exception as e:
        st.error(f"Error fetching articles: {e}")
    return articles

# --- UI LAYOUT ---
st.title("📚 PTES History Modules & Worksheet Hub")
st.write("Select your syllabus option to dynamically gather online readings and matching worksheets.")

# Sidebar Configuration
st.sidebar.header("📋 Syllabus Filter")
selected_component = st.sidebar.selectbox("Select Component Option", list(SYLLABUS_OPTIONS.keys()))
selected_subtopic = st.sidebar.selectbox("Select Core Subject Topic", SYLLABUS_OPTIONS[selected_component])

# Main Free-text search fallback override
st.subheader("🔍 Refine Search Query")
search_keyword = st.text_input("Modify keywords to fine-tune your resource matching:", value=selected_subtopic)

# Action Buttons
col1, col2 = st.columns(2)
with col1:
    search_articles = st.button("🚀 Fetch Syllabus Articles", use_container_width=True)
with col2:
    search_worksheets = st.button("📝 Find Online Worksheets", use_container_width=True)

st.markdown("---")

# --- RESULTS DISPENSATION LOGIC ---
if search_articles:
    st.subheader(f"📖 Academic Articles & Previews for: *{search_keyword}*")
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
            st.warning("No open-access summaries matching this precise subtopic were found. Try modifying the keywords above.")

if search_worksheets:
    st.subheader(f"🧩 Target Worksheets & Practice Packs for: *{search_keyword}*")
    
    # We construct automated search target links using safe redirects to save computing resources
    encoded_query = urllib.parse.quote(f"{search_keyword} history 9489 worksheet filetype:pdf OR quiz")
    ddg_search_url = f"https://duckduckgo.com/?q={encoded_query}"
    quizizz_url = f"https://quizizz.com/admin/search/{urllib.parse.quote(search_keyword)}"
    
    st.info("Click below to access dynamic external worksheet frameworks curated for this topic:")
    
    st.markdown(f"""
    *   👉 [Search Open Source PDF Worksheets & Handouts via DuckDuckGo]({ddg_search_url})
    *   👉 [Check for Interactive Live Revision Quizzes on Quizizz]({quizizz_url})
    """)
    st.caption("Note: Worksheets are fetched externally from educational resource domains.")

import streamlit as st
import requests


# ================================================================
# CONFIGURATION
# Change BASE to your backend URL when deploying
# ================================================================
BASE = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8000")


# ================================================================
# STREAMLIT UI SETUP
# ================================================================
st.set_page_config(
    page_title="ReciPal",
    layout="centered",
    page_icon="🍳"
)

st.markdown("<h1 style='text-align: center;'>🍳 ReciPal</h1>", unsafe_allow_html=True)
st.write("A simple app to extract recipes and get grocery recommendations.")


# ================================================================
# AUTH STATE (stored in session_state)
# ================================================================
if "token" not in st.session_state:
    st.session_state.token = None


def authed_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


# ================================================================
# AUTH FUNCTIONS
# ================================================================
def signup(email, password):
    url = f"{BASE}/auth/signup"
    r = requests.post(url, params={"email": email, "password": password})
    return r


def signin(email, password):
    url = f"{BASE}/auth/signin"
    r = requests.post(url, params={"email": email, "password": password})
    if r.ok:
        st.session_state.token = r.json()["access_token"]
    return r


# ================================================================
# RECIPE EXTRACTION
# ================================================================
def extract_recipe(video_url):
    url = f"{BASE}/recipes/extract"
    r = requests.post(url, params={"url": video_url}, headers=authed_headers())
    return r

# ================================================================
# LIST RECIPES
# ================================================================
def list_recipes():
    url = f"{BASE}/recipes/"
    r = requests.get(url, headers=authed_headers())
    return r


# ================================================================
# PANTRY FUNCTIONS
# ================================================================
def add_pantry_item(name):
    url = f"{BASE}/pantry/add"
    r = requests.post(url, params={"name": name}, headers=authed_headers())
    return r


def list_pantry():
    url = f"{BASE}/pantry/"
    r = requests.get(url, headers=authed_headers())
    return r


# ================================================================
# RECOMMENDER
# ================================================================
def get_recommendations():
    url = f"{BASE}/grocery/recommendations"
    r = requests.get(url, headers=authed_headers())
    return r


# ================================================================
# SIDEBAR — AUTHENTICATION
# ================================================================
st.sidebar.title("Authentication")

with st.sidebar:
    st.subheader("Sign Up")
    email_signup = st.text_input("Email (signup)", key="signup_email")
    password_signup = st.text_input("Password (signup)", type="password", key="signup_pw")
    if st.button("Create Account"):
        res = signup(email_signup, password_signup)
        if res.ok:
            st.success("Account created successfully! Now sign in.")
        else:
            st.error(res.text)

    st.subheader("Sign In")
    email_signin = st.text_input("Email (signin)", key="signin_email")
    password_signin = st.text_input("Password (signin)", type="password", key="signin_pw")
    if st.button("Sign In"):
        res = signin(email_signin, password_signin)
        if res.ok:
            st.success("Signed in successfully!")
        else:
            st.error("Invalid credentials.")

    if st.session_state.token:
        if st.button("Sign Out"):
            st.session_state.token = None
            st.success("Signed out.")


# ================================================================
# MAIN CONTENT
# ================================================================
if not st.session_state.token:
    st.info("Sign in to access features.")
    st.stop()


# ================================================================
# TABS
# ================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📹 Extract Recipe", "🥫 Pantry", "🛒 Grocery Recommendations", "📖 Recipes"])


# ------------------------------------------------------------
# TAB 1 — EXTRACT RECIPE
# ------------------------------------------------------------
with tab1:
    st.header("Extract a Recipe from Video")

    video_url = st.text_input("Enter a YouTube/TikTok/Instagram URL")

    if st.button("Extract Recipe"):
        with st.spinner("Extracting recipe using Gemini..."):
            res = extract_recipe(video_url)

        if res.ok:
            recipe = res.json()
            st.success("Recipe extracted!")
            st.json(recipe)
        else:
            st.error(res.text)


# ------------------------------------------------------------
# TAB 2 — PANTRY
# ------------------------------------------------------------
with tab2:
    st.header("Your Pantry")

    item = st.text_input("Add ingredient")

    if st.button("Add Item"):
        r = add_pantry_item(item)
        if r.ok:
            st.success(f"Added: {item}")
        else:
            st.error(r.text)

    st.subheader("Pantry Items")
    r = list_pantry()
    if r.ok:
        items = r.json()
        if items:
            st.write(items)
        else:
            st.write("No items yet.")
    else:
        st.error(r.text)


# ------------------------------------------------------------
# TAB 3 — RECOMMENDATIONS
# ------------------------------------------------------------
with tab3:
    st.header("Grocery Recommendations")

    if st.button("Get Recommendations"):
        with st.spinner("Computing best ingredients..."):
            r = get_recommendations()

        if r.ok:
            recs = r.json()
            if len(recs) == 0:
                st.info("No recommendations yet. Add recipes and pantry items!")
            else:
                for rec in recs:
                    st.write(f"**{rec['ingredient']}** → unlocks `{rec['unlocks']}` recipes")
        else:
            st.error(r.text)

# ------------------------------------------------------------
# TAB 4 — SHOW RECIPES
# ------------------------------------------------------------
with tab4:
    st.header("Your Recipes")


    r = list_recipes()

    if r.ok:
        recipes = r.json()
        if not recipes:
            st.info("You have no recipes yet.")
        else:
            for recipe in recipes:
                st.markdown(f"""
                ### 🍽 {recipe['title']}
                **Instructions:**  
                {recipe['instructions']}

                **Ingredients:**  
                - { "<br> - ".join(recipe.get('ingredients', [])) if recipe.get('ingredients') else "No ingredients listed" }

                ---
                """, unsafe_allow_html=True)
    else:
        st.error(r.text)

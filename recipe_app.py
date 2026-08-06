import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

st.set_page_config(page_title="Recipe Generator", page_icon="🍽️", layout="centered")
st.title("🍳 Recipe Generator")
st.caption("Tell me what ingredients you have or what you want to eat, and I’ll create a recipe for you.")

if "recipe_text" not in st.session_state:
    st.session_state.recipe_text = ""

api_key = os.getenv("GOOGLE_API_KEY", "").strip()

if not api_key:
    api_key = st.text_input("Google API key", type="password", help="Paste your API key here if it is not already in the .env file.")

if not api_key:
    st.warning("Add your Google API key to the .env file or paste it above to continue.")
    st.stop()

client = genai.Client(api_key=api_key)

with st.sidebar:
    st.header("Recipe preferences")
    meal_type = st.selectbox("Meal type", ["Dinner", "Lunch", "Breakfast", "Dessert", "Snack"])
    cuisine = st.selectbox("Cuisine", ["Any", "Italian", "Indian", "Mexican", "Asian", "American", "Mediterranean"])
    dietary = st.multiselect(
        "Dietary preferences",
        ["Vegetarian", "Vegan", "High protein", "Low carb", "Gluten-free", "Dairy-free"],
    )
    servings = st.slider("Servings", 1, 6, 2)

with st.form("recipe_form", clear_on_submit=False):
    prompt = st.text_area(
        "Describe your recipe idea",
        value=st.session_state.get("prompt", ""),
        placeholder="Example: Create a quick dinner using chicken, spinach, garlic, and rice.",
        height=120,
    )
    submitted = st.form_submit_button("Generate recipe", type="primary")

    if submitted:
        if not prompt.strip():
            st.warning("Please describe the recipe you want.")
            st.stop()

        st.session_state.prompt = prompt

        preferences = []
        if cuisine != "Any":
            preferences.append(f"Cuisine: {cuisine}")
        if meal_type:
            preferences.append(f"Meal type: {meal_type}")
        if dietary:
            preferences.append("Dietary preferences: " + ", ".join(dietary))
        preferences.append(f"Servings: {servings}")

        full_prompt = f"""
You are a helpful cooking assistant.
Create a complete recipe based on this request:
{prompt}

Additional preferences:
- {"\n- ".join(preferences)}

Return the result in this format:
Title
Prep time:
Cook time:
Servings:
Ingredients:
- item 1
- item 2
Instructions:
1. Step one
2. Step two
Tips:
- tip
"""

        with st.spinner("Cooking up your recipe..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=full_prompt,
                )
                st.session_state.recipe_text = getattr(response, "text", str(response))
            except Exception as exc:
                st.error(f"Recipe generation failed: {exc}")
                st.stop()

if st.session_state.recipe_text:
    st.subheader("Your recipe")
    st.markdown(st.session_state.recipe_text)

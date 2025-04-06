# Prompt Generator

**Type:** Generative AI-based Automation Tool
**Duration:** 2024.01 – 2024.03
**Role:** Planning, Data Structure Design, Prototype Development & Operation
**Client:** Internal Design Team (VCD)
**Categories:** 🧠 AI / ML, 🎨 Design & UX, 🛠️ Development & Automation

---

## ✅ Project Overview

This is a web-based tool designed to automatically generate AI image prompts required for brand design tasks. Utilizing **Streamlit (`streamlit`)** for a user-friendly UI, it automatically translates user's Korean input and selected options into English using the **`deep-translator` library (based on Google Translate)**. It automates the process of combining the translated content with selected options like 'Style', 'Season', 'FaceModel', and Midjourney parameters (e.g., `--v`, `--ar`, `--niji`, `--cref`) to generate prompts ready for use in image generation AIs. It also includes a feature to filter inappropriate words using **regular expressions (`re`)**.

---

## 🎯 Key Objectives

*   Reduce the repetitive linguistic/grammatical fatigue associated with writing prompts for AI image generation tools like Midjourney.
*   Ensure consistent image generation results by incorporating unique brand keywords and style guidelines (especially using the `--cref` feature with the `FaceModel` option).
*   Enable non-experts in prompt engineering within the design team to easily create and utilize high-quality AI images.

---

## 🔍 Problem Definition

*   While AI image generation is widespread, proficiency in writing effective prompts varies significantly among individuals.
*   Consistently reflecting a specific brand's identity and style (e.g., maintaining a specific person's face) in generated images is challenging and often involves inefficient repetitive work.
*   Lack of a systematic way to share and manage generated prompt data leads to inconsistencies within the team's work.

---

## 🛠️ Tech Stack (Based on Overall Project)

*   **Language:** Python
*   **Web Framework/UI:** Streamlit (`streamlit`)
*   **Translation:** Deep Translator (`deep-translator`) - Utilizes Google Translate API
*   **Text Processing:** Python `re` (Regular Expressions) - For banned word filtering (`filter_banned_words` function)
*   **Environment Variable Management:** python-dotenv (`dotenv`)
*   *(Based on project description, beyond main.py)*
    *   *AI/Language Processing:* OpenAI API
    *   *Data Processing:* Pandas
    *   *Data Storage/Management:* Gspread + Google Sheets API
    *   *Authentication/User Management:* Firebase

---

## 📊 Key Achievements

*   Achieved a **26% reduction in average task time** spent on prompt writing.
*   Replaced **80% of previously licensed images** by utilizing images generated via Midjourney and Firefly.
*   Achieved **100% adoption** within the internal design team, enabling easy use even for new designers and non-designer roles.
*   Recorded an **average daily usage of over 50 prompts** after service stabilization, with **over 500 prompts generated** cumulatively.

---

## 🔄 Workflow (Based on main.py)

1.  **Input:** User selects and inputs image attributes (style, season, weather, description, etc.) via the web UI (`st.selectbox`, `st.checkbox`, `st.text_input`, etc.).
2.  **Translation:** Selected keywords are translated using the `translate_to_english` function (dictionary-based), and the detailed description is translated using `translate_sentence_to_english` function (using `deep-translator`).
3.  **Prompt Assembly (`get_prompt` function):** Combines the translated texts with Midjourney parameters based on selected options (`fixed_parts`, `face_model_part`, etc.) to create the final prompt.
4.  **Banned Word Filtering (`filter_banned_words` function):** Filters words from the `banned_words` list in the generated prompt, considering `contextual_allowances`.
5.  **Display & Storage:** The completed prompt is displayed in an `st.text_area` and stored in `st.session_state['prompts']` for history tracking.
6.  **(External Use):** The user copies the displayed prompt for use in external tools like Midjourney.
7.  *(Based on project description, beyond main.py) Generated prompts and result images might be automatically saved to Google Sheets.*

---

## 🖼️ UI Examples (Based on main.py Code)

*   **Main Screen:** Selection for 'Style', 'Season', 'Time', 'Weather', 'Ratio' using `st.selectbox`. 'Description' input using `st.text_input`.
*   **Advanced Settings:** Options for 'Person', 'Composition', 'Camera View', 'Camera', 'FaceModel' provided within an `st.expander` using `st.checkbox` and `st.selectbox`. Tooltips (`st.markdown` with HTML/CSS) provide additional information.
*   **Results Screen:** Clicking the `st.button` triggers the `handle_create_prompt` function to generate the prompt. The list of generated prompts (`st.session_state['prompts']`) is displayed using `st.text_area`.
*   **FaceModel Feature:** Selecting 'Ara' or 'Gookin' automatically adds specific Midjourney `--cref` URLs and the `--cw 0` parameter to the prompt (logic within the `get_prompt` function).

---

## 🔗 Live Demo

[https://artist.streamlit.app](https://artist.streamlit.app)

---

## 🔍 Keywords

Prompt Engineering, Midjourney, Image Consistency, Streamlit, **Deep Translator**, **Regular Expressions (Regex)**, Design Automation, Template System, Generative AI, Automatic Translation, **Banned Word Filtering**, **Face Locking (FaceModel, --cref)**

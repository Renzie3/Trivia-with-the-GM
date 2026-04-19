import streamlit as st
import random
import json
import os
from io import BytesIO
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import google.generativeai as genai

st.set_page_config(page_title="Trivia with the GM", layout="wide")

# =========================================================
# FILE PATHS
# =========================================================
SAVED_GAMES_DIR = "saved_games"
USED_QUESTIONS_FILE = "used_questions.json"
LOGO_FILE = "logo.png"

if not os.path.exists(SAVED_GAMES_DIR):
    os.makedirs(SAVED_GAMES_DIR)

if not os.path.exists(USED_QUESTIONS_FILE):
    with open(USED_QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# =========================================================
# CONSTANTS
# =========================================================
ALL_CATEGORIES = [
    "Geography",
    "History",
    "American Current Events",
    "World Current Events",
    "Name That Tune",
    "Health",
    "Movies",
    "Television",
    "US Constitution",
    "Sports History",
    "Sports Current Events",
    "World Records",
    "Word Scramble"
]

STANDARD_CATEGORIES = [
    "Geography",
    "History",
    "American Current Events",
    "World Current Events",
    "Health",
    "Movies",
    "Television",
    "US Constitution",
    "Sports History",
    "Sports Current Events",
    "World Records"
]

WORD_SCRAMBLE_BANK = [
    {"word": "TREASURE", "clue": "Something worth keeping safe", "sources": ["https://www.merriam-webster.com/dictionary/treasure"]},
    {"word": "ATHLETIC", "clue": "Related to sports or physical skill", "sources": ["https://www.merriam-webster.com/dictionary/athletic"]},
    {"word": "HORIZONS", "clue": "What may broaden when you learn more", "sources": ["https://www.merriam-webster.com/dictionary/horizon"]},
    {"word": "LANDMARK", "clue": "A notable point of reference", "sources": ["https://www.merriam-webster.com/dictionary/landmark"]},
    {"word": "JUDICIAL", "clue": "Connected to courts or judges", "sources": ["https://www.merriam-webster.com/dictionary/judicial"]},
    {"word": "PLAYBOOK", "clue": "A set of planned actions", "sources": ["https://www.merriam-webster.com/dictionary/playbook"]},
    {"word": "HEADLINE", "clue": "Something that catches public attention", "sources": ["https://www.merriam-webster.com/dictionary/headline"]},
    {"word": "NOTEBOOK", "clue": "A place to keep ideas", "sources": ["https://www.merriam-webster.com/dictionary/notebook"]},
    {"word": "CHAMPION", "clue": "A winner at the highest level", "sources": ["https://www.merriam-webster.com/dictionary/champion"]},
    {"word": "ELECTION", "clue": "A public choice process", "sources": ["https://www.merriam-webster.com/dictionary/election"]}
]

# =========================================================
# HELPERS: FILE IO
# =========================================================
def load_json_file(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_used_questions():
    return load_json_file(USED_QUESTIONS_FILE, [])

def save_used_questions(data):
    save_json_file(USED_QUESTIONS_FILE, data)

def add_questions_to_history(questions):
    history = load_used_questions()
    for q in questions:
        history.append({
            "question": q.get("question", ""),
            "answer": q.get("answer", ""),
            "category": q.get("category", ""),
            "difficulty": q.get("difficulty", ""),
            "timestamp": datetime.now().isoformat()
        })
    save_used_questions(history)

# =========================================================
# GEMINI CONFIG
# =========================================================
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("Missing GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

genai.configure(api_key=api_key)

def get_gemini_model():
    candidate_models = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]

    for model_name in candidate_models:
        try:
            test_model = genai.GenerativeModel(model_name)
            response = test_model.generate_content("Reply with only the word OK.")
            if response:
                return test_model, model_name
        except Exception:
            continue

    return None, None

model, active_model_name = get_gemini_model()

if model is None:
    st.error("No supported Gemini model was found for your API key.")
    st.info("Please confirm your Gemini API access and model availability.")
    st.stop()

# =========================================================
# APP HEADER
# =========================================================
if os.path.exists(LOGO_FILE):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo = Image.open(LOGO_FILE)
        st.image(logo, width=220)

st.title("Trivia with the GM")
st.caption("Country Club Trivia Night Generator • Gemini AI Version")

st.markdown("""
Designed for an adult country club audience with a broad age range and strong general knowledge.

### Game 1
- Round 1: easy
- Round 2: medium
- Round 3: hard
- 10 questions per round

### Game 2
- 15 questions
- mixed difficulty
- includes 2 Name That Tune
- includes 2 Word Scramble
""")

# =========================================================
# SESSION STATE
# =========================================================
def init_state():
    if "game1" not in st.session_state:
        st.session_state.game1 = []
    if "game2" not in st.session_state:
        st.session_state.game2 = []
    if "saved_name" not in st.session_state:
        st.session_state.saved_name = ""

init_state()

# =========================================================
# WORD SCRAMBLE
# =========================================================
def shuffle_word(word):
    chars = list(word)
    while True:
        random.shuffle(chars)
        scrambled = "".join(chars)
        if scrambled != word:
            return scrambled

def generate_word_scramble(difficulty="medium"):
    item = random.choice(WORD_SCRAMBLE_BANK)
    return {
        "category": "Word Scramble",
        "difficulty": difficulty,
        "question": f"Unscramble this {len(item['word'])}-letter word: {shuffle_word(item['word'])}",
        "answer": item["word"],
        "notes": f"Vague clue: {item['clue']}",
        "sources": item["sources"]
    }

# =========================================================
# AI HELPERS
# =========================================================
def get_recent_history_text(limit=80):
    history = load_used_questions()
    recent = history[-limit:] if history else []
    return json.dumps(recent, indent=2)

def extract_json_from_text(text):
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text

def generate_ai_questions(category, difficulty, count):
    history_text = get_recent_history_text()

    if category == "Name That Tune":
        prompt = f"""
Generate {count} high-quality trivia items for a country club trivia night.

Audience:
- Adults age 18-70
- High school graduates
- Most have 2-4 years of college education
- Questions should feel polished, fair, and enjoyable

Category: Name That Tune
Difficulty: {difficulty}

Requirements:
- Return ONLY valid JSON
- Return a JSON array of exactly {count} objects
- Do not repeat or closely resemble prior used questions listed below
- Songs should be popular and recognizable from roughly the last 50 years
- Include:
  - category
  - difficulty
  - question
  - answer
  - notes
  - song
  - writers
  - performer
  - release_date
  - clip_length
  - sources
- The question should tell the host to play the opening of the song
- sources must contain at least 1 reputable source
- Keep metadata accurate
- Avoid markdown

Used question history to avoid:
{history_text}

JSON format:
[
  {{
    "category": "Name That Tune",
    "difficulty": "{difficulty}",
    "question": "Name That Tune: Play the opening of this song.",
    "answer": "Song Title",
    "notes": "Accept song title.",
    "song": "Song Title",
    "writers": "Writer names",
    "performer": "Best known performer",
    "release_date": "Month Day, Year",
    "clip_length": "4 seconds",
    "sources": ["https://example.com"]
  }}
]
"""
    else:
        prompt = f"""
Generate {count} high-quality trivia questions for a country club trivia night.

Audience:
- Adults age 18-70
- High school graduates
- Most have 2-4 years of college education
- Questions should feel polished, fair, and enjoyable

Category: {category}
Difficulty: {difficulty}

Requirements:
- Return ONLY valid JSON
- Return a JSON array of exactly {count} objects
- Do not repeat or closely resemble prior used questions listed below
- Questions should be fact-based and suitable for live trivia
- Avoid childish or overly obscure trivia
- Include:
  - category
  - difficulty
  - question
  - answer
  - notes
  - sources
- sources must contain at least 1 reputable source
- Current events questions should be timely if possible, but still carefully sourceable
- Avoid markdown

Used question history to avoid:
{history_text}

JSON format:
[
  {{
    "category": "{category}",
    "difficulty": "{difficulty}",
    "question": "Question text",
    "answer": "Answer text",
    "notes": "Optional host note",
    "sources": ["https://example.com"]
  }}
]
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text if hasattr(response, "text") else ""
        json_text = extract_json_from_text(raw_text)
        data = json.loads(json_text)
        if isinstance(data, dict):
            data = [data]
        return data
    except Exception:
        return []

def clean_ai_question(item, category, difficulty):
    q = {
        "category": item.get("category", category),
        "difficulty": item.get("difficulty", difficulty),
        "question": str(item.get("question", "")).strip(),
        "answer": str(item.get("answer", "")).strip(),
        "notes": str(item.get("notes", "")).strip(),
        "sources": item.get("sources", [])
    }

    if not isinstance(q["sources"], list):
        q["sources"] = [str(q["sources"])]

    q["sources"] = [str(s).strip() for s in q["sources"] if str(s).strip()]

    if category == "Name That Tune":
        q["song"] = str(item.get("song", "")).strip()
        q["writers"] = str(item.get("writers", "")).strip()
        q["performer"] = str(item.get("performer", "")).strip()
        q["release_date"] = str(item.get("release_date", "")).strip()
        q["clip_length"] = str(item.get("clip_length", "")).strip()

    return q

def generate_question(category, difficulty):
    if category == "Word Scramble":
        return generate_word_scramble(difficulty)

    ai_items = generate_ai_questions(category, difficulty, 1)
    if ai_items:
        q = clean_ai_question(ai_items[0], category, difficulty)
        if q["question"] and q["answer"]:
            return q

    return {
        "category": category,
        "difficulty": difficulty,
        "question": f"Placeholder question for {category}",
        "answer": "TBD",
        "notes": "AI generation failed for this item. Try Replace This Question.",
        "sources": ["Source needed"]
    }

# =========================================================
# GAME GENERATION
# =========================================================
def safe_pick(pool, count):
    result = []
    local_pool = pool[:]
    while len(result) < count:
        if not local_pool:
            local_pool = pool[:]
        random.shuffle(local_pool)
        result.append(local_pool.pop())
    return result

def generate_game_1():
    rounds = []
    all_generated = []
    round_specs = [
        ("Round 1", "easy"),
        ("Round 2", "medium"),
        ("Round 3", "hard")
    ]

    for round_name, difficulty in round_specs:
        categories = safe_pick(ALL_CATEGORIES, 10)
        questions = [generate_question(cat, difficulty) for cat in categories]
        all_generated.extend(questions)
        rounds.append({
            "round_name": round_name,
            "round_difficulty": difficulty,
            "questions": questions
        })

    add_questions_to_history(all_generated)
    return rounds

def generate_game_2():
    fixed = ["Name That Tune", "Name That Tune", "Word Scramble", "Word Scramble"]
    others = safe_pick(STANDARD_CATEGORIES, 11)
    categories = fixed + others
    random.shuffle(categories)

    difficulties = ["easy"] * 5 + ["medium"] * 5 + ["hard"] * 5
    random.shuffle(difficulties)

    questions = [generate_question(cat, diff) for cat, diff in zip(categories, difficulties)]
    add_questions_to_history(questions)

    return [{
        "round_name": "Game 2 - Mixed Difficulty Round",
        "round_difficulty": "mixed",
        "questions": questions
    }]

# =========================================================
# SAVE / LOAD
# =========================================================
def export_json_payload():
    return json.dumps({
        "title": "Trivia with the GM",
        "generated_at": datetime.now().isoformat(),
        "game_1": st.session_state.game1,
        "game_2": st.session_state.game2
    }, indent=2)

def save_current_games(save_name):
    if not save_name.strip():
        return False, "Please enter a name for the saved game."
    payload = {
        "title": "Trivia with the GM",
        "saved_at": datetime.now().isoformat(),
        "game_1": st.session_state.game1,
        "game_2": st.session_state.game2
    }
    path = os.path.join(SAVED_GAMES_DIR, f"{save_name.strip()}.json")
    save_json_file(path, payload)
    return True, f"Saved to {path}"

def list_saved_games():
    return sorted([f for f in os.listdir(SAVED_GAMES_DIR) if f.endswith(".json")])

def load_saved_game(filename):
    path = os.path.join(SAVED_GAMES_DIR, filename)
    data = load_json_file(path, {})
    st.session_state.game1 = data.get("game_1", [])
    st.session_state.game2 = data.get("game_2", [])

# =========================================================
# REPLACE QUESTION
# =========================================================
def replace_question(game_key, round_index, question_index):
    game = st.session_state[game_key]
    q = game[round_index]["questions"][question_index]
    category = q["category"]
    difficulty = q.get("difficulty", "medium")
    new_q = generate_question(category, difficulty)
    game[round_index]["questions"][question_index] = new_q
    add_questions_to_history([new_q])

# =========================================================
# PDF HELPERS
# =========================================================
def draw_wrapped_text(pdf, text, x, y, max_width=500, line_height=14, font="Helvetica", font_size=10):
    pdf.setFont(font, font_size)
    words = text.split()
    line = ""
    lines = []
    for word in words:
        test = f"{line} {word}".strip()
        if pdf.stringWidth(test, font, font_size) < max_width:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    for ln in lines:
        pdf.drawString(x, y, ln)
        y -= line_height
    return y

def build_host_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 70

    pdf.setTitle("Trivia with the GM - Host Sheet")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, height - 40, "Trivia with the GM - Host Sheet")

    for game_title, rounds in [("Game 1", st.session_state.game1), ("Game 2", st.session_state.game2)]:
        if not rounds:
            continue

        if y < 120:
            pdf.showPage()
            y = height - 70

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, game_title)
        y -= 20

        for rnd in rounds:
            if y < 140:
                pdf.showPage()
                y = height - 70
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, f"{rnd['round_name']} ({rnd.get('round_difficulty','')})")
            y -= 18

            for idx, q in enumerate(rnd["questions"], start=1):
                if y < 180:
                    pdf.showPage()
                    y = height - 70

                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(40, y, f"{idx}. [{q['category']}] [{q.get('difficulty','')}]")
                y -= 14

                y = draw_wrapped_text(pdf, f"Q: {q['question']}", 50, y, 510)
                y = draw_wrapped_text(pdf, f"A: {q['answer']}", 50, y, 510)

                if q.get("notes"):
                    y = draw_wrapped_text(pdf, f"Notes: {q['notes']}", 50, y, 510)

                if q["category"] == "Name That Tune":
                    y = draw_wrapped_text(pdf, f"Song: {q.get('song','')}", 50, y, 510)
                    y = draw_wrapped_text(pdf, f"Writer(s): {q.get('writers','')}", 50, y, 510)
                    y = draw_wrapped_text(pdf, f"Performer: {q.get('performer','')}", 50, y, 510)
                    y = draw_wrapped_text(pdf, f"Release Date: {q.get('release_date','')}", 50, y, 510)
                    y = draw_wrapped_text(pdf, f"Recommended Clip Length: {q.get('clip_length','')}", 50, y, 510)

                if q.get("sources"):
                    y = draw_wrapped_text(pdf, "Sources:", 50, y, 510)
                    for s in q["sources"]:
                        y = draw_wrapped_text(pdf, f"- {s}", 60, y, 500, 12, "Helvetica", 9)

                y -= 10

    pdf.save()
    buffer.seek(0)
    return buffer

def build_score_sheet_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle("Trivia with the GM - Score Sheets")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 40, "Trivia with the GM - Score Sheets")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 65, "Team Name: ______________________________")
    pdf.drawString(40, height - 85, "Date: ______________________________")

    y = height - 120
    sections = [
        ("Game 1 - Round 1", 10),
        ("Game 1 - Round 2", 10),
        ("Game 1 - Round 3", 10),
        ("Game 2", 15)
    ]

    for title, count in sections:
        if y < 100:
            pdf.showPage()
            y = height - 50
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(40, y, title)
        y -= 18
        pdf.setFont("Helvetica", 11)
        for i in range(1, count + 1):
            if y < 80:
                pdf.showPage()
                y = height - 50
            pdf.drawString(50, y, f"Question {i}: ______")
            y -= 16
        pdf.drawString(50, y, "Round Total: ______")
        y -= 28

    if y < 80:
        pdf.showPage()
        y = height - 50

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Grand Total: ______")
    pdf.save()
    buffer.seek(0)
    return buffer

# =========================================================
# EDITORS
# =========================================================
def render_sources_editor(q, key_prefix):
    sources_text = "\n".join(q.get("sources", []))
    edited_sources = st.text_area(
        "Sources (one per line)",
        value=sources_text,
        key=f"{key_prefix}_sources",
        height=100
    )
    q["sources"] = [line.strip() for line in edited_sources.split("\n") if line.strip()]

def render_question_editor(round_index, q, q_idx, game_key):
    prefix = f"{game_key}_{round_index}_{q_idx}"

    with st.expander(f"Q{q_idx + 1}: {q['category']} • {q.get('difficulty','')}", expanded=False):
        c1, c2 = st.columns([4, 1])
        with c1:
            q["category"] = st.text_input("Category", value=q["category"], key=f"{prefix}_category")
        with c2:
            if st.button("🔄 Replace This Question", key=f"{prefix}_replace"):
                with st.spinner("Replacing question..."):
                    replace_question(game_key, round_index, q_idx)
                st.rerun()

        diff_options = ["easy", "medium", "hard", "mixed"]
        current_diff = q.get("difficulty", "medium")
        if current_diff not in diff_options:
            current_diff = "medium"

        q["difficulty"] = st.selectbox(
            "Difficulty",
            diff_options,
            index=diff_options.index(current_diff),
            key=f"{prefix}_difficulty"
        )

        q["question"] = st.text_area("Question", value=q["question"], key=f"{prefix}_question", height=100)
        q["answer"] = st.text_input("Answer", value=q["answer"], key=f"{prefix}_answer")
        q["notes"] = st.text_area("Host Notes", value=q.get("notes", ""), key=f"{prefix}_notes", height=80)

        if q["category"] == "Name That Tune":
            st.markdown("#### Name That Tune Details")
            q["song"] = st.text_input("Song", value=q.get("song", ""), key=f"{prefix}_song")
            q["writers"] = st.text_input("Writer(s)", value=q.get("writers", ""), key=f"{prefix}_writers")
            q["performer"] = st.text_input("Best Known Performer", value=q.get("performer", ""), key=f"{prefix}_performer")
            q["release_date"] = st.text_input("Release Date", value=q.get("release_date", ""), key=f"{prefix}_release_date")
            q["clip_length"] = st.text_input("Recommended Intro Clip Length", value=q.get("clip_length", ""), key=f"{prefix}_clip_length")

        render_sources_editor(q, prefix)

        if st.checkbox("Reveal answer", key=f"{prefix}_reveal"):
            st.success(f"Answer: {q['answer']}")
            if q.get("notes"):
                st.info(q["notes"])

            if q["category"] == "Name That Tune":
                st.write(f"**Song:** {q.get('song', '')}")
                st.write(f"**Writer(s):** {q.get('writers', '')}")
                st.write(f"**Best Known Performer:** {q.get('performer', '')}")
                st.write(f"**Release Date:** {q.get('release_date', '')}")
                st.write(f"**Recommended Clip Length:** {q.get('clip_length', '')}")

            if q.get("sources"):
                st.write("**Sources:**")
                for s in q["sources"]:
                    st.write(f"- {s}")

def render_rounds(rounds, game_key):
    for r_idx, rnd in enumerate(rounds):
        st.markdown(f"## {rnd['round_name']} • Difficulty: {rnd.get('round_difficulty', 'n/a')}")
        for q_idx, q in enumerate(rnd["questions"]):
            render_question_editor(r_idx, q, q_idx, game_key)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Controls")
st.sidebar.success(f"Using Gemini model: {active_model_name}")

if st.sidebar.button("Generate Game 1"):
    with st.spinner("Generating Game 1..."):
        st.session_state.game1 = generate_game_1()

if st.sidebar.button("Generate Game 2"):
    with st.spinner("Generating Game 2..."):
        st.session_state.game2 = generate_game_2()

if st.sidebar.button("Generate Both Games"):
    with st.spinner("Generating both games... this may take a moment."):
        st.session_state.game1 = generate_game_1()
        st.session_state.game2 = generate_game_2()

if st.sidebar.button("Clear All"):
    st.session_state.game1 = []
    st.session_state.game2 = []

st.sidebar.markdown("---")
st.sidebar.subheader("Save / Load")

save_name = st.sidebar.text_input("Save current games as", value=st.session_state.saved_name)
st.session_state.saved_name = save_name

if st.sidebar.button("Save Current Games"):
    ok, msg = save_current_games(save_name)
    if ok:
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

saved_files = list_saved_games()
selected_saved = st.sidebar.selectbox("Load a saved game", [""] + saved_files)

if st.sidebar.button("Load Selected Saved Game"):
    if selected_saved:
        load_saved_game(selected_saved)
        st.sidebar.success(f"Loaded {selected_saved}")
    else:
        st.sidebar.warning("Please select a saved game.")

st.sidebar.markdown("---")
st.sidebar.info("""
Tips:
- Round 1 is easier, Round 2 medium, Round 3 harder.
- Game 2 mixes all difficulty levels.
- Replace regenerates only one question.
- Review current events and music metadata before final use.
""")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Game 1",
    "Game 2",
    "Export / Print",
    "Saved Games",
    "Instructions"
])

with tab1:
    st.header("Game 1")
    if not st.session_state.game1:
        st.info("Click 'Generate Game 1' or 'Generate Both Games' in the sidebar.")
    else:
        render_rounds(st.session_state.game1, "game1")

with tab2:
    st.header("Game 2")
    if not st.session_state.game2:
        st.info("Click 'Generate Game 2' or 'Generate Both Games' in the sidebar.")
    else:
        render_rounds(st.session_state.game2, "game2")

with tab3:
    st.header("Export / Print")
    if st.session_state.game1 or st.session_state.game2:
        st.download_button(
            "Download JSON",
            data=export_json_payload(),
            file_name="trivia_with_the_gm.json",
            mime="application/json"
        )

        host_pdf = build_host_pdf()
        st.download_button(
            "Download Host PDF",
            data=host_pdf,
            file_name="trivia_with_the_gm_host_sheet.pdf",
            mime="application/pdf"
        )

        score_pdf = build_score_sheet_pdf()
        st.download_button(
            "Download Score Sheet PDF",
            data=score_pdf,
            file_name="trivia_with_the_gm_score_sheets.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Generate at least one game first.")

with tab4:
    st.header("Saved Games")
    files = list_saved_games()
    if files:
        for f in files:
            st.write(f"- {f}")
    else:
        st.info("No saved games yet.")

with tab5:
    st.header("Instructions")
    st.markdown("""
### How to use
1. Click **Generate Both Games**
2. Review each round
3. Use **Replace This Question** if needed
4. Edit any wording manually if desired
5. Save the game
6. Download the Host PDF and Score Sheets

### AI generation
- This version uses Gemini AI
- It tries multiple Gemini model names automatically
- It stores used questions in `used_questions.json`

### Important review
Please review before use, especially:
- current events
- sports current events
- world records
- Name That Tune writer / release date metadata

### Streamlit Cloud note
File-based history and saved games may not persist forever on Community Cloud.
For long-term recordkeeping, download JSON and PDFs.
""")

st.markdown("---")
st.caption("Trivia with the GM • Gemini AI Version")
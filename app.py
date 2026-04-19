import streamlit as st
import random
import json
import os
from io import BytesIO
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Trivia with the GM", layout="wide")

# =========================================================
# FILE PATHS
# =========================================================
QUESTION_BANK_FILE = "question_bank.json"
CURRENT_EVENTS_FILE = "current_events.json"
SAVED_GAMES_DIR = "saved_games"
LOGO_FILE = "logo.png"

if not os.path.exists(SAVED_GAMES_DIR):
    os.makedirs(SAVED_GAMES_DIR)

# =========================================================
# LOADERS
# =========================================================
def load_json_file(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

QUESTION_BANK = load_json_file(QUESTION_BANK_FILE, {})
CURRENT_EVENTS = load_json_file(CURRENT_EVENTS_FILE, {})

# Merge curated current events into the main bank
for cat, items in CURRENT_EVENTS.items():
    QUESTION_BANK.setdefault(cat, [])
    QUESTION_BANK[cat].extend(items)

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

# =========================================================
# APP HEADER
# =========================================================
if os.path.exists(LOGO_FILE):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo = Image.open(LOGO_FILE)
        st.image(logo, width=220)

st.title("Trivia with the GM")
st.caption("Country Club Trivia Night Generator • Version 3")

st.markdown("""
Designed for an adult country club audience with broad general knowledge and mixed age ranges.
- **Game 1:** 3 rounds × 10 questions
  - Round 1 = easier
  - Round 2 = medium
  - Round 3 = harder
- **Game 2:** 1 round × 15 questions
  - mixed difficulty
  - includes **2 Name That Tune**
  - includes **2 Word Scramble**
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
# HELPERS
# =========================================================
def shuffle_word(word):
    chars = list(word)
    while True:
        random.shuffle(chars)
        scrambled = "".join(chars)
        if scrambled != word:
            return scrambled

def generate_word_scramble():
    item = random.choice(WORD_SCRAMBLE_BANK)
    return {
        "category": "Word Scramble",
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "question": f"Unscramble this {len(item['word'])}-letter word: {shuffle_word(item['word'])}",
        "answer": item["word"],
        "notes": f"Vague clue: {item['clue']}",
        "sources": item["sources"]
    }

def normalize_question(category, item):
    q = {
        "category": category,
        "difficulty": item.get("difficulty", "medium"),
        "question": item.get("question", ""),
        "answer": item.get("answer", ""),
        "notes": item.get("notes", ""),
        "sources": item.get("sources", [])
    }
    if category == "Name That Tune":
        q["song"] = item.get("song", "")
        q["writers"] = item.get("writers", "")
        q["performer"] = item.get("performer", "")
        q["release_date"] = item.get("release_date", "")
        q["clip_length"] = item.get("clip_length", "")
    return q

def get_questions_by_difficulty(category, difficulty):
    if category == "Word Scramble":
        return [generate_word_scramble()]
    bank = QUESTION_BANK.get(category, [])
    return [normalize_question(category, q) for q in bank if q.get("difficulty", "medium") == difficulty]

def get_any_question(category):
    if category == "Word Scramble":
        return generate_word_scramble()
    bank = QUESTION_BANK.get(category, [])
    if not bank:
        return {
            "category": category,
            "difficulty": "medium",
            "question": f"Placeholder question for {category}",
            "answer": "TBD",
            "notes": "",
            "sources": ["Add source"]
        }
    return normalize_question(category, random.choice(bank))

def get_question_for_round(category, difficulty, used_questions=None):
    if used_questions is None:
        used_questions = set()

    if category == "Word Scramble":
        return generate_word_scramble()

    choices = get_questions_by_difficulty(category, difficulty)
    random.shuffle(choices)
    for c in choices:
        if c["question"] not in used_questions:
            return c

    # fallback to any difficulty in same category
    fallback = [normalize_question(category, q) for q in QUESTION_BANK.get(category, [])]
    random.shuffle(fallback)
    for c in fallback:
        if c["question"] not in used_questions:
            return c

    return get_any_question(category)

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
    difficulties = [("Round 1", "easy"), ("Round 2", "medium"), ("Round 3", "hard")]
    used = set()

    category_pool = ALL_CATEGORIES[:]

    for round_name, difficulty in difficulties:
        categories = safe_pick(category_pool, 10)
        questions = []
        for cat in categories:
            q = get_question_for_round(cat, difficulty, used)
            used.add(q["question"])
            questions.append(q)
        rounds.append({
            "round_name": round_name,
            "round_difficulty": difficulty,
            "questions": questions
        })
    return rounds

def generate_game_2():
    used = set()
    fixed = ["Name That Tune", "Name That Tune", "Word Scramble", "Word Scramble"]
    others = safe_pick(STANDARD_CATEGORIES, 11)
    categories = fixed + others
    random.shuffle(categories)

    difficulty_mix = ["easy"] * 5 + ["medium"] * 5 + ["hard"] * 5
    random.shuffle(difficulty_mix)

    questions = []
    for i, cat in enumerate(categories):
        q = get_question_for_round(cat, difficulty_mix[i], used)
        used.add(q["question"])
        questions.append(q)

    return [{
        "round_name": "Game 2 - Mixed Difficulty Round",
        "round_difficulty": "mixed",
        "questions": questions
    }]

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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return True, f"Saved to {path}"

def list_saved_games():
    if not os.path.exists(SAVED_GAMES_DIR):
        return []
    return sorted([f for f in os.listdir(SAVED_GAMES_DIR) if f.endswith(".json")])

def load_saved_game(filename):
    path = os.path.join(SAVED_GAMES_DIR, filename)
    data = load_json_file(path, {})
    st.session_state.game1 = data.get("game_1", [])
    st.session_state.game2 = data.get("game_2", [])

def replace_question(game_key, round_index, question_index):
    game = st.session_state[game_key]
    q = game[round_index]["questions"][question_index]
    category = q["category"]
    difficulty = q.get("difficulty", "medium")
    current_text = q["question"]

    if category == "Word Scramble":
        new_q = generate_word_scramble()
    else:
        candidates = [normalize_question(category, item) for item in QUESTION_BANK.get(category, [])]
        same_difficulty = [c for c in candidates if c.get("difficulty") == difficulty and c["question"] != current_text]
        any_difficulty = [c for c in candidates if c["question"] != current_text]
        if same_difficulty:
            new_q = random.choice(same_difficulty)
        elif any_difficulty:
            new_q = random.choice(any_difficulty)
        else:
            new_q = get_any_question(category)

    game[round_index]["questions"][question_index] = new_q

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

    def new_page(title):
        pdf.showPage()
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, height - 40, title)

    pdf.setTitle("Trivia with the GM - Host Sheet")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 40, "Trivia with the GM - Host Sheet")
    y = height - 70

    for section_title, rounds in [("Game 1", st.session_state.game1), ("Game 2", st.session_state.game2)]:
        if not rounds:
            continue
        if y < 120:
            new_page("Trivia with the GM - Host Sheet")
            y = height - 70

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, section_title)
        y -= 20

        for rnd in rounds:
            if y < 140:
                new_page("Trivia with the GM - Host Sheet")
                y = height - 70
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, f"{rnd['round_name']} ({rnd.get('round_difficulty', '')})")
            y -= 18

            for idx, q in enumerate(rnd["questions"], start=1):
                if y < 160:
                    new_page("Trivia with the GM - Host Sheet")
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
                    y = draw_wrapped_text(pdf, f"Release date: {q.get('release_date','')}", 50, y, 510)
                    y = draw_wrapped_text(pdf, f"Recommended clip length: {q.get('clip_length','')}", 50, y, 510)

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
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(40, y, title)
        y -= 18
        pdf.setFont("Helvetica", 11)
        for i in range(1, count + 1):
            pdf.drawString(50, y, f"Question {i}: ______")
            y -= 16
            if y < 80:
                pdf.showPage()
                y = height - 50
        pdf.drawString(50, y, "Round Total: ______")
        y -= 28
        if y < 100:
            pdf.showPage()
            y = height - 50

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Grand Total: ______")
    pdf.save()
    buffer.seek(0)
    return buffer

def render_sources_editor(q, key_prefix):
    sources_text = "\n".join(q.get("sources", []))
    edited_sources = st.text_area(
        "Sources (one per line)",
        value=sources_text,
        key=f"{key_prefix}_sources",
        height=100
    )
    q["sources"] = [line.strip() for line in edited_sources.split("\n") if line.strip()]

def render_question_editor(round_data, round_index, q, q_idx, game_key):
    prefix = f"{game_key}_{round_index}_{q_idx}"

    with st.expander(f"Q{q_idx + 1}: {q['category']} • {q.get('difficulty','')}", expanded=False):
        c1, c2 = st.columns([4, 1])
        with c1:
            q["category"] = st.text_input("Category", value=q["category"], key=f"{prefix}_category")
        with c2:
            if st.button("🔄 Replace This Question", key=f"{prefix}_replace"):
                replace_question(game_key, round_index, q_idx)
                st.rerun()

        q["difficulty"] = st.selectbox(
            "Difficulty",
            ["easy", "medium", "hard", "mixed"],
            index=["easy", "medium", "hard", "mixed"].index(q.get("difficulty", "medium")) if q.get("difficulty", "medium") in ["easy", "medium", "hard", "mixed"] else 1,
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
            render_question_editor(rnd, r_idx, q, q_idx, game_key)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Controls")

if st.sidebar.button("Generate Game 1"):
    st.session_state.game1 = generate_game_1()

if st.sidebar.button("Generate Game 2"):
    st.session_state.game2 = generate_game_2()

if st.sidebar.button("Generate Both Games"):
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
- Use Replace This Question to swap only one question.
- Re-check time-sensitive topics before game night.
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
3. Use **Replace This Question** if you do not like one
4. Edit any text if needed
5. Save the game set with a name
6. Download the **Host PDF**
7. Download the **Score Sheet PDF**

### Current events
- This version uses curated current-events questions from `current_events.json`
- Update that file before an event if you want fresher material

### Name That Tune
- This app provides:
  - song
  - writer(s)
  - best known performer
  - release date
  - recommended opening clip length
- You should play your own legal music clips during the event

### Previous games
- Saved games are stored in the `saved_games` folder
- On Streamlit Community Cloud, file storage may not be persistent long-term
- For permanent archival, always download your JSON or PDFs

### Source verification
- Every starter question has at least one source
- For changing topics like world records or current events, do a quick final fact check before use
""")

st.markdown("---")
st.caption("Trivia with the GM • Version 3")
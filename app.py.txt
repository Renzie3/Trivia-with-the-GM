import streamlit as st
import random
import json
from datetime import datetime

st.set_page_config(page_title="Trivia with the GM", layout="wide")

# =========================================================
# APP HEADER
# =========================================================
st.title("🎙️ Trivia with the GM")
st.caption("Country Club Trivia Night Generator")

st.markdown("""
This app creates two trivia games:

### Game 1
- 3 rounds
- 10 questions per round

### Game 2
- 1 round
- 15 questions total
- Includes **2 Name That Tune**
- Includes **2 Word Scramble**

Each question includes:
- Category
- Question
- Answer
- Host notes
- At least one source citation

You can also:
- Replace any question individually
- Edit any question manually
- Export your trivia set
- Use host-friendly print view
""")

# =========================================================
# CATEGORIES
# =========================================================
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
    "World Records",
]

SPECIAL_CATEGORIES = [
    "Name That Tune",
    "Word Scramble",
]

ALL_CATEGORIES = STANDARD_CATEGORIES + SPECIAL_CATEGORIES

# =========================================================
# QUESTION BANK
# Every entry includes sources
# =========================================================
QUESTION_BANK = {
    "Geography": [
        {
            "question": "What is the capital city of Australia?",
            "answer": "Canberra",
            "notes": "A common trick question because many people guess Sydney or Melbourne.",
            "sources": [
                "https://www.britannica.com/place/Canberra",
                "https://www.australia.gov.au/about-australia/our-country"
            ]
        },
        {
            "question": "Mount Kilimanjaro is located in which country?",
            "answer": "Tanzania",
            "notes": "",
            "sources": [
                "https://www.britannica.com/place/Mount-Kilimanjaro",
                "https://whc.unesco.org/en/list/403/"
            ]
        },
        {
            "question": "What river flows through Egypt and is one of the longest rivers in the world?",
            "answer": "The Nile River",
            "notes": "",
            "sources": [
                "https://www.britannica.com/place/Nile-River",
                "https://education.nationalgeographic.org/resource/nile-river/"
            ]
        },
        {
            "question": "What is the largest ocean on Earth?",
            "answer": "The Pacific Ocean",
            "notes": "",
            "sources": [
                "https://www.noaa.gov/education/resource-collections/ocean-coasts/ocean",
                "https://www.britannica.com/place/Pacific-Ocean"
            ]
        }
    ],
    "History": [
        {
            "question": "In what year did the Berlin Wall fall?",
            "answer": "1989",
            "notes": "",
            "sources": [
                "https://www.britannica.com/event/Berlin-Wall",
                "https://www.history.com/topics/cold-war/berlin-wall"
            ]
        },
        {
            "question": "Who was the British Prime Minister for most of World War II?",
            "answer": "Winston Churchill",
            "notes": "",
            "sources": [
                "https://www.britannica.com/biography/Winston-Churchill",
                "https://www.iwm.org.uk/history/winston-churchill"
            ]
        },
        {
            "question": "Which civilization built Machu Picchu?",
            "answer": "The Inca",
            "notes": "",
            "sources": [
                "https://www.britannica.com/place/Machu-Picchu",
                "https://whc.unesco.org/en/list/274/"
            ]
        },
        {
            "question": "Who wrote the Declaration of Independence?",
            "answer": "Thomas Jefferson was the principal author",
            "notes": "",
            "sources": [
                "https://www.archives.gov/founding-docs/declaration-history",
                "https://www.britannica.com/topic/Declaration-of-Independence"
            ]
        }
    ],
    "American Current Events": [
        {
            "question": "How long is a term for a member of the U.S. House of Representatives?",
            "answer": "Two years",
            "notes": "Stable civic-knowledge fallback suitable when live current-events feeds are not used.",
            "sources": [
                "https://www.house.gov/the-house-explained",
                "https://www.usa.gov/branches-of-government"
            ]
        },
        {
            "question": "What is the official residence of the President of the United States?",
            "answer": "The White House",
            "notes": "",
            "sources": [
                "https://www.whitehouse.gov/about-the-white-house/",
                "https://www.britannica.com/topic/White-House"
            ]
        },
        {
            "question": "Which branch of the U.S. government interprets laws?",
            "answer": "The Judicial Branch",
            "notes": "",
            "sources": [
                "https://www.usa.gov/branches-of-government",
                "https://www.supremecourt.gov/about/constitutional.aspx"
            ]
        },
        {
            "question": "How many voting members are in the U.S. House of Representatives?",
            "answer": "435",
            "notes": "",
            "sources": [
                "https://www.house.gov/the-house-explained",
                "https://www.census.gov/topics/public-sector/congressional-apportionment/about.html"
            ]
        }
    ],
    "World Current Events": [
        {
            "question": "In what city is the headquarters of the United Nations located?",
            "answer": "New York City",
            "notes": "",
            "sources": [
                "https://www.un.org/en/about-us/un-headquarters",
                "https://www.britannica.com/topic/United-Nations"
            ]
        },
        {
            "question": "What organization is abbreviated WHO?",
            "answer": "World Health Organization",
            "notes": "",
            "sources": [
                "https://www.who.int/about",
                "https://www.britannica.com/topic/World-Health-Organization"
            ]
        },
        {
            "question": "What currency is used by many member states of the European Union?",
            "answer": "The euro",
            "notes": "",
            "sources": [
                "https://european-union.europa.eu/institutions-law-budget/euro_en",
                "https://www.ecb.europa.eu/euro/html/index.en.html"
            ]
        },
        {
            "question": "What is the name of the international court based in The Hague that settles legal disputes between states?",
            "answer": "The International Court of Justice",
            "notes": "",
            "sources": [
                "https://www.icj-cij.org/home",
                "https://www.un.org/en/icj/"
            ]
        }
    ],
    "Health": [
        {
            "question": "How many chambers does the human heart have?",
            "answer": "Four",
            "notes": "",
            "sources": [
                "https://medlineplus.gov/ency/anatomyvideos/000087.htm",
                "https://my.clevelandclinic.org/health/body/21704-heart"
            ]
        },
        {
            "question": "Which vitamin is primarily produced when skin is exposed to sunlight?",
            "answer": "Vitamin D",
            "notes": "",
            "sources": [
                "https://ods.od.nih.gov/factsheets/VitaminD-Consumer/",
                "https://medlineplus.gov/vitamind.html"
            ]
        },
        {
            "question": "The femur is a bone found in what part of the body?",
            "answer": "The thigh or upper leg",
            "notes": "",
            "sources": [
                "https://my.clevelandclinic.org/health/body/23303-femur",
                "https://www.britannica.com/science/femur"
            ]
        },
        {
            "question": "What blood type is often called the universal donor for red blood cells?",
            "answer": "O negative",
            "notes": "",
            "sources": [
                "https://www.redcrossblood.org/donate-blood/blood-types.html",
                "https://www.nhlbi.nih.gov/health/blood-transfusion"
            ]
        }
    ],
    "Movies": [
        {
            "question": "Who directed the movie 'Jaws'?",
            "answer": "Steven Spielberg",
            "notes": "",
            "sources": [
                "https://www.britannica.com/topic/Jaws-film-by-Spielberg",
                "https://www.imdb.com/title/tt0073195/"
            ]
        },
        {
            "question": "Which film won the Academy Award for Best Picture for films released in 1994?",
            "answer": "Forrest Gump",
            "notes": "",
            "sources": [
                "https://www.oscars.org/oscars/ceremonies/1995",
                "https://www.britannica.com/topic/Forrest-Gump-film"
            ]
        },
        {
            "question": "What film is widely listed as the highest-grossing film worldwide without adjusting for inflation?",
            "answer": "Avatar",
            "notes": "This can change over time depending on re-releases; verify before use if desired.",
            "sources": [
                "https://www.boxofficemojo.com/chart/top_lifetime_gross/",
                "https://www.the-numbers.com/box-office-records/worldwide/all-movies/cumulative/all-time"
            ]
        },
        {
            "question": "In 'The Wizard of Oz,' what road does Dorothy follow?",
            "answer": "The Yellow Brick Road",
            "notes": "",
            "sources": [
                "https://www.britannica.com/topic/The-Wizard-of-Oz-film-by-Fleming",
                "https://www.imdb.com/title/tt0032138/"
            ]
        }
    ],
    "Television": [
        {
            "question": "What coffee shop do the characters frequently visit in 'Friends'?",
            "answer": "Central Perk",
            "notes": "",
            "sources": [
                "https://www.imdb.com/title/tt0108778/",
                "https://friends.fandom.com/wiki/Central_Perk"
            ]
        },
        {
            "question": "Which television series featured the character Don Draper?",
            "answer": "Mad Men",
            "notes": "",
            "sources": [
                "https://www.britannica.com/topic/Mad-Men",
                "https://www.imdb.com/title/tt0804503/"
            ]
        },
        {
            "question": "In the U.S. version of 'The Office,' in what Pennsylvania city is the branch located?",
            "answer": "Scranton",
            "notes": "",
            "sources": [
                "https://www.imdb.com/title/tt0386676/",
                "https://theoffice.fandom.com/wiki/Scranton"
            ]
        },
        {
            "question": "What is the name of the fictional continent where much of 'Game of Thrones' takes place?",
            "answer": "Westeros",
            "notes": "",
            "sources": [
                "https://www.hbo.com/game-of-thrones",
                "https://gameofthrones.fandom.com/wiki/Westeros"
            ]
        }
    ],
    "US Constitution": [
        {
            "question": "How many amendments does the U.S. Constitution have?",
            "answer": "27",
            "notes": "",
            "sources": [
                "https://www.archives.gov/founding-docs/amendments-11-27",
                "https://constitution.congress.gov/constitution/"
            ]
        },
        {
            "question": "Which amendment protects freedom of speech?",
            "answer": "The First Amendment",
            "notes": "",
            "sources": [
                "https://constitution.congress.gov/constitution/amendment-1/",
                "https://www.archives.gov/founding-docs/bill-of-rights-transcript"
            ]
        },
        {
            "question": "Which amendment protects against self-incrimination?",
            "answer": "The Fifth Amendment",
            "notes": "",
            "sources": [
                "https://constitution.congress.gov/constitution/amendment-5/",
                "https://www.law.cornell.edu/constitution/fifth_amendment"
            ]
        },
        {
            "question": "How many senators does each state have in the U.S. Senate?",
            "answer": "Two",
            "notes": "",
            "sources": [
                "https://www.senate.gov/about/origins-foundations/senate-and-constitution/constitution.htm",
                "https://constitution.congress.gov/constitution/article-1/"
            ]
        }
    ],
    "Sports History": [
        {
            "question": "Who was the first person to run a mile in under four minutes?",
            "answer": "Roger Bannister",
            "notes": "",
            "sources": [
                "https://www.britannica.com/biography/Roger-Bannister",
                "https://www.worldathletics.org/heritage/news/roger-bannister-sub-four-minute-mile-anniversary"
            ]
        },
        {
            "question": "Which boxer was known as 'The Greatest'?",
            "answer": "Muhammad Ali",
            "notes": "",
            "sources": [
                "https://www.britannica.com/biography/Muhammad-Ali-boxer",
                "https://www.ali.com/"
            ]
        },
        {
            "question": "In what year were the first modern Olympic Games held?",
            "answer": "1896",
            "notes": "",
            "sources": [
                "https://olympics.com/ioc/ancient-olympic-games/the-modern-games",
                "https://www.britannica.com/sports/Olympic-Games"
            ]
        },
        {
            "question": "What baseball player broke Major League Baseball's color barrier in 1947?",
            "answer": "Jackie Robinson",
            "notes": "",
            "sources": [
                "https://www.britannica.com/biography/Jackie-Robinson",
                "https://www.mlb.com/jackie-robinson"
            ]
        }
    ],
    "Sports Current Events": [
        {
            "question": "How many points is a touchdown worth in American football before the extra point attempt?",
            "answer": "6",
            "notes": "Reliable fallback sports rules question.",
            "sources": [
                "https://operations.nfl.com/learn-the-game/nfl-basics/",
                "https://www.britannica.com/sports/gridiron-football"
            ]
        },
        {
            "question": "In golf, what term means one stroke under par on a hole?",
            "answer": "Birdie",
            "notes": "",
            "sources": [
                "https://www.usga.org/content/usga/home-page/rules-hub/topics/golf-glossary.html",
                "https://www.britannica.com/sports/golf"
            ]
        },
        {
            "question": "How many players from one team are on the court at one time in an NBA game?",
            "answer": "5",
            "notes": "",
            "sources": [
                "https://official.nba.com/rule-no-1-court-dimensions-equipment/",
                "https://www.britannica.com/sports/basketball"
            ]
        },
        {
            "question": "How many innings are in a regulation Major League Baseball game, unless extra innings are required?",
            "answer": "9 innings",
            "notes": "",
            "sources": [
                "https://www.mlb.com/glossary/rules/regulation-game",
                "https://www.britannica.com/sports/baseball"
            ]
        }
    ],
    "World Records": [
        {
            "question": "Who holds the men's 100-meter world record?",
            "answer": "Usain Bolt",
            "notes": "",
            "sources": [
                "https://worldathletics.org/records/by-discipline/sprints/100-metres/outdoor/men",
                "https://www.britannica.com/biography/Usain-Bolt"
            ]
        },
        {
            "question": "What is the tallest mountain above sea level in the world?",
            "answer": "Mount Everest",
            "notes": "",
            "sources": [
                "https://www.britannica.com/place/Mount-Everest",
                "https://education.nationalgeographic.org/resource/mount-everest/"
            ]
        },
        {
            "question": "What is the largest desert in the world, including polar deserts?",
            "answer": "Antarctica",
            "notes": "A good trivia twist because many people guess the Sahara.",
            "sources": [
                "https://www.britannica.com/place/Antarctica",
                "https://education.nationalgeographic.org/resource/deserts/"
            ]
        },
        {
            "question": "Which animal is the tallest on Earth?",
            "answer": "The giraffe",
            "notes": "",
            "sources": [
                "https://nationalzoo.si.edu/animals/giraffe",
                "https://www.britannica.com/animal/giraffe"
            ]
        }
    ],
    "Name That Tune": [
        {
            "question": "Name That Tune: Play the opening of this song.",
            "answer": "Billie Jean",
            "notes": "Accept song title. Optionally accept artist if your house rules allow.",
            "song": "Billie Jean",
            "writers": "Michael Jackson",
            "performer": "Michael Jackson",
            "release_date": "January 2, 1983",
            "clip_length": "5 seconds",
            "sources": [
                "https://www.britannica.com/topic/Billie-Jean",
                "https://www.songhall.org/profile/Michael_Jackson",
                "https://www.discogs.com/master/51993-Michael-Jackson-Billie-Jean"
            ]
        },
        {
            "question": "Name That Tune: Play the opening of this song.",
            "answer": "Bohemian Rhapsody",
            "notes": "Accept song title.",
            "song": "Bohemian Rhapsody",
            "writers": "Freddie Mercury",
            "performer": "Queen",
            "release_date": "October 31, 1975",
            "clip_length": "4 seconds",
            "sources": [
                "https://www.britannica.com/topic/Bohemian-Rhapsody-song-by-Queen",
                "https://www.queenonline.com/",
                "https://www.discogs.com/master/5274-Queen-Bohemian-Rhapsody"
            ]
        },
        {
            "question": "Name That Tune: Play the opening of this song.",
            "answer": "I Will Always Love You",
            "notes": "Accept song title. This version refers to the best-known Whitney Houston recording.",
            "song": "I Will Always Love You",
            "writers": "Dolly Parton",
            "performer": "Whitney Houston",
            "release_date": "November 3, 1992",
            "clip_length": "6 seconds",
            "sources": [
                "https://www.britannica.com/topic/I-Will-Always-Love-You-song",
                "https://www.songhall.org/profile/Dolly_Parton",
                "https://www.discogs.com/master/79719-Whitney-Houston-I-Will-Always-Love-You"
            ]
        },
        {
            "question": "Name That Tune: Play the opening of this song.",
            "answer": "Hey Ya!",
            "notes": "Accept song title.",
            "song": "Hey Ya!",
            "writers": "André 3000",
            "performer": "Outkast",
            "release_date": "September 9, 2003",
            "clip_length": "3 seconds",
            "sources": [
                "https://www.britannica.com/topic/Outkast",
                "https://www.discogs.com/master/103780-Outkast-Hey-Ya",
                "https://www.songhall.org/profile/andre_3000"
            ]
        },
        {
            "question": "Name That Tune: Play the opening of this song.",
            "answer": "Sweet Caroline",
            "notes": "Accept song title.",
            "song": "Sweet Caroline",
            "writers": "Neil Diamond",
            "performer": "Neil Diamond",
            "release_date": "May 28, 1969",
            "clip_length": "5 seconds",
            "sources": [
                "https://www.britannica.com/biography/Neil-Diamond",
                "https://www.discogs.com/master/547163-Neil-Diamond-Sweet-Caroline-Good-Times-Never-Seemed-So-Good",
                "https://www.songhall.org/profile/neil_diamond"
            ]
        }
    ]
}

# =========================================================
# WORD SCRAMBLE BANK
# 7-11 letters, vague clue, sources included
# =========================================================
WORD_SCRAMBLE_BANK = [
    {
        "word": "TREASURE",
        "clue": "Something worth keeping safe",
        "sources": [
            "https://www.merriam-webster.com/dictionary/treasure"
        ]
    },
    {
        "word": "ATHLETIC",
        "clue": "Related to sports or physical skill",
        "sources": [
            "https://www.merriam-webster.com/dictionary/athletic"
        ]
    },
    {
        "word": "HORIZONS",
        "clue": "What may broaden when you learn more",
        "sources": [
            "https://www.merriam-webster.com/dictionary/horizon"
        ]
    },
    {
        "word": "LANDMARK",
        "clue": "A notable point of reference",
        "sources": [
            "https://www.merriam-webster.com/dictionary/landmark"
        ]
    },
    {
        "word": "JUDICIAL",
        "clue": "Connected to courts or judges",
        "sources": [
            "https://www.merriam-webster.com/dictionary/judicial"
        ]
    },
    {
        "word": "PLAYBOOK",
        "clue": "A set of planned actions",
        "sources": [
            "https://www.merriam-webster.com/dictionary/playbook"
        ]
    },
    {
        "word": "HEADLINE",
        "clue": "Something that catches public attention",
        "sources": [
            "https://www.merriam-webster.com/dictionary/headline"
        ]
    },
    {
        "word": "NOTEBOOK",
        "clue": "A place to keep ideas",
        "sources": [
            "https://www.merriam-webster.com/dictionary/notebook"
        ]
    },
    {
        "word": "CHAMPION",
        "clue": "A winner at the highest level",
        "sources": [
            "https://www.merriam-webster.com/dictionary/champion"
        ]
    },
    {
        "word": "ELECTION",
        "clue": "A public choice process",
        "sources": [
            "https://www.merriam-webster.com/dictionary/election"
        ]
    }
]

# =========================================================
# HELPERS
# =========================================================
def shuffle_word(word):
    chars = list(word)
    original = chars[:]
    while True:
        random.shuffle(chars)
        if chars != original:
            return "".join(chars)

def generate_word_scramble_entry():
    entry = random.choice(WORD_SCRAMBLE_BANK)
    scrambled = shuffle_word(entry["word"])
    return {
        "category": "Word Scramble",
        "question": f"Unscramble this {len(entry['word'])}-letter word: {scrambled}",
        "answer": entry["word"],
        "notes": f"Vague clue: {entry['clue']}",
        "sources": entry["sources"]
    }

def normalize_question(category, entry):
    if category == "Name That Tune":
        return {
            "category": "Name That Tune",
            "question": entry["question"],
            "answer": entry["answer"],
            "notes": entry.get("notes", ""),
            "sources": entry.get("sources", []),
            "song": entry.get("song", ""),
            "writers": entry.get("writers", ""),
            "performer": entry.get("performer", ""),
            "release_date": entry.get("release_date", ""),
            "clip_length": entry.get("clip_length", "")
        }

    return {
        "category": category,
        "question": entry["question"],
        "answer": entry["answer"],
        "notes": entry.get("notes", ""),
        "sources": entry.get("sources", [])
    }

def get_random_question(category, exclude_question=None):
    if category == "Word Scramble":
        candidate = generate_word_scramble_entry()
        if exclude_question and candidate["question"] == exclude_question:
            return generate_word_scramble_entry()
        return candidate

    entries = QUESTION_BANK.get(category, [])
    if not entries:
        return {
            "category": category,
            "question": f"Placeholder question for {category}",
            "answer": "TBD",
            "notes": "",
            "sources": ["Source needed"]
        }

    candidates = entries[:]
    random.shuffle(candidates)
    for entry in candidates:
        q = normalize_question(category, entry)
        if exclude_question is None or q["question"] != exclude_question:
            return q

    return normalize_question(category, random.choice(entries))

def safe_pick_categories(pool, count):
    result = []
    working = pool[:]
    while len(result) < count:
        if not working:
            working = pool[:]
        random.shuffle(working)
        result.append(working.pop())
    return result

def generate_game_1():
    category_pool = [
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

    rounds = []
    for round_num in range(1, 4):
        categories = safe_pick_categories(category_pool, 10)
        questions = [get_random_question(cat) for cat in categories]
        rounds.append({
            "round_name": f"Round {round_num}",
            "questions": questions
        })
    return rounds

def generate_game_2():
    fixed = ["Name That Tune", "Name That Tune", "Word Scramble", "Word Scramble"]
    others_pool = [
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
    others = safe_pick_categories(others_pool, 11)
    all_categories = fixed + others
    random.shuffle(all_categories)
    questions = [get_random_question(cat) for cat in all_categories]

    return [{
        "round_name": "Game 2 - Single Round",
        "questions": questions
    }]

def export_payload(game1, game2):
    return json.dumps({
        "title": "Trivia with the GM",
        "generated_at": datetime.now().isoformat(),
        "game_1": game1,
        "game_2": game2
    }, indent=2)

def init_state():
    if "game1" not in st.session_state:
        st.session_state.game1 = []
    if "game2" not in st.session_state:
        st.session_state.game2 = []

init_state()

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
st.sidebar.markdown("### Tips")
st.sidebar.markdown("""
- Use **Generate Both Games** to create a full event.
- Use **Replace This Question** if you do not like a question.
- You may manually edit any question, answer, notes, or sources.
- For **Name That Tune**, upload/play your own legal audio clip outside this app.
""")

# =========================================================
# RENDER HELPERS
# =========================================================
def render_sources_editor(q, prefix):
    existing_sources = q.get("sources", [])
    sources_text = "\n".join(existing_sources)
    updated = st.text_area(
        "Sources (one per line)",
        value=sources_text,
        key=f"{prefix}_sources",
        height=100
    )
    q["sources"] = [line.strip() for line in updated.split("\n") if line.strip()]

def render_name_that_tune_fields(q, prefix):
    st.markdown("#### Name That Tune Details")
    q["song"] = st.text_input("Song", value=q.get("song", ""), key=f"{prefix}_song")
    q["writers"] = st.text_input("Writer(s)", value=q.get("writers", ""), key=f"{prefix}_writers")
    q["performer"] = st.text_input("Best Known Performer", value=q.get("performer", ""), key=f"{prefix}_performer")
    q["release_date"] = st.text_input("Release Date of Best Known Release", value=q.get("release_date", ""), key=f"{prefix}_release_date")
    q["clip_length"] = st.text_input("Recommended Intro Clip Length", value=q.get("clip_length", ""), key=f"{prefix}_clip_length")

def replace_question(game_key, round_index, question_index):
    target_game = st.session_state[game_key]
    q = target_game[round_index]["questions"][question_index]
    category = q["category"]
    current_question = q["question"]
    new_q = get_random_question(category, exclude_question=current_question)
    target_game[round_index]["questions"][question_index] = new_q

def render_round(round_data, round_index, game_key):
    st.markdown(f"## {round_data['round_name']}")
    for q_idx, q in enumerate(round_data["questions"]):
        with st.expander(f"Q{q_idx + 1}: {q['category']}", expanded=False):
            prefix = f"{game_key}_{round_index}_{q_idx}"

            c1, c2 = st.columns([4, 1])
            with c1:
                q["category"] = st.text_input("Category", value=q["category"], key=f"{prefix}_category")
            with c2:
                if st.button("🔄 Replace This Question", key=f"{prefix}_replace"):
                    replace_question(game_key, round_index, q_idx)
                    st.rerun()

            q["question"] = st.text_area("Question", value=q["question"], key=f"{prefix}_question", height=100)
            q["answer"] = st.text_input("Answer", value=q["answer"], key=f"{prefix}_answer")
            q["notes"] = st.text_area("Host Notes", value=q.get("notes", ""), key=f"{prefix}_notes", height=80)

            if q["category"] == "Name That Tune":
                render_name_that_tune_fields(q, prefix)

            render_sources_editor(q, prefix)

            show_answer = st.checkbox("Reveal answer", key=f"{prefix}_reveal")
            if show_answer:
                st.success(f"Answer: {q['answer']}")
                if q.get("notes"):
                    st.info(f"Notes: {q['notes']}")
                if q.get("category") == "Name That Tune":
                    st.write(f"**Song:** {q.get('song', '')}")
                    st.write(f"**Writer(s):** {q.get('writers', '')}")
                    st.write(f"**Best Known Performer:** {q.get('performer', '')}")
                    st.write(f"**Release Date:** {q.get('release_date', '')}")
                    st.write(f"**Recommended Clip Length:** {q.get('clip_length', '')}")

                if q.get("sources"):
                    st.write("**Sources:**")
                    for s in q["sources"]:
                        st.write(f"- {s}")

def print_view(rounds, title):
    st.markdown(f"# {title}")
    for rnd in rounds:
        st.markdown(f"## {rnd['round_name']}")
        for i, q in enumerate(rnd["questions"], start=1):
            st.markdown(f"### {i}. [{q['category']}]")
            st.markdown(q["question"])
            st.markdown(f"**Answer:** {q['answer']}")
            if q.get("notes"):
                st.markdown(f"**Host Notes:** {q['notes']}")

            if q.get("category") == "Name That Tune":
                st.markdown(f"**Song:** {q.get('song', '')}")
                st.markdown(f"**Writer(s):** {q.get('writers', '')}")
                st.markdown(f"**Best Known Performer:** {q.get('performer', '')}")
                st.markdown(f"**Release Date:** {q.get('release_date', '')}")
                st.markdown(f"**Recommended Intro Clip Length:** {q.get('clip_length', '')}")

            if q.get("sources"):
                st.markdown("**Sources:**")
                for s in q["sources"]:
                    st.markdown(f"- {s}")
            st.markdown("---")

# =========================================================
# MAIN TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs(["Game 1", "Game 2", "Export", "Instructions"])

with tab1:
    st.header("Game 1: 3 Rounds × 10 Questions")
    if not st.session_state.game1:
        st.info("Use the sidebar and click 'Generate Game 1' or 'Generate Both Games'.")
    else:
        for r_idx, rnd in enumerate(st.session_state.game1):
            render_round(rnd, r_idx, "game1")

with tab2:
    st.header("Game 2: 1 Round × 15 Questions")
    st.caption("Includes 2 Name That Tune and 2 Word Scramble questions.")
    if not st.session_state.game2:
        st.info("Use the sidebar and click 'Generate Game 2' or 'Generate Both Games'.")
    else:
        for r_idx, rnd in enumerate(st.session_state.game2):
            render_round(rnd, r_idx, "game2")

with tab3:
    st.header("Export / Print")
    if st.session_state.game1 or st.session_state.game2:
        payload = export_payload(st.session_state.game1, st.session_state.game2)
        st.download_button(
            "Download Trivia JSON",
            data=payload,
            file_name="trivia_with_the_gm.json",
            mime="application/json"
        )

        st.subheader("Host Print View")
        if st.session_state.game1:
            print_view(st.session_state.game1, "Game 1")
        if st.session_state.game2:
            print_view(st.session_state.game2, "Game 2")
    else:
        st.info("Generate at least one game first.")

with tab4:
    st.header("How to Use This App")
    st.markdown("""
### Before Trivia Night
1. Click **Generate Both Games**
2. Review the questions
3. If you do not like a question, click **Replace This Question**
4. Edit wording if needed
5. For **Name That Tune**, prepare your own legal song clips separately
6. Use the **Export** tab to print or download your set

### About Sources
- Every starter question includes at least one source
- You can edit or add sources manually
- For time-sensitive facts, re-check sources before your event

### About Name That Tune
This app stores:
- Song
- Writer(s)
- Best known performer
- Release date
- Recommended clip length

You should play your own legally obtained clip during the event.
""")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("Trivia with the GM • Streamlit app for country club trivia hosting")
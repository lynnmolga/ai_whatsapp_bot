import re
from difflib import SequenceMatcher
import requests
from app.config import EXAMPLES_PATH
from app.storage import read_jsonl

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "aminadaven/dictalm2.0-instruct:q4_k_m"

BANNED_WORDS = [
    "מצטערת",
    "מתנצלת",
    "סליחה",
    "[שם]",
    "בהקדם האפשרי",
    "בהקדם",
    "נדבר בקרוב",
    "רק רוצה להגיד",
    "אני צריך",
    "אנחנו",
    "אליכם",
    "אלינו",
    "בהזדמנות אחרת",
    "מה לגבי",
    "אני אשמח",
    "מה איתך"
]


def is_valid_reply(reply: str) -> bool:
    if "?" in reply:
        return False
    if any(phrase in reply for phrase in BANNED_WORDS):
        return False
    return True


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def load_relevant_examples(message: str, intent: str, limit: int = 5) -> str:
    examples = read_jsonl(EXAMPLES_PATH)
    scored = []
    for ex in examples:
        ex_type = ex.get("type", "")
        ex_incoming = ex.get("incoming", "")
        score = similarity(message, ex_incoming)
        if ex_type == intent:
            score += 0.6
        scored.append((score, ex))
    top_examples = [
        ex for _, ex in sorted(scored, key=lambda x: x[0], reverse=True)[:limit]
    ]
    formatted = []
    for ex in top_examples:
        formatted.append(
            f"הודעה: {ex['incoming']}\n"
            f"לין ענתה: {ex['reply']}"
        )
    return "\n\n".join(formatted)


def classify_risk(message: str) -> str:
    risky_words = [
        "emergency", "hospital", "money", "bank", "password",
        "urgent", "hurt", "accident",
        "בית חולים", "כסף", "בנק", "סיסמה", "דחוף", "תאונה",
        "קרה משהו", "פצוע", "מיון",
    ]
    lowered = message.lower()
    if any(word in lowered for word in risky_words):
        return "sensitive"
    return "safe"


def classify_sender(sender: str) -> str:
    s = sender.lower().strip()
    mom_words = ["mom", "mother", "אמא", "אמא שלי", "מאמי"]
    partner_words = ["partner", "boyfriend", "girlfriend", "בן זוג", "בת זוג", "אור"]
    friend_words = ["friend", "חבר", "חברה", "רוני", "שהם", "תמר"]
    if any(word in s for word in mom_words):
        return "mom"
    if any(word in s for word in partner_words):
        return "partner"
    if any(word in s for word in friend_words):
        return "friend"
    return "general"


def get_tone_for_sender(sender_type: str) -> str:
    tones = {
        "mom": (
            "טון רך ומרגיע. להוריד דאגה. אפשר להיות קצת יותר חמה, "
            "אבל לא להמציא עובדות כמו אכלתי או אני בדרך"
        ),
        "partner": (
            "טון קרוב ואוהב, טבעי וקצת חם. קצר, לא דרמטי, לא רשמי."
        ),
        "friend": (
            "טון קליל, ישיר, קצת מצחיק אם מתאים. לא רשמי בכלל."
        ),
        "general": (
            "טון קצר, טבעי וישיר. לא רשמי ולא מתאמץ."
        ),
    }
    return tones.get(sender_type, tones["general"])

def fallback_reply(intent: str) -> str:
    fallbacks = {
        "general": "הכל טוב פשוט קצת עמוסה :)",
        "worried": "הכל בסדר פשוט קצת עסוקה :)",
        "mom": "אני בסדר עסוקה קצת :) אחזור אליך",
        "location": "לא יודעת עדיין אעדכן",
        "pushy": "יום עמוס אחזור אליך מאוחר יותר",
        "invite": "אוף לא יכולה היום אולי מחר",
        "call": "לא יכולה עכשיו אחזור אלייך אחר כך",
        "short": "פה פשוט עסוקה רגע",
    }
    return fallbacks.get(intent, "הכל טוב פשוט קצת עמוסה")

def classify_intent(message: str, sender: str) -> str:
    text = message.lower().strip()
    stop_words = [
        "טוב",
        "סבבה",
        "אוקיי",
        "אוקי",
        "אין בעיה",
        "נדבר אחרי",
        "נדבר אחר כך",
        "תתקשרי אחרי",
        "תתקשרי אליי אחרי",
        "יאללה",
        "מעולה",
        "אחלה",
        "בסדר",
        "קבענו"
    ]
    if text in stop_words:
        return "stop"
    if any(text.startswith(word) for word in stop_words):
        return "stop"
    food_words = [
        "אכלת", "אוכל", "לאכול", "תאכלי", "שתית", "מים",
    ]
    worry_words = [
        "הכל בסדר", "את בסדר", "דואגת", "דאגתי", "קרה משהו",
        "למה את לא עונה", "איפה את", "את חיה",
    ]
    location_words = [
        "מתי את מגיעה", "מתי תהיי", "מתי בבית", "את בדרך",
        "איפה את עכשיו", "מתי את חוזרת", "איפה"
    ]
    pressure_words = [
        "נו", "תעני", "כבר", "מסננת", "טוב תודה באמת",
        "מה נסגר",
    ]
    invite_words = [
        "בואי", "נצא", "נפגש", "יוצאים", "לצאת", "קפה",
        "בירה", "היום בערב", "זורמת",
    ]
    call_words = [
        "שיחה", "לדבר", "תתקשרי", "אפשר לדבר", "יש לך דקה",
        "call me", "can you talk",
    ]
    short_ping = ["?", "היי", "נו", "איפה"]
    if any(word in text for word in food_words):
        return "mom"
    if any(word in text for word in worry_words):
        return "worried"
    if any(word in text for word in location_words):
        return "location"
    if any(word in text for word in pressure_words):
        return "pushy"
    if any(word in text for word in invite_words):
        return "invite"
    if any(word in text for word in call_words):
        return "call"
    if text in short_ping or len(text) <= 3:
        return "short"
    if "מה איתך" in text or "מה שלומך" in text:
        return "general"
    return "general"


def get_task_for_intent(intent: str, risk: str) -> str:
    if risk == "sensitive":
        return (
            "לא לענות לתוכן עצמו. רק להגיד שלין ראתה את ההודעה, "
            "שהיא לא זמינה כרגע, ושתחזור לזה כשתוכל."
        )
    tasks = {
        "worried": (
            "להרגיע שהכל בסדר ולהגיד שלין עסוקה או לא זמינה כרגע."
        ),
        "mom": (
            "להרגיע בלי להמציא עובדות. לא סתם להגיד שדברים קרו"
        ),
        "location": (
            "לא להמציא מיקום או זמן הגעה. להגיד שלא יודעת או שתעדכן אחר כך."
        ),
        "pushy": (
            "לענות קליל, לא מתגונן, ולהבהיר שלין לא מסננת אלא עסוקה."
        ),
        "invite": (
        "להגיב להזמנה קצר וקליל. לרוב לדחות או לסרב. "
        "אפשר להציע מחר או יום אחר. לא להסביר למה."
        ),
        "call": (
            "להגיד שלין לא יכולה לדבר כרגע ותחזור לזה כשיתאפשר."
        ),
        "short": (
            "לענות ממש קצר, כאילו לין עסוקה אבל ראתה את ההודעה."
        ),
        "general": (
            "לענות קצר וטבעי כאילו לין עסוקה ולא זמינה כרגע."
        ),
    }
    return tasks.get(intent, tasks["general"])


def clean_output(text: str) -> str:
    for word in BANNED_WORDS:
        text = text.replace(word, "")
    text = re.sub(r"\(\d+\s*מילים\)", "", text)
    text = re.sub(r"[\"']", "", text)
    text = text.replace(".", "")
    text = text.replace("!", "")
    text = text.replace(",", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_replies(text: str) -> list[str]:
    text = text.strip()
    parts = re.split(r"(?:^|\s)(\d+)[\.\)]?\s+", text)
    replies = []
    for i in range(1, len(parts), 2):
        reply = parts[i + 1].strip()
        if reply:
            replies.append(reply)
    return replies[:3]


def score_reply(reply: str, intent: str) -> int:
    score = 0
    words = reply.split()
    if 3 <= len(words) <= 10:
        score += 3
    elif len(words) <= 14:
        score += 1
    else:
        score -= 3

    hallucination_phrases = [
        "אני בדרך",
        "אני אוכלת",
        "אני אוכל",
        "אני מתקשרת",
        "אני אתקשר",
        "אכלתי",
        # "עוד כמה דקות",
        # "בקרוב",
    ]
    if any(phrase in reply for phrase in hallucination_phrases):
        score -= 5

    formal_phrases = [
        "בהזדמנות אחרת",
        "בהקדם",
        "מתנצלת",
        "מצטערת",
        "סליחה",
        "אשמח",
        "התחייבות",
        "כרגע"
    ]
    if any(phrase in reply for phrase in formal_phrases):
        score -= 4
    if intent == "invite":
        if any(word in reply for word in ["מחר", "יום אחר", "לא היום", "לא אספיק"]):
            score += 3
        if any(word in reply for word in ["יש לי", "אני עסוקה היום"]):
            score -= 2
    if intent == "worried":
        if any(word in reply for word in ["הכל בסדר", "הכל טוב", "אני בסדר"]):
            score += 3
    if intent == "mom":
        if any(word in reply for word in ["אל תדאגי", "הכל טוב", "הכל בסדר"]):
            score += 3
    if intent == "location":
        if any(word in reply for word in ["לא יודעת", "לא בטוחה", "אעדכן"]):
            score += 3
        if any(word in reply for word in ["אני בדרך", "מגיעה עוד"]):
            score -= 5
    return score


def choose_best_reply(draft: str, intent: str) -> str:
    replies = split_replies(draft)
    replies = [clean_output(r) for r in replies if r.strip()]
    valid = [r for r in replies if is_valid_reply(r)]
    if not valid:
        return fallback_reply(intent)
    best = max(valid, key=lambda r: score_reply(r, intent))
    return best.strip()


def generate_draft(sender: str, message: str) -> dict:
    risk = classify_risk(message)
    intent = classify_intent(message, sender)
    best_reply = ""
    draft = ""
    if intent == "stop":
        return {
            "sender": sender,
            "incoming": message,
            "risk": risk,
            "intent": intent,
            "sender_type": classify_sender(sender),
            "should_reply": False,
            "draft": "",
        }
    sender_type = classify_sender(sender)
    tone = get_tone_for_sender(sender_type)
    task = get_task_for_intent(intent, risk)
    examples = load_relevant_examples(message=message, intent=intent, limit=5)
    prompt = f"""
    את כותבת 3 טיוטות קצרות לתשובת וואטסאפ בשם לין.

    לין היא אישה. לענות תמיד בלשון נקבה יחידה.

    ההודעה:
    {message}
    סוג ההודעה:
    {intent}
    המטרה:
    {task}
    טון:
    {tone}
    דוגמאות אמיתיות של לין. צריך לחקות את סגנון הדיבור:
    {examples} 
    חוקים:
    - עברית בלבד
    - אם יש סתירה בין החוקים לבין הדוגמאות, ללכת לפי הדוגמאות
    - קצר וטבעי כמו בוואטסאפ
    - לחקות את הסגנון בדוגמאות בלי להעתיק אותן
    - לא לשאול שאלות
    - לא להשתמש במרכאות או בסוגריים
    - לא להמציא עובדות: לא להגיד שאכלתי, שאני בדרך או שאתקשר
    - לא לשאול שאלות
    - לא להשתמש במרכאות או בסוגריים
    - לא להמציא עובדות: לא להגיד שאכלתי, שאני בדרך, או שאתקשר
    - אם אין מידע, לענות כללי ומרגיע
    - בהזמנות: לענות קליל, אפשר להציע מחר/יום אחר
    - לא להסביר למה
    - לא להשתמש במילים רשמיות או מתנצלות

    פלט:
    1.
    2.
    3.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 120,
                },
            },
            timeout=240,
        )
        response.raise_for_status()
        result = response.json()
        raw_draft = result.get("response", "No response from model")
        best_reply = choose_best_reply(raw_draft, intent)
        draft = clean_output(raw_draft)
    except Exception as e:
        draft = f"Ollama error: {type(e).__name__}: {e}"

    return {
        "sender": sender,
        "incoming": message,
        "risk": risk,
        "intent": intent,
        "sender_type": sender_type,
        "should_reply": True,
        "draft": draft,
        "best_reply": best_reply,
    }

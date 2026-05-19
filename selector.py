from crewai import LLM
from firebase_admin import credentials, firestore
import firebase_admin
import os
import json
import math
from dotenv import load_dotenv

# ── Firebase ─────────────────────────────────────────────
# ── Firebase ─────────────────────────────────────────────
load_dotenv()

firebase_env = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_env:
    raise ValueError("FIREBASE_CREDENTIALS is missing")

firebase_dict = json.loads(firebase_env)

cred = credentials.Certificate(firebase_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ── API KEYS ROTATION ───────────────────────────────────
api_keys = [
    os.getenv("GROQ_API_line_1"),
    os.getenv("GROQ_API_line_2"),
    os.getenv("GROQ_API_line_3"),
    os.getenv("GROQ_API_line_4"),
]

# حذف المفاتيح الفارغة
api_keys = [k for k in api_keys if k]

current_key_index = 0


def get_next_key():
    global current_key_index

    key = api_keys[current_key_index]

    current_key_index = (
        current_key_index + 1
    ) % len(api_keys)

    return key


# ── إنشاء LLM ───────────────────────────────────────────
def create_llm():
    return LLM(
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=get_next_key(),
        temperature=0.3,
        max_tokens=150,
    )


# ── حساب المسافة ────────────────────────────────────────
def filter_lines_by_proximity(
    lat1,
    long1,
    lat2,
    long2,
    threshold=0.05
):
    route_docs = db.collection("routes").stream()

    filtered = []

    for doc in route_docs:
        data = doc.to_dict()

        points = data.get("points", [])

        if not points:
            continue

        has_start = False
        has_end = False

        for p in points:

            plat = p.get("lat") or p.get("latitude", 0)

            plng = p.get("lng") or p.get("longitude", 0)

            dist_start = math.sqrt(
                (lat1 - plat) ** 2 +
                (long1 - plng) ** 2
            )

            dist_end = math.sqrt(
                (lat2 - plat) ** 2 +
                (long2 - plng) ** 2
            )

            if dist_start < threshold:
                has_start = True

            if dist_end < threshold:
                has_end = True

        if has_start and has_end:
            filtered.append(doc.id)

    return filtered


# ── ترتيب الخطوط بدون AI ────────────────────────────────
def rank_lines(
    filtered_lines,
    cost_pref,
    time_pref,
    comfort_pref
):

    # الأوزان
    weights = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    cost_weight = weights.get(cost_pref, 1)

    time_weight = weights.get(time_pref, 1)

    comfort_weight = weights.get(comfort_pref, 1)

    # بيانات الخطوط
    transport_scores = {
        "bus": {
            "cost_rank": 1,
            "time_rank": 4,
            "comfort_rank": 4
        },

        "L12": {
            "cost_rank": 1,
            "time_rank": 4,
            "comfort_rank": 4
        },

        "L36": {
            "cost_rank": 1,
            "time_rank": 4,
            "comfort_rank": 4
        },

        "L58": {
            "cost_rank": 1,
            "time_rank": 4,
            "comfort_rank": 4
        },

        "L89A": {
            "cost_rank": 1,
            "time_rank": 4,
            "comfort_rank": 4
        },

        "L608A": {
            "cost_rank": 1,
            "time_rank": 4,
            "comfort_rank": 4
        },

        "tram": {
            "cost_rank": 2,
            "time_rank": 3,
            "comfort_rank": 3
        },

        "metro": {
            "cost_rank": 3,
            "time_rank": 2,
            "comfort_rank": 2
        },

        "teleferik": {
            "cost_rank": 2,
            "time_rank": 3,
            "comfort_rank": 3
        },

        "taxi": {
            "cost_rank": 4,
            "time_rank": 1,
            "comfort_rank": 1
        }
    }

    ranked = []

    for line in filtered_lines:

        if line not in transport_scores:
            continue

        data = transport_scores[line]

        score = (
            cost_weight * data["cost_rank"]
            +
            time_weight * data["time_rank"]
            +
            comfort_weight * data["comfort_rank"]
        )

        ranked.append({
            "line_name": line,
            "score": score
        })

    ranked.sort(key=lambda x: x["score"])

    return {
        "routes": ranked
    }


# ── MAIN FUNCTION ───────────────────────────────────────
def run_selector(inputs: dict):

    filtered = filter_lines_by_proximity(
        inputs["lat1"],
        inputs["long1"],
        inputs["lat2"],
        inputs["long2"],
        threshold=0.05
    )

    print("✅ Filtered lines:", filtered)

    if not filtered:
        return {
            "routes": [],
            "message": "No lines found"
        }

    result = rank_lines(
        filtered,
        inputs["Cost"],
        inputs["time"],
        inputs["Comfort"]
    )

    return result
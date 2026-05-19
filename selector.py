from firebase_admin import credentials, firestore
import firebase_admin
import os
import json
import math
from dotenv import load_dotenv

# ── ENV ──────────────────────────────────────────────────
load_dotenv()

# ── Firebase ─────────────────────────────────────────────
if not firebase_admin._apps:
    firebase_env = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_env:
        # Vercel: من environment variable
        firebase_dict = json.loads(firebase_env)
        cred = credentials.Certificate(firebase_dict)
    else:
        # Local: من ملف JSON
        cred = credentials.Certificate(
            "transport-assistant-2c59e-firebase-adminsdk-fbsvc-27107e88f9.json"
        )
    firebase_admin.initialize_app(cred)

db = firestore.client()


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

    weights = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    cost_weight    = weights.get(cost_pref, 1)
    time_weight    = weights.get(time_pref, 1)
    comfort_weight = weights.get(comfort_pref, 1)

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
            cost_weight    * data["cost_rank"]
            + time_weight  * data["time_rank"]
            + comfort_weight * data["comfort_rank"]
        )

        ranked.append({
            "line_name": line,
            "score": score
        })

    ranked.sort(key=lambda x: x["score"])

    return {"routes": ranked}


# ── MAIN FUNCTION ───────────────────────────────────────
def run_selector(inputs: dict):

    filtered = filter_lines_by_proximity(
        inputs["lat1"],
        inputs["long1"],
        inputs["lat2"],
        inputs["long2"],
        threshold=0.05
    )

    print("Filtered lines:", filtered)

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
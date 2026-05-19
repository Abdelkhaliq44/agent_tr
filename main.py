# from crewai import LLM ,Agent,Task,Process,Crew
# from crewai.tools import tool
# from dotenv import load_dotenv
# from pydantic import BaseModel, Field  
# from typing import List
# from dotenv import load_dotenv
# from firebase_admin import credentials, firestore
# import agentops
# import os 
# import json
# import firebase_admin
# import requests
# cred = credentials.Certificate("transport-assistant-2c59e-firebase-adminsdk-fbsvc-27107e88f9.json")
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# output_dir ="./ai-agent-output"
# os.makedirs(output_dir,exist_ok=True)
# load_dotenv()
# llm1 = LLM(
#     model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY_1"),
#     temperature=1,
#     max_tokens=8192,
# )

# llm2 = LLM(
#     model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY_2"),
#     temperature=1,
#     max_tokens=8192,
# )

# llm3 = LLM(
#     model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY_3"),
#     temperature=1,
#     max_tokens=8192,
# )

# llm4 = LLM(
#     model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
#     api_key=os.getenv("GROQ_API_KEY_4"),
#     temperature=1,
#     max_tokens=8192,
# )
# # llm4= LLM(
# #     model="gemini/gemini-2.5-flash",
# #     api_key=os.getenv('api_key_llm1'),
# #     temperature=0.7,
# # )
# agentops.init(
#     api_key=os.getenv('agentops_api_key'),
#     skip_auto_end_session=True
# )
# @tool
# def get_faibase(collection_name: str, document_name: str, array_name: str):
#     """
#     Retrieve data from Firebase.
#     array_name: the name of the array to retrieve ('markers' or 'points')
#     """
#     doc_ref = db.collection(collection_name).document(document_name)
#     doc = doc_ref.get()
#     data = doc.to_dict().get(array_name, [])
#     return data
   
# def init_agents_and_crew():

#         #Agent  A" get the  station from fairbase

#         class Station(BaseModel):
#             latitude: float
#             longitude: float

#         class RouteStations(BaseModel):
#             boarding_station: Station
#             dropoff_station: Station
        
#         agent_station_for_Firebase=Agent(
#         name ='agent_station_for_Firebase',
#             role='This agent identifies the nearest station from a list of stations it retrieves from Firebase.',
#             goal= 'Stasio gives rides and Stasio gets down from among the Stasio that it brings from the Firebase, depending on the points it gives.',
#             backstory='This elegant is the first stage of drawing a complete route based on transport lines, where it specifies which station to board and which station to disembark from on the transport line.',
#             llm=llm1,
#             verbose=False,
#             tools=[get_faibase]
#         )
#         task_station_for_Firebase=Task(
#             description="""
#             Use the tool get_faibase with:
#                     collection_name = "routes"
#                     document_name = "{document}"
#                     array_name = "marker"
#                     It brings up all the stations on the line
#                     It receives the person's starting_point({lat1},{long1}) and arrival_point({lat2},{long2}).
#                     Based on the stations, it determines the boarding station closest to the ({lat1},{long1}) and the drop-off station closest to the ({lat2},{long2}).
#                     3. Return ONLY a valid JSON object in this format:

#             {{
#             "boarding_station": {{
#                 "latitude": float,
#                 "longitude": float
#             }},
#             "dropoff_station": {{
#                 "latitude": float,
#                 "longitude": float
#             }}
#             }}
                    
#                         """,
            
#             expected_output="Valid JSON object only.",
#         output_json=RouteStations,
#         output_file=os.path.join(output_dir,'stup1.json'),
        
#             agent=agent_station_for_Firebase,

#         )
#         # #Agent  A get the  route from fairbase

#         class RoutePoint(BaseModel):
#             lat: float
#             lng: float


#         class RouteSegment(BaseModel):
#             segment_points: List[RoutePoint]

#         agent_part_for_Firebase=Agent(
#         name ='agent_part_for_Firebase',
#             role='The agent retrieves the section of the transmission line that the user will use.',
#             goal= 'It performs the entire route from the Firebase and determines the segment the user is traversing based on the two stations specified by the previous agent (agent_station_for_Firebase).',
#             backstory='This agent is the second stage; it determines the route taken by the transporter, so you will not later merge it with the complete route drawn on the map.',
#             llm=llm2,
#             verbose=False,
#             tools=[get_faibase]
#         )
#         task_part_for_Firebase=Task(
#             description="""
#                     Use the tool get_faibase with:
#                     collection_name = "routes"
#                     document_name = "{document}"
#                     array_name = "points"
#                     First, it retrieves all the points of the line from firbase.
#                     The boarding and alighting stations are received from the previous agent, agent_station_for_Firebase.
#                     Now, the system cuts off the damage it brought from the Firebase, where it cancels all points before the boarding station and after the drop-off station, and cancels all points in between, including the two stations.
                
#                     Return ONLY valid JSON.
#                         """,
            
#             expected_output="Valid JSON object only.",
#             agent=agent_part_for_Firebase,
#             output_json=RouteSegment,
#          output_file=os.path.join(output_dir,'stup2.json'),
        
#             context=[ 
#                 task_station_for_Firebase,
#                 ],

#         )
#         # #Agent B  get the route from osrm 
#         @tool("Get Distance From OSRM")
#         def get_distance_from_osrm(start_lat: float, start_lng: float,
#                                 end_lat: float, end_lng: float):
#             """
#             Returns driving distance (meters) and duration (seconds)
#             between two points using OSRM.
#             """

#             url = (
#                 f"http://router.project-osrm.org/route/v1/driving/"
#                 f"{start_lng},{start_lat};{end_lng},{end_lat}"
#                 f"?overview=false"
#             )

#             response = requests.get(url)
#             data = response.json()

#             if data["code"] != "Ok":
#                 return {"error": "Route not found"}

#             route = data["routes"][0]

#             return {
#                 "distance_meters": route["distance"],
            
#             }
#         @tool("Get True Route From OSRM")
#         def get_route_from_osrm(start_lat: float, start_lng: float,
#                                 end_lat: float, end_lng: float):
#             """
#             Returns the real driving route between two points using OSRM.
#             """

#             url = f"http://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=full&geometries=geojson"

#             response = requests.get(url)
#             data = response.json()

#             if data["code"] != "Ok":
#                 return {"error": "Route not found"}

#             coordinates = data["routes"][0]["geometry"]["coordinates"]

#             points = [
#                 {"lat": coord[1], "lng": coord[0]}
#                 for coord in coordinates
#             ]

#             return {"points": points}
#         class osrmRoute(BaseModel):
#             boarding_segment: RouteSegment
#             dropoff_segment: RouteSegment
#         class FinalRoute(BaseModel):
#             full_route: List[RoutePoint]
#             boarding_station: Station
#             dropoff_station: Station
#         agent_part_for_Osrm=Agent(
#             name='agent_part_for_Osrm',
#             role='Bring the true path using osrm',
#             goal= 'It brings the actual route between the starting point and the pick-up point, and between the drop-off point and the arrival point.',
#             backstory='This is stage 3, where the route the user takes to reach the boarding station and from the drop-off station to the destination is determined and then merged.',
#             llm=llm3,
#             tools=[get_route_from_osrm,get_distance_from_osrm],
#             verbose=False,

#         )
#         task_part_for_Osrm=Task(
#             description="""
#             You MUST use the tool 'Get True Route From OSRM' to retrieve the real driving route.
#             Use the tool get_distance_from_osrm with:
#                         start_lat= {lat1},
#                         start_lng= {long1},
#                         end_lat= {lat2}, 
#                         end_lng= {long2}
#                     Use the tool get_route_from_osrm with:
#                         start_lat= {lat1},
#                         start_lng= {long1},
#                         end_lat= {lat2}, 
#                         end_lng= {long2}
#                         It receives the person's starting_point({lat1},{long1}) and arrival_point({lat2},{long2}).
#                         The boarding and landing stations are received from the previous agent, agent_station_for_Firebase.
#                         You must use osrm to calculate the distance between the starting point and the boarding station, and between the drop-off station and the arrival point, in meters.
#                         You must at least bring up double the distance from the points. For example, if the distance between the station and point M is 20, you should bring up at least point 40 to draw the route. This applies to all landing and boarding sections.
#                         Based on the Osrm, it brings the true, correct, and closest route from the starting point and boarding station to nearby points.
#                         Based on the Osrm, it brings the true, correct, and shortest route from the pick-up station to the destination, including nearby points.
                        
#                         """,
#             expected_output="Valid JSON object only.",
#             output_json=osrmRoute,
#         output_file=os.path.join(output_dir,'stup3.json'),
#             agent=agent_part_for_Osrm,
#             context=[ 
#                 task_station_for_Firebase,
#                 ],
                

#         )
#         #Aegnt  C gnrait the complet route  (A+B)  and get taim
#         agent_completed_route=Agent(
#             name='agent_completed_route',
#             role='Gather all parts of the road',
#             goal= 'Providing a complete list of path points combines all previous agent results.',
#             backstory='This is the final stage where all the parts are assembled to create a complete path that includes everything and is ready to be sent to the application filters for drawing.',
#             llm=llm4,
#             verbose=False,

#         )
#         task_completed_route=Task(
#             description="""
#                     First, the route is taken from the starting point to the pick-up station from the agent agent_part_for_Osrm.
#                     Secondly, the road section is part of the transport route between the pick-up and drop-off stations, as per the agent's results agent_part_for_Firebase.
#                     Three receive the route from the drop-off station to the arrival point from the agent results agent_part_for_Osrm
#                     Fourth, it arranges all the results as follows: points from the start to the ride, then to the dismount, then to the arrival, all together.
#                     Also send the results for Agent 1 agent_station_for_Firebase : boarding station and drop-off station.
#                     "boarding_station": {{
#                             "latitude": float,
#                             "longitude": float
#                                 }},
#                     "dropoff_station": {{
#                             "latitude": float,
#                             "longitude": float
#                           }}
#                           """,
#             expected_output="Valid JSON object only.",
#             output_json=FinalRoute,
#             output_file=os.path.join(output_dir,'stup4.json'),
#             context=[ 
#                 task_station_for_Firebase,
#                 task_part_for_Firebase,
#                 task_part_for_Osrm,
#                 ],
#             agent=agent_completed_route,

#         )
#         #the Crew
#         rankyx_crew = Crew(
#             agents=[
#                 agent_station_for_Firebase,
#                 agent_part_for_Firebase,
#                 agent_part_for_Osrm,
#                 agent_completed_route
#             ],
#             tasks=[
#                 task_station_for_Firebase,
#                 task_part_for_Firebase,
#                 task_part_for_Osrm,
#                 task_completed_route


#             ],
#             process=Process.sequential,
#             verbose= True

#         )
#         return rankyx_crew

# def run_ai(inputs):
#     crew = init_agents_and_crew()
#     result = crew.kickoff(inputs=inputs)
#     return json.loads(result.raw)
from crewai import LLM, Agent, Task, Process, Crew
from crewai.tools import tool
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from firebase_admin import credentials, firestore
import agentops
import os
import json
import math
import firebase_admin
import requests

# ─── Firebase ───────────────────────────────────────────────
# ── Firebase ─────────────────────────────────────────────
load_dotenv()
output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)
firebase_env = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_env:
    raise ValueError("FIREBASE_CREDENTIALS is missing")

firebase_dict = json.loads(firebase_env)

cred = credentials.Certificate(firebase_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

agentops.init(api_key=os.getenv("agentops_api_key"), skip_auto_end_session=True)


# ─── LLM ────────────────────────────────────────────────────
def make_llm(key_env):
    return LLM(
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=os.getenv(key_env),
        temperature=0.2,
        max_tokens=4096,
    )

llm4 = make_llm("GROQ_API_KEY_4")


# ─── Pydantic Models ────────────────────────────────────────
class Station(BaseModel):
    latitude: float
    longitude: float

class RoutePoint(BaseModel):
    lat: float
    lng: float

class FinalRoute(BaseModel):
    full_route: List[RoutePoint]
    boarding_station: Station
    dropoff_station: Station


# ─── Helper ─────────────────────────────────────────────────
def _haversine(lat1, lng1, lat2, lng2) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ════════════════════════════════════════════════════════════
#  STEP 1 & 2 — Firebase (pure Python)
# ════════════════════════════════════════════════════════════
def run_firebase_step(document: str, lat1, long1, lat2, long2) -> dict:
    doc = db.collection("routes").document(document).get().to_dict()
    stations = doc.get("marker", [])
    points   = doc.get("points", [])

    nearest_b = min(stations, key=lambda s: _haversine(
        s["lat"], s["lng"], float(lat1), float(long1)))
    nearest_d = min(stations, key=lambda s: _haversine(
        s["lat"], s["lng"], float(lat2), float(long2)))

    bi = min(range(len(points)), key=lambda i: _haversine(
        points[i]["lat"], points[i]["lng"], nearest_b["lat"], nearest_b["lng"]))
    di = min(range(len(points)), key=lambda i: _haversine(
        points[i]["lat"], points[i]["lng"], nearest_d["lat"], nearest_d["lng"]))

    if bi > di:
        bi, di = di, bi

    segment = points[bi: di + 1]

    result = {
        "boarding_station": {
            "latitude":  nearest_b["lat"],
            "longitude": nearest_b["lng"]
        },
        "dropoff_station": {
            "latitude":  nearest_d["lat"],
            "longitude": nearest_d["lng"]
        },
        "segment_points": segment
    }

    with open(os.path.join(output_dir, "step1.json"), "w") as f:
        json.dump({
            "boarding_station": result["boarding_station"],
            "dropoff_station":  result["dropoff_station"],
        }, f)
    with open(os.path.join(output_dir, "step2.json"), "w") as f:
        json.dump({"segment_points": segment}, f)

    return result


# ════════════════════════════════════════════════════════════
#  STEP 3 — OSRM (pure Python)
# ════════════════════════════════════════════════════════════
def _osrm_route(start_lat, start_lng, end_lat, end_lng) -> list:
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{start_lng},{start_lat};{end_lng},{end_lat}"
        f"?overview=full&geometries=geojson"
    )
    data = requests.get(url).json()
    if data["code"] != "Ok":
        return []
    coords = data["routes"][0]["geometry"]["coordinates"]
    return [{"lat": c[1], "lng": c[0]} for c in coords]


def run_osrm_step(firebase_result: dict, inputs: dict) -> dict:
    b = firebase_result["boarding_station"]
    d = firebase_result["dropoff_station"]

    boarding_segment = _osrm_route(
        inputs["lat1"], inputs["long1"],
        b["latitude"], b["longitude"]
    )
    dropoff_segment = _osrm_route(
        d["latitude"], d["longitude"],
        inputs["lat2"], inputs["long2"]
    )

    result = {
        "boarding_segment": {"segment_points": boarding_segment},
        "dropoff_segment":  {"segment_points": dropoff_segment},
    }

    with open(os.path.join(output_dir, "step3.json"), "w") as f:
        json.dump(result, f)

    return result


# ════════════════════════════════════════════════════════════
#  STEP 4 — Merger (pure Python, no LLM needed)
# ════════════════════════════════════════════════════════════
def run_merge_step(firebase_result: dict, osrm_result: dict) -> dict:
    b = firebase_result["boarding_station"]
    d = firebase_result["dropoff_station"]

    full_route = (
        osrm_result["boarding_segment"]["segment_points"]
        + firebase_result["segment_points"]
        + osrm_result["dropoff_segment"]["segment_points"]
    )

    result = {
        "full_route":        full_route,
        "boarding_station":  b,
        "dropoff_station":   d,
    }

    with open(os.path.join(output_dir, "step4.json"), "w") as f:
        json.dump(result, f)

    return result


# ════════════════════════════════════════════════════════════
#  Main entry point
# ════════════════════════════════════════════════════════════
def run_ai(inputs: dict) -> dict:
    # Step 1 & 2 — Firebase
    firebase_result = run_firebase_step(
        document=inputs["document"],
        lat1=inputs["lat1"],
        long1=inputs["long1"],
        lat2=inputs["lat2"],
        long2=inputs["long2"],
    )

    # Step 3 — OSRM
    osrm_result = run_osrm_step(firebase_result, inputs)

    # Step 4 — Merge
    final_result = run_merge_step(firebase_result, osrm_result)

    return final_result
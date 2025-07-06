import osmnx as ox
import random
from osmnx.distance import great_circle

# You can tune these weights
ALPHA = 1.0  # Distance
BETA = 2.0   # Blockage risk
GAMMA = 3.0  # Traffic congestion

def score_path(G, path):
    distance = 0
    blockage_risk = 0
    traffic_congestion = 0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        # Distance
        dist = great_circle(G.nodes[u]['y'], G.nodes[u]['x'],
                                               G.nodes[v]['y'], G.nodes[v]['x'])
        distance += dist

        # Blockage risk
        risk_u = G.nodes[u].get('blockage_risk', random.uniform(0, 1))
        risk_v = G.nodes[v].get('blockage_risk', random.uniform(0, 1))
        blockage_risk += (risk_u + risk_v) / 2

        # Traffic congestion (on the edge)
        traffic = G.edges[u, v, 0].get('traffic_congestion', random.randint(1, 10))
        traffic_congestion += traffic

    return ALPHA * distance + BETA * blockage_risk + GAMMA * traffic_congestion

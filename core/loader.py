import osmnx as ox
import networkx as nx
import random

def load_graph(place="Purulia, West Bengal, India", filepath="data/purulia.graphml", use_cache=True):
    ox.settings.use_cache = use_cache
    try:
        print("🔃 Loading graph from file...")
        G = ox.load_graphml(filepath)
    except:
        print(f"🌐 Downloading graph for: {place}")
        G = ox.graph_from_place(place, network_type='all', simplify=True)
        ox.save_graphml(G, filepath)

    # ✅ Add dummy risk and congestion attributes here
    assign_dummy_risks_and_traffic(G)

    return G

def assign_dummy_risks_and_traffic(G):
    for node in G.nodes:
        G.nodes[node]['blockage_risk'] = random.uniform(0, 1)

    for u, v, k in G.edges(keys=True):
        G.edges[u, v, k]['traffic_congestion'] = random.randint(1, 10)

    print("✅ Dummy risk and congestion values assigned.")

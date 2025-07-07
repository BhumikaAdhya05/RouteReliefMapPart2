import osmnx as ox
import networkx as nx
import random
import os
from core.routing import precompute_fallback_paths

def load_graph(place="Purulia, West Bengal, India", filepath="data/purulia.graphml", use_cache=True):
    ox.settings.use_cache = use_cache
    try:
        print("🔃 Loading graph from file...")
        G = ox.load_graphml(filepath)
    except:
        print(f"🌐 Downloading graph for: {place}")
        G = ox.graph_from_place(place, network_type='all', simplify=True)
        ox.save_graphml(G, filepath)

    assign_dummy_risks_and_traffic(G)

    # ✅ Offline precompute fallback paths (between 5 common critical points)
    nodes = list(G.nodes)
    if len(nodes) > 5:
        important_nodes = random.sample(nodes, 5)
        for i in range(len(important_nodes)):
            for j in range(i + 1, len(important_nodes)):
                src = important_nodes[i]
                tgt = important_nodes[j]
                fallback_path_file = f"fallbacks/fallbacks_{src}_{tgt}.pkl"
                if not os.path.exists(fallback_path_file):
                    precompute_fallback_paths(G, src, tgt, k=3, blocked_nodes=set(), cache_file=fallback_path_file)

    return G

def assign_dummy_risks_and_traffic(G):
    for node in G.nodes:
        G.nodes[node]['blockage_risk'] = random.uniform(0, 1)
    for u, v, k in G.edges(keys=True):
        G.edges[u, v, k]['traffic_congestion'] = random.randint(1, 10)
    print("✅ Dummy risk and congestion values assigned.")

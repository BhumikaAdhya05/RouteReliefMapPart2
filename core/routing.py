import networkx as nx
import osmnx as ox
import pickle
import os
from core.scorer import score_path
from core.aco import AntColony
from osmnx.distance import great_circle

def heuristic(a, b, G):
    return great_circle(G.nodes[a]['y'], G.nodes[a]['x'],
                                           G.nodes[b]['y'], G.nodes[b]['x'])

def astar_path(G, source, target):
    return nx.astar_path(G, source, target, heuristic=lambda a, b: heuristic(a, b, G))

def dijkstra_path(G, source, target):
    return nx.dijkstra_path(G, source, target)

def precompute_fallback_paths(G, source, target, k=3, blocked_nodes=set(), cache_file='fallbacks.pkl'):
    G_clean = G.copy()
    G_clean.remove_nodes_from(blocked_nodes)

    try:
        all_paths = list(nx.all_simple_paths(G_clean, source, target, cutoff=50))
        all_paths = sorted(all_paths, key=lambda p: score_path(G, p))
        top_k = all_paths[:k]

        # Save to cache
        with open(cache_file, 'wb') as f:
            pickle.dump(top_k, f)
        print(f"✅ Precomputed and saved {len(top_k)} fallback paths.")

    except Exception as e:
        print(f"❌ Could not precompute fallbacks: {e}")

    if not top_k:
        print("⚠️ No fallback paths found during precomputation.")
        return

def hmaosp_route(G, source, target, blocked_nodes=set()):
    G_undirected = G.to_undirected()

    try:
        print("🔁 Attempting A*")
        path = astar_path(G, source, target)
    except:
        print("⚠️ A* failed. Using Dijkstra.")
        path = dijkstra_path(G_undirected, source, target)

    for i, node in enumerate(path):
        if node in blocked_nodes:
            print(f"🚧 Blockage at node {node}")
            
            prefix_path = path[:i]
            reroute_source = prefix_path[-1] if prefix_path else source

            G_clean = G_undirected.copy()
            G_clean.remove_nodes_from(blocked_nodes)

            cache_file = f'fallbacks_{reroute_source}_{target}.pkl'

            # Precompute if not cached
            if not os.path.exists(cache_file):
                precompute_fallback_paths(G_clean, reroute_source, target, k=3, blocked_nodes=blocked_nodes, cache_file=cache_file)

            try:
                with open(cache_file, 'rb') as f:
                    fallback_paths = pickle.load(f)

                if fallback_paths:
                    best = sorted(fallback_paths, key=lambda p: score_path(G, p))[0]
                    print("🔁 Re-routed using precomputed fallback.")
                    return prefix_path + best[1:]  # Avoid node duplication
            except:
                print("❌ Failed to load fallback.")

            # ACO fallback
            # Try Dijkstra again as reroute fallback
            try:
                print("🔁 Trying Dijkstra reroute...")
                reroute_path = dijkstra_path(G_clean, reroute_source, target)
                print("✅ Dijkstra reroute succeeded.")
                return prefix_path + reroute_path[1:]  # Skip duplicate
            except:
                print("⚠️ Dijkstra reroute failed. Trying ACO...")

            # ACO fallback
            aco = AntColony(G_clean, reroute_source, target)
            best_path = aco.run()
            if best_path:
                print("✅ ACO fallback succeeded.")
                return prefix_path + best_path[1:]
            else:
                print("❌ ACO failed too.")
                return path

    return path

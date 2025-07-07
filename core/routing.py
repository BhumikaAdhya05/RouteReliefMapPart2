import networkx as nx
import os
import pickle
from core.aco import AntColony
from core.scorer import score_path

FALLBACK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fallbacks"))

def precompute_fallback_paths(G, source, target, k=3, blocked_nodes=set(), cache_file=None):
    from networkx import all_simple_paths

    # Compute all simple paths up to depth 20
    paths = list(all_simple_paths(G.to_undirected(), source, target, cutoff=20))
    # Filter out any that pass through blocked nodes
    paths = [p for p in paths if not any(n in blocked_nodes for n in p)]

    if cache_file:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'wb') as f:
            pickle.dump(paths[:k], f)
        print(f"✅ Saved {len(paths[:k])} fallback paths to {cache_file}")

def load_all_fallbacks(source, target):
    fallback_file = f"{FALLBACK_DIR}/allpaths_{source}_{target}.pkl"
    if os.path.exists(fallback_file):
        with open(fallback_file, 'rb') as f:
            return pickle.load(f)
    return []

def hmaosp_route(G, source, target, blocked_nodes=set()):
    from osmnx.distance import great_circle
    G_undirected = G.to_undirected()

    try:
        print("🔁 Trying A* first...")
        path = nx.astar_path(G, source, target, heuristic=lambda a, b: great_circle(
            G.nodes[a]['y'], G.nodes[a]['x'], G.nodes[b]['y'], G.nodes[b]['x']))
    except:
        print("⚠️ A* failed. Using Dijkstra.")
        path = nx.dijkstra_path(G_undirected, source, target)

    for i, node in enumerate(path):
        if node in blocked_nodes:
            print(f"🚧 Blockage at node {node}")
            prefix_path = path[:i]
            reroute_source = prefix_path[-1] if prefix_path else source

            print("🔍 Rerouting from", reroute_source, "to", target, "excluding:", blocked_nodes)

            # ✅ Try fallback paths
            fallback_paths = load_all_fallbacks(reroute_source, target)
            fallback_paths = [p for p in fallback_paths if not any(n in blocked_nodes for n in p)]

            if fallback_paths:
                best = sorted(fallback_paths, key=lambda p: score_path(G, p))[0]
                print("🔁 Re-routed using precomputed full fallback.")
                print("🛣️ Final fallback path:", best)
                assert all(n not in blocked_nodes for n in best), "❌ Blocked node still in fallback path!"
                return prefix_path + best[1:]

            # ✅ If fallback failed, try Dijkstra on cleaned graph
            print("⚠️ No valid fallback. Trying Dijkstra...")
            G_clean = G_undirected.copy()
            G_clean.remove_nodes_from(blocked_nodes)

            try:
                new_path = nx.dijkstra_path(G_clean, reroute_source, target)
                print("✅ Dijkstra reroute succeeded.")
                print("🛣️ Final rerouted path:", new_path)
                assert all(n not in blocked_nodes for n in new_path), "❌ Blocked node still in Dijkstra path!"
                return prefix_path + new_path[1:]
            except Exception as e:
                print(f"⚠️ Dijkstra failed: {e}")

            # ✅ ACO fallback as last resort
            print("🐜 Trying ACO fallback...")
            try:
                aco = AntColony(G_clean, reroute_source, target)
                best = aco.run()
                if best:
                    print("✅ ACO reroute succeeded.")
                    print("🛣️ Final ACO path:", best)
                    assert all(n not in blocked_nodes for n in best), "❌ Blocked node still in ACO path!"
                    return prefix_path + best[1:]
            except Exception as e:
                print(f"❌ ACO also failed: {e}")

            print("❌ All reroutes failed. Returning partial path.")
            return prefix_path

    return path

__all__ = ["hmaosp_route", "load_all_fallbacks", "precompute_fallback_paths"]

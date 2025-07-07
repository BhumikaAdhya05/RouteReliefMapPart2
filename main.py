from core.loader import load_graph
from core.routing import hmaosp_route
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle
import os
from networkx import all_simple_paths


def animate_route(G, path, blocked_node=None):
    if not path or len(path) < 2:
        print("❌ No valid path found.")
        return

    fig, ax = ox.plot_graph(G, show=False, close=False, bgcolor="white", node_size=0, edge_color="#ccc")
    x = [G.nodes[n]['x'] for n in path]
    y = [G.nodes[n]['y'] for n in path]

    ax.plot(x, y, color='lightcoral', linewidth=3, alpha=0.4, label="Full Path")
    marker, = ax.plot([], [], 'ro', markersize=12, label="Current Position")
    marker.set_zorder(10)
    animated_line, = ax.plot([], [], 'r-', linewidth=2)

    def init():
        marker.set_data([], [])
        animated_line.set_data([], [])
        return marker, animated_line

    def update(i):
        if i < len(x):
            marker.set_data([x[i]], [y[i]])
            animated_line.set_data(x[:i+1], y[:i+1])
        return marker, animated_line

    ani = animation.FuncAnimation(fig, update, init_func=init, frames=len(x), interval=1000, blit=True, repeat=False)

    if blocked_node and 'x' in G.nodes[blocked_node] and 'y' in G.nodes[blocked_node]:
        bx = G.nodes[blocked_node]['x']
        by = G.nodes[blocked_node]['y']
        ax.plot(bx, by, 'ks', markersize=10, label="Blocked Node")

    ax.legend()
    plt.title("🧭 HMAOSP: Route Simulation")
    plt.show()


def main():
    G = load_graph("Purulia, West Bengal, India", "data/purulia.graphml")

    print("🧭 Enter source and destination coordinates (latitude, longitude)")
    source_lat = float(input("Source Latitude: "))
    source_lon = float(input("Source Longitude: "))
    dest_lat = float(input("Destination Latitude: "))
    dest_lon = float(input("Destination Longitude: "))

    source = ox.distance.nearest_nodes(G, source_lon, source_lat)
    target = ox.distance.nearest_nodes(G, dest_lon, dest_lat)

    # ✅ Precompute and store all fallback paths BEFORE blockage simulation
    fallback_file = f"fallbacks/allpaths_{source}_{target}.pkl"
    if not os.path.exists(fallback_file):
        print("📦 Precomputing all fallback paths...")
        paths = list(all_simple_paths(G.to_undirected(), source, target, cutoff=20))
        os.makedirs("fallbacks", exist_ok=True)
        with open(fallback_file, "wb") as f:
            pickle.dump(paths, f)
        print(f"✅ Saved {len(paths)} fallback paths to disk.")
    else:
        print("✅ Loaded fallback path database.")

    # Simulate blockage
    simulate_block = input("Simulate blockage? (y/n): ").strip().lower() == 'y'
    blocked_nodes = set()
    trial_path = hmaosp_route(G, source, target, blocked_nodes)

    blocked_node = None
    if simulate_block and trial_path and len(trial_path) > 3:
        blocked_node = trial_path[len(trial_path) // 2]
        blocked_nodes = {blocked_node}
        print(f"🚧 Simulating blockage at node: {blocked_node}")
    else:
        print("⚠️ Not simulating blockage or path too short.")

    path = hmaosp_route(G, source, target, blocked_nodes)
    animate_route(G, path, blocked_node=blocked_node if simulate_block else None)


if __name__ == "__main__":
    main()

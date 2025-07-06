from core.loader import load_graph
from core.routing import hmaosp_route
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from core.visualize import visualize_graph_with_scores


def animate_route(G, path, blocked_node=None):
    if not path or len(path) < 2:
        print("❌ No valid path found.")
        return

    fig, ax = ox.plot_graph(G, show=False, close=False, bgcolor="white", node_size=0, edge_color="#ccc")

    x = [G.nodes[n]['x'] for n in path]
    y = [G.nodes[n]['y'] for n in path]

    # Static full path background
    ax.plot(x, y, color='lightcoral', linewidth=3, alpha=0.4, label="Full Path")

    # Animated marker and red trail
    marker, = ax.plot([], [], 'ro', markersize=12, label="Current Position")
    marker.set_zorder(10)  # Bring to front
    animated_line, = ax.plot([], [], 'r-', linewidth=2)

    def init():
        marker.set_data([], [])
        animated_line.set_data([], [])
        return marker, animated_line

    def update(i):
        if i < len(x):
            marker.set_data([x[i]], [y[i]])  # ✅ wrap in brackets
            animated_line.set_data(x[:i+1], y[:i+1])
        return marker, animated_line

    ani = animation.FuncAnimation(
        fig, update, init_func=init, frames=len(x), interval=1000, blit=True, repeat=False
    )

    # Show blocked node
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

    # Get nearest graph nodes
    source = ox.distance.nearest_nodes(G, source_lon, source_lat)
    target = ox.distance.nearest_nodes(G, dest_lon, dest_lat)

    # Simulate blockage
    simulate_block = input("Simulate blockage? (y/n): ").strip().lower() == 'y'
    blocked_node = None
    blocked_nodes = set()

    # Do a trial route to get the actual mid-node
    trial_path = hmaosp_route(G, source, target, blocked_nodes)

    if simulate_block and trial_path and len(trial_path) > 3:
        blocked_node = trial_path[len(trial_path) // 2]
        blocked_nodes = {blocked_node}
        print(f"🚧 Simulating blockage at node on path: {blocked_node}")
    else:
        print("⚠️ Not simulating blockage or path too short.")

    # Re-run route with possible blockage
    path = hmaosp_route(G, source, target, blocked_nodes)

    if not path or len(path) < 2:
        print("⚠️ No valid path found.")
        return

    animate_route(G, path, blocked_node=blocked_node if simulate_block else None)


if __name__ == "__main__":
    main()

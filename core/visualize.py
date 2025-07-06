import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

def visualize_graph_with_scores(G, path=[], blocked_nodes=[]):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Background edges color-coded by traffic congestion
    edge_colors = []
    for u, v, k in G.edges(keys=True):
        congestion = G.edges[u, v, k].get('traffic_congestion', 0)
        if congestion <= 3:
            edge_colors.append('green')
        elif congestion <= 7:
            edge_colors.append('orange')
        else:
            edge_colors.append('red')

    ox.plot_graph(G, ax=ax, show=False, close=False, edge_color=edge_colors, edge_linewidth=0.8, node_size=0)

    # Draw path (in bold red)
    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos=nx.get_node_attributes(G, 'x'), edgelist=path_edges,
                               edge_color='crimson', width=3, ax=ax)

    # Draw source, target, and blocked nodes
    if path:
        start, end = path[0], path[-1]
        x = G.nodes[start]['x']
        y = G.nodes[start]['y']
        ax.scatter(x, y, c='blue', s=100, label='Start')

        x = G.nodes[end]['x']
        y = G.nodes[end]['y']
        ax.scatter(x, y, c='green', s=100, label='End')

    for node in blocked_nodes:
        x = G.nodes[node]['x']
        y = G.nodes[node]['y']
        ax.scatter(x, y, c='black', s=80, label='Blocked')

    plt.legend()
    plt.title("🛣️ Risk-Aware Path with Traffic & Blockages")
    plt.show()

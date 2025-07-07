# core/aco.py

import random
import os
import osmnx as ox
import networkx as nx
from core.pheromone import save_pheromone, load_pheromone

class AntColony:
    def __init__(self, G, source, target, n_ants=10, n_best=3, n_iterations=50,
                 decay=0.5, alpha=1, beta=2, pheromone_file=None):
        self.G = G.to_undirected()
        self.source = source
        self.target = target
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.pheromone_file = pheromone_file or os.path.join(base_dir, "pheromones", f"{source}_{target}.pkl")

        # Load previous pheromone map if it exists
        existing = load_pheromone(self.pheromone_file)
        if existing:
            print("📥 Loaded previous pheromone map.")
            self.pheromone = existing
        else:
            self.pheromone = {edge: 1.0 for edge in self.G.edges()}
            print("🆕 Initialized new pheromone map.")

    def run(self):
        best_path = None
        best_score = float('inf')

        for _ in range(self.n_iterations):
            all_paths = self._construct_paths()
            self._update_pheromones(all_paths)

            for path in all_paths:
                score = self._score_path(path)
                if score < best_score:
                    best_path = path
                    best_score = score

        # Save updated pheromone map
        os.makedirs(os.path.dirname(self.pheromone_file), exist_ok=True)
        save_pheromone(self.pheromone_file, self.pheromone)
        print("💾 Saved pheromone map.")

        return best_path

    def _construct_paths(self):
        paths = []
        for _ in range(self.n_ants):
            path = self._construct_path()
            if path:
                paths.append(path)
        return paths

    def _construct_path(self):
        path = [self.source]
        visited = set(path)
        current = self.source

        for _ in range(100):  # max steps
            neighbors = [n for n in self.G.neighbors(current) if n not in visited]
            if not neighbors:
                return None

            probabilities = []
            for neighbor in neighbors:
                edge = tuple(sorted((current, neighbor)))
                distance = self._distance(current, neighbor)
                pheromone = self.pheromone.get(edge, 1.0)
                prob = (pheromone ** self.alpha) * ((1.0 / distance) ** self.beta)
                probabilities.append(prob)

            total = sum(probabilities)
            if total == 0:
                return None

            probabilities = [p / total for p in probabilities]
            next_node = random.choices(neighbors, weights=probabilities)[0]
            path.append(next_node)
            visited.add(next_node)
            current = next_node

            if current == self.target:
                return path

        return None

    def _distance(self, u, v):
        return ox.distance.great_circle(
            self.G.nodes[u]['y'], self.G.nodes[u]['x'],
            self.G.nodes[v]['y'], self.G.nodes[v]['x']
        )

    def _score_path(self, path):
        return sum(self._distance(path[i], path[i+1]) for i in range(len(path)-1))

    def _update_pheromones(self, paths):
        for edge in self.pheromone:
            self.pheromone[edge] *= (1 - self.decay)

        sorted_paths = sorted(paths, key=self._score_path)[:self.n_best]
        for path in sorted_paths:
            score = self._score_path(path)
            for i in range(len(path)-1):
                edge = tuple(sorted((path[i], path[i+1])))
                self.pheromone[edge] += 1.0 / (score + 1e-5)  # Avoid div-by-zero

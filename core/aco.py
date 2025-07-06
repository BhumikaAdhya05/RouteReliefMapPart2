import random
import osmnx as ox
from osmnx.distance import great_circle
import networkx as nx

class AntColony:
    def __init__(self, G, source, target, n_ants=10, n_best=3, n_iterations=50,
                 decay=0.5, alpha=1, beta=2):
        self.G = G.to_undirected()
        self.pheromone = {edge: 1.0 for edge in self.G.edges()}
        self.source = source
        self.target = target
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha  # influence of pheromone
        self.beta = beta    # influence of distance

    def run(self):
        best_path = None
        best_score = float('inf')

        for iteration in range(self.n_iterations):
            all_paths = self._construct_paths()
            self._update_pheromones(all_paths)

            for path in all_paths:
                score = self._score_path(path)
                if score < best_score:
                    best_path = path
                    best_score = score

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
                edge = (current, neighbor)
                distance = self._distance(current, neighbor)
                pheromone = self.pheromone.get(edge, 1.0)
                prob = (pheromone ** self.alpha) * ((1.0 / distance) ** self.beta)
                probabilities.append(prob)

            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]
            next_node = random.choices(neighbors, weights=probabilities)[0]
            path.append(next_node)
            visited.add(next_node)
            current = next_node

            if current == self.target:
                return path

        return None

    def _distance(self, u, v):
        return great_circle(
            self.G.nodes[u]['y'], self.G.nodes[u]['x'],
            self.G.nodes[v]['y'], self.G.nodes[v]['x']
        )

    def _score_path(self, path):
        return sum(self._distance(path[i], path[i+1]) for i in range(len(path)-1))

    def _update_pheromones(self, paths):
        # evaporate existing
        for edge in self.pheromone:
            self.pheromone[edge] *= (1 - self.decay)

        # reinforce best
        sorted_paths = sorted(paths, key=self._score_path)[:self.n_best]
        for path in sorted_paths:
            for i in range(len(path)-1):
                edge = (path[i], path[i+1])
                self.pheromone[edge] += 1.0 / self._score_path(path)

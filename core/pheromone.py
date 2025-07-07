# core/pheromone.py

import pickle
import os

def save_pheromone(filepath, pheromone_dict):
    with open(filepath, 'wb') as f:
        pickle.dump(pheromone_dict, f)

def load_pheromone(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    else:
        return None

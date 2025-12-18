import sys
import os
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ai.q_learning.training_manager import TrainManager

cfg = {
    3: {'eps': 1000, 'save': 200, 'wl': 3},
    4: {'eps': 1500, 'save': 300, 'wl': 4},
    5: {'eps': 2000, 'save': 400, 'wl': 4},
    6: {'eps': 2500, 'save': 500, 'wl': 5},
    7: {'eps': 3000, 'save': 600, 'wl': 5},
    8: {'eps': 3500, 'save': 700, 'wl': 5},
    9: {'eps': 4000, 'save': 800, 'wl': 5},
    10: {'eps': 4500, 'save': 900, 'wl': 5},
    11: {'eps': 5000, 'save': 1000, 'wl': 5},
    12: {'eps': 5500, 'save': 1100, 'wl': 5},
    13: {'eps': 6000, 'save': 1200, 'wl': 5},
    14: {'eps': 6500, 'save': 1300, 'wl': 5},
    15: {'eps': 7000, 'save': 1400, 'wl': 5}
}

def train_all():
    start = time.time()
    
    for sz in range(3, 9):
        tm = TrainManager(size=sz, sym='O')
        tm.train_vs_random(eps=cfg[sz]['eps'], save_every=cfg[sz]['save'])
        
        tm = TrainManager(size=sz, sym='X')
        tm.train_vs_random(eps=cfg[sz]['eps'], save_every=cfg[sz]['save'])
    
    end = time.time()
    return {'time': end - start}

if __name__ == '__main__':
    train_all()

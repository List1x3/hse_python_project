import sys
import os
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ai.q_learning.training_manager import TrainManager

cfg = {
    3: {'eps': 10000, 'save': 2000, 'wl': 3},
    4: {'eps': 15000, 'save': 3000, 'wl': 4},
    5: {'eps': 20000, 'save': 4000, 'wl': 4},
    6: {'eps': 25000, 'save': 5000, 'wl': 5},
    7: {'eps': 30000, 'save': 6000, 'wl': 5},
    8: {'eps': 35000, 'save': 7000, 'wl': 5},
    9: {'eps': 40000, 'save': 8000, 'wl': 5},
    10: {'eps': 45000, 'save': 9000, 'wl': 5},
    11: {'eps': 50000, 'save': 10000, 'wl': 5},
    12: {'eps': 55000, 'save': 11000, 'wl': 5},
    13: {'eps': 60000, 'save': 12000, 'wl': 5},
    14: {'eps': 65000, 'save': 1300, 'wl': 5},
    15: {'eps': 70000, 'save': 1400, 'wl': 5}
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

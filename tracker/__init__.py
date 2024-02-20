from .basic_tracker import *
from .trackers import *

def get_Tracker(tracker_name, mode):
    if mode == 'Basic':
        return eval(f'get_{tracker_name}({"BasicTracker"})')
    else:
        return eval(f'get_{tracker_name}({"DynamicTracker"})')


from .basic_tracker import *
from .trackers import *

def get_BasicTracker_by_name(tracker_name):
    return eval(f'get_{tracker_name}({"BasicTracker"})')

def get_DynamicTracker_by_name(tracker_name):
    return eval(f'get_{tracker_name}({"DynamicTracker"})')
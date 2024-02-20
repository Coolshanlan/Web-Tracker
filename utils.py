import collections, json, copy

default_config = {
    "enable":True,
    "extract_all": False,
    "encoding": False,
    "update_second": 300,
    "tracker": {
        "mode": "Basic",
        "tracker_name": "BasicTracker",
    }
}

def load_config(path='config.json'):
    try:
        with open(path, 'r') as f:
            track_website_infos = json.load(f)
    except:
        return None
    return track_website_infos


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def load_info(_info):
    website_info = copy.deepcopy(dict(default_config))
    update_dict(website_info, _info)
    return website_info

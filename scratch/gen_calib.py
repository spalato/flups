from datetime import date
from ruamel.yaml import YAML
import toml
import json
import yaml

ryaml = YAML()

records = [
    {
        "date": "2021-04-13", #date(2021, 4, 13),
        "b0": 303.047,
        "b1": 0.122468,
        "zero_indexed": False,
    },
    {
        "date": "2021-05-25", #date(2021, 5, 25),
        "b0": 303.44,
        "b1": 0.122607,
        "zero_indexed": False,
    }
]

indexed = {
    "2021-04-13": {
        "b0": 303.047,
        "b1": 0.122468,
        "zero_indexed": False,
    },
    "2021-05-25": {
        "b0": 303.44,
        "b1": 0.122607,
        "zero_indexed": False,
    },
}

dated = {
    date(2021, 4, 13): {
        "b0": 303.047,
        "b1": 0.122468,
        "zero_indexed": False,
    },
    date(2021, 5, 25): {
        "b0": 303.44,
        "b1": 0.122607,
        "zero_indexed": False,
    },
}
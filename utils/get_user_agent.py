import os
import json
import random


def get_a_ua():
    ua_path = os.path.abspath('../data/user_agent.json')
    p = json.load(open(ua_path))
    return random.choice(p)


if __name__ == '__main__':
    print(get_a_ua())

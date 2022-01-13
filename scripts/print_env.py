import os
import json

if __name__ == '__main__':
    print(json.dumps({
        key: dict(os.environ)[key]
        for key in sorted(dict(os.environ).keys())
    }, indent=2))
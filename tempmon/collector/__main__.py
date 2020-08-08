# pylint: disable=relative-beyond-top-level
from ..db.client import put
import time

temp_path = "/sys/bus/w1/devices/28-03150230cfff/hwmon/hwmon1/temp1_input"

def main():
    while True:
        with open(temp_path, "r") as f:
            temp = int(f.read().rstrip())
        put(temp)
        time.sleep(60)

if __name__ == "__main__":
    main()

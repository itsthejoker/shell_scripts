import os

from subprocess import check_output

import crayons

BATTERY_PATH = "/sys/class/power_supply/cw2015-battery/"

try:
    ssid = [
        line.strip("\t") for line in check_output(["iw", "dev"]).decode().splitlines()
            if "ssid" in line
    ][0][5:]

    network_speed = [
        line.strip().split("   ")[0].split("=")[1] for line in check_output(
            ["iwconfig", "wlan0"]
        ).decode().splitlines() if "Bit Rate" in line
    ][0] + "-ish"
except IndexError:
    ssid = "Not Connected"
    network_speed = "N/A"

battery_capacity = int(check_output(
    ["cat", os.path.join(BATTERY_PATH, "capacity")]
).decode())

battery_status = check_output(
    ["cat", os.path.join(BATTERY_PATH, "status")]
).decode().strip()
if battery_status == "Charging" or battery_status == "Full":
    battery_status = crayons.green(battery_status, bold=True)
else:
    battery_status = crayons.yellow(battery_status, bold=True)

disk_capacity_raw = check_output(
    ["df", "-l", "--output=source,pcent"]
).decode().splitlines()
disks = {line.split()[0]: line.split()[1] for line in disk_capacity_raw}
for disk in list(disks.keys()):
    if not disk.startswith("/dev/"):
        del disks[disk]
    if "loop" in disk or "zram" in disk:
        del disks[disk]


def generate_art(
        percentage: int,
        length: int = 50,
        term_columns: int = None,
        invert_colors: bool = False
) -> str:
    """
    Generate a colored progress bar of octothorpes and periods.

    :param percentage: integer between 1 and 100.
    :param length: how many characters to draw with; overridden if cols is passed in
    :param term_columns: the width of the terminal window; this overrides length
    :return: the fancy-ass bar
    """
    if term_columns:
        length = int(0.66 * term_columns)
    pcent = round(percentage/100 * length)
    if invert_colors:
        if percentage > 40:
            color = crayons.green
        elif percentage > 20:
            color = crayons.yellow
        else:
            color = crayons.red
    else:
        if percentage < 60:
            color = crayons.green
        elif percentage < 80:
            color = crayons.yellow
        else:
            color = crayons.red

    return color((pcent * "#") + ((length-pcent) * "."), bold=True)


def get_empty_space(header, cols, art):
    return " " * int(((int(cols) - len(header)) - len(art)) - 2)


rows, cols = os.popen('stty size', 'r').read().split()
rows = int(rows)
cols = int(cols)

print("\n- Disk -\n--------")
for d in disks:
    percentage_amt = int(disks[d].strip("%"))
    art = generate_art(percentage_amt, term_columns=cols)
    empty_space = get_empty_space(d, cols, art)
    print(d, empty_space, art)

print("\n- Network -\n-----------")
ssid_header = "SSID:"
empty = get_empty_space(ssid_header, cols, art)
print(ssid_header, empty, ssid)

network_speed_header = "Speed:"
empty = get_empty_space(network_speed_header, cols, art)
print(network_speed_header, empty, network_speed)

print("\n- Battery -\n-----------")
battery_art = generate_art(battery_capacity, term_columns=cols, invert_colors=True)
battery_header = "Battery Power:"
empty = get_empty_space(battery_header, cols, art)
print(battery_header, empty, battery_art)
battery_status_header = "Battery Status:"
empty = get_empty_space(battery_status_header, cols, art)
print(battery_status_header, empty, battery_status)
print()

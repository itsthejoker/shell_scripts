import os

from subprocess import check_output

import crayons

ssid = [
    line.strip("\t") for line in check_output(["iw", "dev"]).decode().splitlines()
        if "ssid" in line
][0][5:]

battery_capacity = int(check_output(
    ["cat", "/sys/class/power_supply/cw2015-battery/capacity"]
).decode())
battery_health = check_output(
    ["cat", "/sys/class/power_supply/cw2015-battery/health"]
).decode()

disk_capacity_raw = check_output(
    ["df", "-l", "--output=source,pcent"]
).decode().splitlines()
disks = {line.split()[0]: line.split()[1] for line in disk_capacity_raw}
for disk in list(disks.keys()):
    if not disk.startswith("/dev/"):
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


rows, cols = os.popen('stty size', 'r').read().split()
rows = int(rows)
cols = int(cols)

print("\n- Disk -\n--------\n")
for d in disks:
    percentage_amt = int(disks[d].strip("%"))
    art = generate_art(percentage_amt, term_columns=cols)
    empty_space = (int(cols) - len(d)) - len(art)
    print(d, " " * (empty_space-2), art)

print("\n- Network -\n-----------")
print(f"SSID: {ssid}")

print("\n- Battery -\n-----------")
battery_art = generate_art(battery_capacity, term_columns=cols, invert_colors=True)
battery_header = "Battery Power:"
empty_space = (int(cols) - len(battery_header)) - len(art)
print(battery_header, " " * (empty_space - 2), battery_art)
print(f"Battery Health: {battery_health}\n")

import textwrap

def generate_banner(msg):
    print(f"{'#'*54}".center(80))
    for line in textwrap.wrap(msg, width=50):
        print(f"#{line.center(52)}#".center(80))
    print(f"{'#'*54}".center(80))

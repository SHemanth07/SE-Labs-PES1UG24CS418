"""
Bike share rental parser (fixed version).

Every function validates its input and returns None when the input is
invalid, instead of crashing with an exception. Valid input behaves
exactly as before.
"""


def _is_ascii_digits(s):
    """True only for a non-empty string made of ASCII digits 0-9."""
    return isinstance(s, str) and s != "" and s.isascii() and s.isdigit()


def parse_ride_duration(text):
    """
    Converts a ride duration written as HH:MM into minutes.
    Returns the number of minutes, or None if the input is invalid.
    """
    if not isinstance(text, str):
        return None
    parts = text.strip().split(':')
    if len(parts) != 2:
        return None
    hours, minutes = parts
    if not (_is_ascii_digits(hours) and _is_ascii_digits(minutes)):
        return None
    if len(hours) > 4 or len(minutes) > 2:
        return None
    hours, minutes = int(hours), int(minutes)
    if minutes > 59:
        return None
    return hours * 60 + minutes


def format_station_code(code):
    """
    Formats a station code as ZONE-NUMBER, e.g. 'a12' -> 'A-12'.
    Returns None if the code is not one letter followed by digits.
    """
    if not isinstance(code, str):
        return None
    code = code.strip()
    if len(code) < 2 or not code.isascii():
        return None
    if not code[0].isalpha() or not _is_ascii_digits(code[1:]):
        return None
    code = code.upper()
    return code[0] + '-' + code[1:]


def parse_ride_log(line):
    """
    Parses 'bike_type,minutes,subscriber' into (str, int, bool).
    Returns None if the line does not have exactly three valid fields.
    """
    if not isinstance(line, str):
        return None
    parts = line.split(',')
    if len(parts) != 3:
        return None
    bike_type = parts[0].strip()
    minutes = parts[1].strip()
    subscriber = parts[2].strip().lower()
    if bike_type == "":
        return None
    if not _is_ascii_digits(minutes) or len(minutes) > 6 or int(minutes) <= 0:
        return None
    if subscriber not in ("yes", "no"):
        return None
    return bike_type, int(minutes), subscriber == "yes"


def main():
    try:
        print("==== Running parse_ride_duration ====")
        value = input("Enter a ride duration as HH:MM (e.g. 01:15): ")
        result = parse_ride_duration(value)
        print("Duration in minutes:" if result is not None else "Invalid duration:",
              result if result is not None else repr(value))

        print("\n==== Running format_station_code ====")
        value = input("Enter a station code (e.g. a12): ")
        result = format_station_code(value)
        print("Formatted station code:" if result is not None else "Invalid station code:",
              result if result is not None else repr(value))

        print("\n==== Running parse_ride_log ====")
        value = input("Enter a ride log line as type,minutes,subscriber (e.g. electric,45,yes): ")
        result = parse_ride_log(value)
        print("Parsed ride log:" if result is not None else "Invalid ride log line:",
              result if result is not None else repr(value))
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")


if __name__ == "__main__":
    main()

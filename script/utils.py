from datetime import datetime
import time

def message(msg):
    """
    Prints a message with a timestamp.

    Parameters:
        msg (str): The message to print.
    """
    print(f"[{time.ctime()}] {msg}")

def parseSteamDate(date_string):
    """
    Formats weird Steam date strings into a nicer format.
    
    Example conversion: "25 Jan, 2021 @ 12:34pm" -> "25 January 2021"

    Parameters:
        date_string (str): The input date string, as fetched from steamcommunity
                           screenshot page.
    
    Returns:
        str: The formatted date string in the format "DD Month YYYY".
    """
    if "@" in date_string:
        date_part = date_string.split("@")[0].strip()
    else:
        date_part = date_string.strip()

    try:
        parsed_date = datetime.strptime(date_part, "%d %b, %Y")
        formatted_date = parsed_date.strftime("%d %B %Y")
    except ValueError:
        # If the year is missing, assume the current year
        current_year = datetime.now().year
        date_part_with_year = f"{date_part} {current_year}"
        parsed_date = datetime.strptime(date_part_with_year, "%d %b %Y")
        formatted_date = parsed_date.strftime("%d %B %Y")

    return formatted_date
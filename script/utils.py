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
        date_string = date_string.split("@")[0]

    date_string = date_string.strip()

    input_date_format = "%b %d, %Y" if date_string[0].isalpha() else "%d %b, %Y"

    # if the year is missing, assume current year
    if "," not in date_string:
        current_year = datetime.now().year
        date_string = f"{date_string}, {current_year}"

    parsed_date = datetime.strptime(date_string, input_date_format)
    formatted_date = parsed_date.strftime("%d %B %Y")

    return formatted_date
from datetime import datetime
import time

def message(msg):
    """
    Prints a message with a timestamp.

    Parameters:
        msg (str): The message to print.
    """
    print(f"[{time.ctime()}] {msg}")
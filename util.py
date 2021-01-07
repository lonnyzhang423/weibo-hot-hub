import os
from datetime import datetime
from typing import AnyStr


def stripEmbracingQuotes(text: str):
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text


def currentTimeStr():
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')


def currentDateStr():
    return datetime.now().astimezone().strftime('%Y-%m-%d')


def ensureDir(file):
    directory = os.path.abspath(os.path.dirname(file))
    if not os.path.exists(directory):
        os.makedirs(directory)


def writeText(file: str, text: AnyStr):
    ensureDir(file)
    with open(file, 'w') as f:
        f.write(text)

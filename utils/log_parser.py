

import re


def parse_logs(file_path):
    
    pattern = re.compile(
        r"\[(?P<timestamp>[\d\- :]+)\]\s+"
        r"(?P<level>\w+)\s+"
        r"(?P<service>[\w\-]+):\s+"
        r"(?P<message>.+)"
    )

    entries = []
    with open(file_path, "r") as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                entries.append(match.groupdict())
    return entries


def filter_by_service(entries, service_keyword):
    
    return [e for e in entries if service_keyword.lower() in e["service"].lower()]


def has_errors(entries):
    
    return any(e["level"] == "ERROR" for e in entries)


import time
from utils.log_parser import filter_by_service, has_errors


def scan(log_entries, result_queue):
    start = time.time()

    # Simulated heavy scanning workload (real system: checking connection
    # pool health, replaying slow queries, checking replication lag)
    time.sleep(0.5)

    db_logs = filter_by_service(log_entries, "db")

    result = {
        "agent": "db_agent",
        "found_issue": False,
        "file": None,
        "line": None,
        "error_type": None,
        "raw_message": None,
    }

    if has_errors(db_logs):
        for entry in db_logs:
            result["found_issue"] = True
            result["file"] = "db_connector.py"
            result["line"] = None
            result["error_type"] = "DatabaseError"
            result["raw_message"] = entry["message"]
            break

    result["scan_time_sec"] = round(time.time() - start, 4)
    result_queue.put(result)
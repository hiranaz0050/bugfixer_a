

import time
from utils.log_parser import filter_by_service, has_errors


def scan(log_entries, result_queue):
    start = time.time()

    # Simulated heavy scanning workload (real system: checking route tables,
    # load balancer health, upstream service status)
    time.sleep(0.4)

    routing_logs = filter_by_service(log_entries, "routing")

    result = {
        "agent": "routing_agent",
        "found_issue": False,
        "file": None,
        "line": None,
        "error_type": None,
        "raw_message": None,
    }

    for entry in routing_logs:
        if entry["level"] == "INFO" and "500" in entry["message"]:
            result["found_issue"] = True
            result["file"] = "router.py"
            result["line"] = None
            result["error_type"] = "UpstreamServerError"
            result["raw_message"] = entry["message"]
            break

    result["scan_time_sec"] = round(time.time() - start, 4)
    result_queue.put(result)
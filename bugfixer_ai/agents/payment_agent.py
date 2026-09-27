
import time
from utils.log_parser import filter_by_service, has_errors


def scan(log_entries, result_queue):
   
    start = time.time()

    # Simulated heavy scanning workload (real system: parsing large production
    # log volumes, checking gateway signatures, tracing DB joins etc.)
    time.sleep(0.6)

    payment_logs = filter_by_service(log_entries, "payment")

    result = {
        "agent": "payment_agent",
        "found_issue": False,
        "file": None,
        "line": None,
        "error_type": None,
        "raw_message": None,
    }

    if has_errors(payment_logs):
        for entry in payment_logs:
            if "TypeError" in entry["message"] or "null pointer" in entry["message"]:
                result["found_issue"] = True
                result["file"] = "payment_processor.py"
                result["line"] = 245
                result["error_type"] = "NullReferenceError"
                result["raw_message"] = entry["message"]
                break

    result["scan_time_sec"] = round(time.time() - start, 4)
    result_queue.put(result)
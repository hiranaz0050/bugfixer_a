

import time
import multiprocessing as mp

from agents import payment_agent, db_agent, routing_agent
from utils.log_parser import parse_logs
from utils.patch_generator import generate_patch
from utils.test_runner import run_verification_tests


AGENTS = [payment_agent, db_agent, routing_agent]
LOG_FILE = "sample_logs/error_log.txt"


def run_agents_parallel(log_entries):
    """Teeno agents ko ek saath, alag processes mein chalata hai."""
    result_queue = mp.Queue()
    processes = []

    start = time.time()
    for agent_module in AGENTS:
        p = mp.Process(target=agent_module.scan, args=(log_entries, result_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    elapsed = time.time() - start

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results, elapsed


def run_agents_sequential(log_entries):
    """Comparison ke liye: same 3 agents, ek ek karke (baseline)."""
    result_queue = mp.Queue()
    start = time.time()

    for agent_module in AGENTS:
        agent_module.scan(log_entries, result_queue)

    elapsed = time.time() - start

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    return results, elapsed


def pick_root_cause(results):
    """
    Jitne bhi agents ne issue report kiya, unmein se sab se specific/upstream
    cause chuno - agent priority order ke hisaab se (payment > db > routing).
    """
    priority = {"payment_agent": 0, "db_agent": 1, "routing_agent": 2}
    found = [r for r in results if r["found_issue"]]
    if not found:
        return None
    return sorted(found, key=lambda r: priority.get(r["agent"], 99))[0]


def main():
    print("=" * 60)
    print("BugFixer AI - Automated Debugging System")
    print("=" * 60)

    print("\n[1] Parsing error logs...")
    log_entries = parse_logs(LOG_FILE)
    print(f"    -> {len(log_entries)} log lines parsed")

    print("\n[2] Running scanning agents (PARALLEL)...")
    parallel_results, parallel_time = run_agents_parallel(log_entries)
    for r in parallel_results:
        status = "ISSUE FOUND" if r["found_issue"] else "clean"
        print(f"    -> {r['agent']}: {status} (scan time: {r['scan_time_sec']}s)")
    print(f"    TOTAL PARALLEL TIME: {parallel_time:.4f}s")

    print("\n[3] Running same agents (SEQUENTIAL) for comparison...")
    _, sequential_time = run_agents_sequential(log_entries)
    print(f"    TOTAL SEQUENTIAL TIME: {sequential_time:.4f}s")

    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"    SPEEDUP FROM PARALLELISM: {speedup:.2f}x")

    print("\n[4] Identifying root cause...")
    root_cause = pick_root_cause(parallel_results)
    if not root_cause:
        print("    -> No issue found in logs.")
        return

    print(f"    -> Root cause: {root_cause['error_type']} in {root_cause['file']}")
    print(f"    -> Detail: {root_cause['raw_message']}")

    print("\n[5] Generating patch...")
    patch_result = generate_patch(root_cause)
    print(f"    -> Explanation: {patch_result['explanation']}")
    print(f"    -> Patch:\n{patch_result['patch']}")

    print("\n[6] Running automated verification tests...")
    test_result = run_verification_tests(patch_result)
    for t in test_result["tests"]:
        mark = "PASS" if t["passed"] else "FAIL"
        print(f"    -> [{mark}] {t['name']}")

    if test_result["all_passed"]:
        print(f"\n[DONE] Fix verified and ready to deploy. "
              f"(verification time: {test_result['verification_time_sec']}s)")
    else:
        print("\n[WARNING] Some tests failed - patch needs manual review.")

    print("=" * 60)


if __name__ == "__main__":
    main()
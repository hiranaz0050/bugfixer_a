# BugFixer AI - Automated Debugging System

A hackathon prototype that finds the root cause of a server crash from
error logs, creates a fix (patch), and verifies it with automated tests -
turning a 3-4 hour manual process into a matter of seconds.

## How to run it

```bash
py main.py
```

No extra installation needed - it only uses Python's built-in libraries
(`multiprocessing`, `re`, `time`), so it will run on any machine right away.

## Project Structure
bugfixer_ai/
├── main.py # Orchestrator - agents ko parallel launch karta hai
├── agents/
│ ├── payment_agent.py # Payment gateway logs scan karta hai
│ ├── db_agent.py # Database logs scan karta hai
│ └── routing_agent.py # API routing logs scan karta hai
├── utils/
│ ├── log_parser.py # Raw logs ko structured data mein convert karta hai
│ ├── patch_generator.py # Root cause ke hisaab se code patch banata hai
│ └── test_runner.py # Generated patch ko verify karta hai
└── sample_logs/
├── error_log.txt # Scenario 1: food delivery checkout crash

## Ye kaam kaise karta hai

1. **Ingestion** - error log parse hoti hai structured entries mein
2. **Parallel scanning** - teeno agents (`payment`, `db`, `routing`) ek saath,
   alag processes mein chalte hain - is se demo mein sequential ke muqablay
   ~2-2.5x speedup milta hai (real production logs pe ye gap aur bhi zyada hoga)
3. **Root cause selection** - sab se specific/upstream cause priority ke
   sath select hota hai (payment > db > routing)
4. **Patch generation** - `patch_generator.py` mein rule-based templates hain
5. **Automated verification** - patch ko deploy karne se pehle simulated
   test suite chalti hai

## Scenarios test 

```bash
py main.py                                    # default: checkout crash scenario
py main.py sample_logs/db_timeout_log.txt     # DB timeout scenario
```


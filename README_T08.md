# T08 — Natural Language to Spec (English)

Use plain English to instruct Aurora. The text is converted to a spec, then compiled to code/tests (offline).

## Quick start
```bash
make say WHAT="find the largest number in a list"
# or
python -m aurora_x.main --nl "sum of squares for a list"
```

## Supported Commands
- "find the largest number in a list" → max_in_list
- "reverse a string" → reverse_string  
- "sum of squares" → sum_of_squares
- "add two numbers" → add_two_numbers
- Other text → auto-generated placeholder spec

## How it Works
1. Natural language text is parsed to identify intent
2. A spec file is generated in `/specs/`
3. The v3 compiler creates code and tests in `/runs/`
4. Results persist to dashboard and JSONL logs

## Environment
Works offline - no external APIs needed. All processing is local.
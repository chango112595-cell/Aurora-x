## CLI: Generate Code from Spec (offline)

Run any spec through Aurora-X to produce code, tests, and a mini report:
```bash
python -m aurora_x.main --spec specs/rich_spec_v2.md
python -m aurora_x.main --spec specs/reverse_string.md
```
Then execute tests printed in the output.

### Available Specs:
- `specs/rich_spec_v2.md` - Add two numbers function
- `specs/reverse_string.md` - Unicode-safe string reversal
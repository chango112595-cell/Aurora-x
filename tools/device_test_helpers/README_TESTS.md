# Aurora One-Shot Hybrid Device Test (README)

## Files:
 - `tools/device_test_runner.py` (main orchestrator)
 - `scripts/aurora_device_test.sh` (wrapper)

## How to run (recommended):

1. Ensure PACK 6 + PACK 7 files are present and importable (PYTHONPATH includes repo root)
   ```bash
   export PYTHONPATH="$PWD:$PYTHONPATH"
   python3 -c "import sys; sys.path.insert(0, '.'); import aurora_fw.builder.packager"
   ```

2. Make scripts executable:
   ```bash
   chmod +x tools/device_test_runner.py scripts/aurora_device_test.sh
   ```

3. Run the hybrid test (auto-detect embedded + always linux-sbc + virtual):
   ```bash
   ./scripts/aurora_device_test.sh
   ```

   To force a target (e.g., esp32), run:
   ```bash
   ./scripts/aurora_device_test.sh --force esp32
   ```

   To auto-approve and perform flashing immediately:
   ```bash
   ./scripts/aurora_device_test.sh --auto-approve
   ```

4. Operator approval:
   By default stage jobs are stored in:
   ```
   aurora_fw/flasher/suggestions/
   ```
   Operator must review job JSON files and either:
   - Approve and call flash (e.g. via integration/dashboard), OR
   - Call the flash action manually with:
     ```bash
     python3 -c "from aurora_fw.flasher.flasher import flash_now; flash_now('path/to/job.json')"
     ```

5. Hot-swap demo:
   The runner will attempt hot-swap a demo plugin (`aurora_modules/demo-plugin`) after flashing.

## Notes:
- This is a dev/test harness. For real hardware flashing, ensure correct connections, drivers and that you understand the flashing commands.
- The runner will not flash physical devices unless you use `--auto-approve` or call flash manually after verifying the job.
- For continuous integration, run with a virtual target or a test rig.

## What this runner will do (step-by-step)

1. Clean `build/` folder (if `--clean`).

2. Build sample firmware artifacts for:
   - linux-sbc (tar with install script)
   - virtual device (small script)
   - and whichever embedded device is chosen/detected (esp32/cortex-m/rp2040).

3. Package each artifact into `.axf` (calls `aurora_fw.builder.packager.create_axf`).

4. Register the package in local registry (`aurora_fw.registry.register`) if available.

5. Stage a flash job for each package (creates JSON in `aurora_fw/flasher/suggestions/`).

6. If `--auto-approve` is set, the script will call `flash_now()` to execute flashing. Otherwise the operator must approve.

7. After staged jobs, the runner attempts a hot-swap demo: creates a `demo-plugin.tar.gz` and calls `cog_kernel.hotswap_manager.manager.apply_module_tar` to install and hot-reload it.

8. Final summary is logged in `logs/device_test_run.log`.

## Safety & operator control

- By default flashing is NOT executed. Jobs are staged into `aurora_fw/flasher/suggestions/` and require explicit approval.
- You can review staged jobs before approving in your operator dashboard (`integration/dashboard`) or by inspecting JSON files.
- To auto-approve (dangerous), use `--auto-approve`. Only do that on a controlled test bench.

## Example runs

Default hybrid (auto-detect + linux-sbc + virtual):
```bash
./scripts/aurora_device_test.sh --clean
```

Force ESP32 profile, no auto flash:
```bash
./scripts/aurora_device_test.sh --force esp32
# Inspect suggestions:
ls aurora_fw/flasher/suggestions
```

Force RP2040 and auto-approve (will try to flash if tools available):
```bash
./scripts/aurora_device_test.sh --force rp2040 --auto-approve
```

## Troubleshooting

If `create_axf` or other PACK6 functions are not importable, ensure your PYTHONPATH includes the repo root:
```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
```

If flashing tools are missing, the runner will create staged JSON jobs and simulate flash outcome; install `esptool`/`openocd`/`dfu-util` as needed.

## Final notes

This harness is intentionally conservative: operator approval is required by default for any flashing step. Use `--auto-approve` only on test rigs.

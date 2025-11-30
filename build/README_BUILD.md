# Aurora EdgeOS - Universal Cross-Build Tooling (3J)

## Overview
Multi-arch builder scripts, CI snippets, cross-compiler toolchains, firmware packaging, ABI matrices, signing helpers.

## Files

- `multiarch-tool.sh` - Build script for images and firmware (multi-arch)
- `firmware_packager.py` - Creates OTA tarballs + signs them (GPG)
- `ci-templates/` - GH Actions snippets for cross-builds

## Usage

### Multi-arch Docker Build

```bash
./build/multiarch-tool.sh auroraos latest
```

### Firmware Packaging

```bash
python3 build/firmware_packager.py ./source_dir output.tar.gz
```

### CI Integration

Copy `ci-templates/gh-cross-build.yml` to `.github/workflows/` for GitHub Actions cross-builds.

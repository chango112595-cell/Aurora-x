#!/usr/bin/env bash
# Simple wrapper: builds project using target toolchain
# usage: build_wrapper.sh <target> <build-dir>
TARGET="${1:-generic}"
BUILD_DIR="${2:-build}"
mkdir -p "$BUILD_DIR"
case "$TARGET" in
  esp32)
    echo "Building for esp32 (requires esp-idf)"
    # user is expected to run idf.py build in project folder; wrapper provided for convenience
    idf.py -B "$BUILD_DIR" build || exit 1
    ;;
  cortex-m)
    echo "Building for cortex-m (arm-none-eabi)"
    make -C . BUILD_DIR="$BUILD_DIR" || exit 1
    ;;
  *)
    echo "Generic make"
    make -C . BUILD_DIR="$BUILD_DIR" || exit 1
    ;;
esac

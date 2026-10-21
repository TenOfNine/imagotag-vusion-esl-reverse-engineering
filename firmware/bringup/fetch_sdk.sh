#!/bin/sh
# fetch_sdk.sh - get the EFR32FG22 device headers (Zlib licence) and the
# CMSIS core headers from Silicon Labs' Gecko SDK v4.4.1 on GitHub.
# Only these two folders are checked out (sparse, no history). The result
# lives in ./sdk and is not committed.
set -e
cd "$(dirname "$0")"
if [ -d sdk/gecko_sdk/.git ]; then
  echo "sdk/gecko_sdk already present"
  exit 0
fi
mkdir -p sdk
git clone --depth 1 --branch v4.4.1 --filter=blob:none --sparse \
  https://github.com/SiliconLabs/gecko_sdk sdk/gecko_sdk
git -C sdk/gecko_sdk sparse-checkout set \
  platform/Device/SiliconLabs/EFR32FG22 \
  platform/CMSIS/Core/Include
echo "done: sdk/gecko_sdk ($(git -C sdk/gecko_sdk rev-parse --short HEAD))"

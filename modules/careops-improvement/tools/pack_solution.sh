#!/bin/sh
# Apache-2.0
# Offline packaging only. PAC never receives an environment or authentication argument.
set -eu
module_root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
output_root=${1:-"$module_root/.local/solution-check"}
mkdir -p "$output_root"
pac solution pack --zipfile "$output_root/ImprovementRegister.zip"   --folder "$module_root/platform/solution/src" --packagetype Unmanaged --errorlevel Warning
# A new path prevents stale extracted files from satisfying round-trip checks.
roundtrip=$(mktemp -d "$output_root/roundtrip.XXXXXX")
pac solution unpack --zipfile "$output_root/ImprovementRegister.zip"   --folder "$roundtrip" --packagetype Unmanaged --errorlevel Warning
printf 'Unpacked source: %s\n' "$roundtrip"

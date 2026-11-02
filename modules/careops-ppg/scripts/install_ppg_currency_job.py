"""Install the 15-minute macOS user job from a provisioned private runtime."""
import argparse
import os
import plistlib
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("runtime", type=Path)
p.add_argument("node", type=Path)
p.add_argument("adapter", type=Path, help="Relative path within runtime/.local")
args = p.parse_args()
root = args.runtime.resolve(strict=True)
node = args.node.resolve(strict=True)
if args.adapter.is_absolute() or not (root / args.adapter).resolve(strict=True).is_relative_to(root / ".local"):
    p.error("Supply an installation-private adapter")
for required in ["scripts/ppg_currency_job.sh", "scripts/ppg_currency_report.mjs",
                 "scripts/ppg_policy_currency.mjs", ".local/currency-job/current.json"]:
    if not (root / required).is_file():
        p.error(f"Missing runtime file {required}")
label = "org.careops.ppgworkbench.policy-currency"
job = dict(Label=label, WorkingDirectory=str(root), StartInterval=900,
           ProgramArguments=["/bin/sh","scripts/ppg_currency_job.sh",str(node),str(args.adapter),".local/currency-job"],
           StandardOutPath=str(root/".local/currency-job/stdout.log"),
           StandardErrorPath=str(root/".local/currency-job/stderr.log"))
destination = Path.home() / "Library/LaunchAgents" / (label+".plist")
destination.parent.mkdir(exist_ok=True)
with destination.open("xb") as f:
    plistlib.dump(job,f)
domain = f"gui/{os.getuid()}"
subprocess.run(["launchctl","bootstrap",domain,str(destination)],check=True)
subprocess.run(["launchctl","kickstart",domain+"/"+label],check=True)

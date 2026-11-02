"""Prepare the policy currency Office Script and an independent empty host."""
import argparse
import json
from pathlib import Path
from scripts.ppg_office_runtime import blank_workbook


def build(directory):
    if '.local' not in directory.resolve().parts:
        raise ValueError('Use a new private output directory')
    directory.mkdir(parents=True,exist_ok=False,mode=0o700)
    root=Path(__file__).resolve().parents[1]
    meta=json.loads((root/'templates/installation/office-scripts/roles.json').read_text())
    meta.update(description='Policy currency matching and disposition reporting',
                body=(root/'scripts/ppg_currency_cloud.ts').read_text())
    (directory/'PPG-currency-cloud-v1.osts').write_text(json.dumps(meta))
    blank_workbook(directory/'PPG-currency-cloud-host.xlsx')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    build(parser.parse_args().directory)

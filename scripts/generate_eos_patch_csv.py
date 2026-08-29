#!/usr/bin/env python3
"""
Wolf Logic — Native ETC Eos Patch CSV Exporter
Converts the unpatched NCL rig inventory into official ETC Eos Patch CSV format:
Columns: Channel, Address, Type, Label
Channels and Addresses are left 100% BLANK so the user can soft-patch in Eos.
"""

import csv
import os

def generate_eos_patch_csv(input_csv, output_csv):
    fixtures = []
    with open(input_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fixtures.append({
                'Channel': '',       # Blank for custom user patching
                'Address': '',       # Blank for custom user patching
                'Type': row.get('Fixture_Type', ''),
                'Label': row.get('Label_Notes', '') or f"{row.get('Fixture_Type', '')} #{row.get('Unit_Number', '')}"
            })

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['Channel', 'Address', 'Type', 'Label']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fix in fixtures:
            writer.writerow(fix)

    print(f"✓ Native ETC Eos Patch CSV exported ({len(fixtures)} fixtures) to: {output_csv}")

if __name__ == '__main__':
    src = '/mnt/wolf-thumb/ETC-Wolf/csv/ncl_rig_inventory_unpatched.csv'
    dest = '/mnt/wolf-thumb/ETC-Wolf/csv/eos_patch_ncl_inventory.csv'
    generate_eos_patch_csv(src, dest)

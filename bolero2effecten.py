#!/usr/bin/env -S uv run --script

# /// script
# requires-python = '>=3.12'
# dependencies = [
#     'openpyxl',
#     'pandas',
# ]
# ///

from datetime import datetime
from contextlib import suppress as suppress_error
from os import remove
from shutil import copy2

import pandas as pd
import argparse

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('bolero_input_file')
    args = parser.parse_args()

    # Parse Bolero transaction file and merge with assets_mapping.csv
    bolero_csv_path = args.bolero_input_file
    effecten_mapping_path = 'assets_mapping.csv'

    df = pd.read_csv(bolero_csv_path,index_col=0, dtype=str)
    df = df[(df['Status'] == 'Uitgevoerd') & (df['Type effect'] != 'Option' )]
    new_df = pd.DataFrame({
        'Naam': df['Naam'],
        'ISIN': df['isin'],
        'Type effect': df['Type effect']
    })

    effecten = pd.read_csv(effecten_mapping_path)
    effecten = pd.concat([effecten, new_df])
    effecten = effecten.drop_duplicates(subset=['Naam','ISIN','Type effect'])
    effecten = effecten.sort_values(by=['Naam'], ascending=True)

    # Make a fresh backup from the mapping file
    backup_file_path = effecten_mapping_path.replace('.csv', '.backup.csv')
    with suppress_error(FileNotFoundError):
        remove(backup_file_path)
    copy2(effecten_mapping_path, backup_file_path)

    # Save the new mapping file
    effecten.to_csv(effecten_mapping_path, index=False)

if __name__ == '__main__':
    main()

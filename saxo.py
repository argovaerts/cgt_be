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
    parser.add_argument('saxo_input_file')
    args = parser.parse_args()
    saxo_excel_path = args.saxo_input_file

    tx_data_path = 'transaction_data.csv'

    # Read Saxo Excel transactions export
    df = pd.read_excel(saxo_excel_path, dtype=str)
    df = df[df['Type'] == 'Transactie']

    # Create new DataFrame with desired structure
    df[['Actie', 'Aantal', '_', 'Koers', 'Munt']] = df['Acties'].str.split(expand=True)

    df['Koers'] = df['Koers'].apply(map_amounts)
    df['Aantal'] = df['Aantal'].apply(map_amounts)
    df['Omrekeningskoers'] = df['Omrekeningskoers'].apply(map_amounts)
    df['Koers in Euro'] = df['Koers'] * df['Aantal'] * df['Omrekeningskoers']

    new_df = pd.DataFrame({
        'Datum': df['Transactiedatum'],
        'Transactie': df['Actie'].apply(map_activity_type),
        'ISIN': df['Instrument ISIN'],
        'Effect': df['Instrument'],
        'Type effect': df['Instrument ISIN'].apply(map_effect_type),
        'Broker': 'Saxo',
        'Aantal': df['Aantal'],
        'Koers': df['Koers'],
        'Munt': df['Munt'],
        'Koers in Euro': df['Koers in Euro'],
        'Opmerking': ''
    })

    # Make a fresh backup from the transaction data file
    backup_file_path = tx_data_path.replace('.csv', '.backup.csv')
    with suppress_error(FileNotFoundError):
        remove(backup_file_path)
    copy2(tx_data_path, backup_file_path)

    # Append to transaction data file
    tx_df = pd.read_csv(tx_data_path)
    tx_df = pd.concat([tx_df, new_df])
    tx_df = tx_df.sort_values(by=['Datum'], ascending=True)
    tx_df.to_csv(tx_data_path, index=False)

# Map activity type
def map_activity_type(transactie):
   return transactie.upper()

# Map effect type using mapping CSV
def map_effect_type(name) -> str:
    type_df = pd.read_csv('assets_mapping.csv', index_col='ISIN')
    type = type_df['Type effect'].get(name)
    if type is None:
        raise KeyError(f'Voeg {name} toe aan mapping table.')
    return type

# Map amounts
def map_amounts(amount) -> float:
    return float(amount.replace(',', ''))

# Convert date to ISO standard
def convert_date(date_str):
    dt = datetime.strptime(date_str, '%d/%m/%Y')
    return dt.strftime('%Y-%m-%d')

if __name__ == '__main__':
    main()

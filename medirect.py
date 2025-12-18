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
import pytz

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('medirect_input_file')
    args = parser.parse_args()
    medirect_excel_path = args.medirect_input_file

    tx_data_path = 'transaction_data.csv'

    # Read Medirect Excel transactions export
    df = pd.read_excel(medirect_excel_path, dtype=str)

    # Create new DataFrame with desired structure
    df[['Munt','Koers']] = df['Koers'].str.split(expand=True)
    df['Munt'] = df['Munt'].apply(map_currency)
    df['Koers in Euro'] = df['Koers'].where(df['Munt'] == 'EUR', '')

    new_df = pd.DataFrame({
        'Datum': df['Datum / Tijd (CET)'].apply(convert_date),
        'Transactie': df['Transacties'].apply(map_activity_type),
        'ISIN': df['Naam'].apply(map_isin),
        'Effect': df['Naam'],
        'Type effect': df['Naam'].apply(map_effect_type),
        'Broker': 'Medirect',
        'Aantal': df['Hoeveelheid'].apply(map_amounts),
        'Koers': df['Koers'].apply(map_amounts),
        'Munt': df['Munt'],
        'Koers in Euro': df['Koers in Euro'].apply(map_amounts),
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

# Convert date to ISO standard
def convert_date(date_str) -> str:
    tz = pytz.timezone(date_str[-3:])
    dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S %Z')
    dt_local = tz.localize(dt)
    dt_utc = dt_local.astimezone(pytz.UTC)
    return dt_utc.strftime('%Y-%m-%d')

# Map activity type
def map_activity_type(transactie) -> str:
    return transactie.upper()

# Map ISIN using mapping CSV
def map_isin(name) -> str:
    isin_df = pd.read_csv('assets_mapping.csv', index_col='Naam')
    isin = isin_df['ISIN'].get(name)
    if isin is None:
        raise KeyError(f'Voeg {name} toe aan mapping table.')
    return isin

# Map effect type using mapping CSV
def map_effect_type(name) -> str:
    type_df = pd.read_csv('assets_mapping.csv', index_col='Naam')
    type = type_df['Type effect'].get(name)
    if type is None:
        raise KeyError(f'Voeg {name} toe aan mapping table.')
    return type

# Map amounts
def map_amounts(amount_with_symbol) -> float:
    amount_str = amount_with_symbol.replace('€ ','')
    return float(amount_str.replace('.', '').replace(',', '.'))

# Map currency symbol to three letter code
def map_currency(symbol) -> str:
    if symbol == '€':
        return 'EUR'
    else:
        return ''

if __name__ == '__main__':
    main()

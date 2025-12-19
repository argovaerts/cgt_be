#!/usr/bin/env -S uv run --script

# /// script
# requires-python = '>=3.12'
# dependencies = [
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
    bolero_csv_path = args.bolero_input_file

    tx_data_path = 'transaction_data.csv'

    # Read Bolero CSV transactions export
    df = pd.read_csv(bolero_csv_path,index_col=0, dtype=str)
    df = df[(df['Status'] == 'Uitgevoerd') & (df['Type effect'] != 'Option' )]

    # Create new DataFrame with desired structure but process bonds seperately
    df[['Limietkoers', 'Munt']] = df['Limietkoers'].str.split(expand=True)
    bonds_df = df[(df['Type effect'] == 'Bond')]
    df = df[(df['Type effect'] != 'Bond')]

    new_df = pd.DataFrame({
        'Datum': df['Datum'].apply(convert_date),
        'Transactie': df['Type transactie'].apply(map_activity_type),
        'ISIN': df['isin'],
        'Effect': df['Naam'],
        'Type effect': df['Type effect'],
        'Broker': 'Bolero',
        'Aantal': df['Aantal'].apply(map_amounts),
        'Koers': df['Limietkoers'].apply(map_amounts),
        'Munt': df['Munt'],
        'Koers in Euro': '',
        'Opmerking': ''
    })

    new_df['Koers in Euro'] = new_df['Koers in Euro'].where(df['Munt'] != 'EUR', new_df['Koers'])

    new_bonds_df = pd.DataFrame({
        'Datum': bonds_df['Datum'].apply(convert_date),
        'Transactie': bonds_df['Type transactie'].apply(map_activity_type),
        'ISIN': bonds_df['isin'],
        'Effect': bonds_df['Naam'],
        'Type effect': bonds_df['Type effect'],
        'Broker': 'Bolero',
        'Aantal': bonds_df['Aantal'].apply(map_amounts),
        'Koers': bonds_df['Limietkoers'].apply(convert_bond_quote),
        'Munt': bonds_df['Munt'],
        'Koers in Euro': '',
        'Opmerking': ''
    })

    new_df = pd.concat([new_df, new_bonds_df])

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
    dt = datetime.strptime(date_str, '%d-%m-%Y')
    return dt.strftime('%Y-%m-%d')

# Map activity type
def map_activity_type(transactie) -> str:
   if transactie == 'Aankoop':
       return 'KOOP'
   elif transactie == 'Verkoop':
       return 'VERKOOP'
   elif transactie == 'Intekening':
       return 'KOOP'
   return ''

# Map amounts
def map_amounts(amount) -> float:
    return float(amount.replace('-','-1').replace('.', '').replace(',', '.'))

# Convert bond quote
def convert_bond_quote(quote_str) -> float:
    return float(quote_str.replace('%','').replace('-','100').replace('.', '').replace(',', '.'))

if __name__ == '__main__':
    main()

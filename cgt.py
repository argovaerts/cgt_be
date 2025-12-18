#!/usr/bin/env -S uv run --script

# /// script
# requires-python = '>=3.12'
# dependencies = [
#     'openpyxl',
#     'pandas',
# ]
# ///

from collections import deque
import pandas as pd

CGT_START_DATE = "2026-01-01"

PRECISION = 6  # Decimal precision for rounding
TOLERANCE = 1e-6  # Allowable tolerance for floating-point errors

def main() -> None:
    print('Start verwerking')
    transactions = pd.read_csv('transaction_data.csv')
    transactions = transactions.sort_values(by=['Datum', 'ISIN'], ascending=False)
    transactions['Transactie'] = transactions['Transactie'].str.upper()
    transactions['_asset'] = [' - '.join(i) for i in zip(transactions['ISIN'].map(str),transactions['Effect'])]

    buy_transactions = transactions[transactions['Transactie'] != 'VERKOOP']
    sell_transactions = transactions[transactions['Transactie'] == 'VERKOOP']
    assets = transactions['_asset'].unique()

    results = pd.DataFrame([], columns=[
        'ISIN', 'Effect', 'Type effect', 'Datum aankoop', 'Broker aankoop', 'Aantal aankoop', 'Koers in Euro aankoop of waardering bij start',
        'Datum verkoop', 'Broker verkoop', 'Aantal verkoop', 'Koers in Euro verkoop', 'Meerwaarde in Euro', 'Opmerking aankoop', 'Opmerking verkoop'
    ])

    for asset_index, asset in enumerate(assets, start=1):
        print(f'\n--- Verwerking effect {asset_index}/{len(assets)}: {asset} ---')

        asset_buy_transactions = buy_transactions[buy_transactions['_asset'] == asset]
        asset_sell_transactions = sell_transactions[sell_transactions['_asset'] == asset]

        total_bought = round(asset_buy_transactions['Aantal'].sum(), PRECISION)
        total_sold = round(asset_sell_transactions['Aantal'].sum(), PRECISION)
        print(f'Totaal aantal gekocht: {total_bought}')
        print(f'Totaal aantal verkocht: {total_sold}')

        if total_bought < total_sold:
            raise AssertionError(
                    f'Onvoldoende voorraad voor {asset}. '
                    f'Totaal gekocht: {total_bought}, Totaal verkocht: {total_sold}.'
                )

        # Make BUY transactions into a FIFO queue
        fifo_queue = process_buy_transactions(asset_buy_transactions)

        # Process SELL transactions
        results = process_sell_transactions(results, asset_sell_transactions, fifo_queue)

    # Save results
    results.to_excel('fifo_results.xlsx', index=False)
    print('\nFIFO berekening voltooid. Resultaten werden opgeslagen in fifo_results.xlsx.')


def process_buy_transactions(asset_buy_transactions: pd.DataFrame) -> deque:
    fifo_queue = deque()

    for index, buy in asset_buy_transactions.iterrows():
        fifo_queue.append(
            {
                'Datum': buy['Datum'],
                'ISIN': buy['ISIN'],
                'Effect': buy['Effect'],
                'Broker': buy['Broker'],
                'Aantal': round(buy['Aantal'], PRECISION),
                'Koers in Euro': buy['Koers in Euro'],
                'Opmerking': buy['Opmerking']
            }
        )
        print(f'🛒 KOOP toegevoegd: {fifo_queue[-1]}')
    
    return fifo_queue

def process_sell_transactions(results: pd.DataFrame, asset_sell_transactions: pd.DataFrame, fifo_queue: deque) -> pd.DataFrame:
    for index, sell in asset_sell_transactions.iterrows():
        asset = sell['_asset']
        
        sell_shares = round(sell['Aantal'], PRECISION)

        print(f'🔄 VERKOOP {sell_shares} deelbewijzen aan {sell['Koers in Euro']} per eenheid') # type: ignore
        print(f'FIFO queue voor verwerking: {list(fifo_queue)}')
        print(f'Totaal aantal voor verwerking: {sum(f.get('Aantal') for f in fifo_queue)}') # type: ignore

        # Match the sell shares to the FIFO queue
        while sell_shares > TOLERANCE:  # Allow small differences
            if not fifo_queue:
                # Debug remaining inventory at failure point
                print(f'❌ Resterende FIFO queue: {list(fifo_queue)}')
                raise AssertionError(
                    f'Onvoldoende voorraad voor {asset}. '
                    f'Geprobeerd om {sell_shares} deelbewijzen te verkopen. '
                )

            # Get the oldest BUY in the queue
            buy = fifo_queue[0]
            buy_shares = round(buy['Aantal'], PRECISION)

            if buy_shares <= sell_shares + TOLERANCE:
                # Fully consume this BUY
                fifo_cost_basis = buy_shares * buy['Koers in Euro']
                sell_shares -= buy_shares
                fifo_queue.popleft()  # Remove the consumed BUY

                sale_proceeds = round(buy_shares * sell['Koers in Euro'], PRECISION)
                gain_loss = round(sale_proceeds - fifo_cost_basis, 2)

                if sell['Datum'] > CGT_START_DATE: # Only report transactions after CGT start date
                    results = pd.concat([pd.DataFrame([[
                        sell['ISIN'], sell['Effect'], sell['Type effect'], buy['Datum'], buy['Broker'], buy['Aantal'], buy['Koers in Euro'],
                        sell['Datum'], sell['Broker'], buy_shares, sell['Koers in Euro'], gain_loss, buy['Opmerking'], sell['Opmerking']
                    ]], columns=results.columns), results], ignore_index=True)
                    print(f'✅ Volledig geconsumeerde KOOP: {buy}. Kostenbasis: {fifo_cost_basis}, Winst/verlies: {gain_loss}')
            else:
                # Partially consume this BUY
                fifo_cost_basis = sell_shares * buy['Koers in Euro']
                fifo_queue[0]['Aantal'] = round(buy_shares - sell_shares, PRECISION)  # Update the queue

                sale_proceeds = round(sell_shares * sell['Koers in Euro'], PRECISION)
                gain_loss = round(sale_proceeds - fifo_cost_basis, 2)

                if sell['Datum'] > CGT_START_DATE: # Only report transactions after CGT start date
                    results = pd.concat([pd.DataFrame([[
                        sell['ISIN'], sell['Effect'], sell['Type effect'], buy['Datum'], buy['Broker'], buy['Aantal'], buy['Koers in Euro'],
                        sell['Datum'], sell['Broker'], sell_shares, sell['Koers in Euro'], gain_loss, buy['Opmerking'], sell['Opmerking']
                    ]], columns=results.columns), results], ignore_index=True)
                    print(f'⚡ Deels geconsumeerde KOOP: {fifo_queue[0]}. Kostenbasis: {fifo_cost_basis}, Winst/verlies: {gain_loss}')

                sell_shares = 0
    
    return results


if __name__ == '__main__':
    main()

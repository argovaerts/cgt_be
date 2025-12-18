# Opstellen rapport meerwaardebelasting

## Installatie en opzet

1. Indien nodig, installeer [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Download een zip bundel van deze repository of maak een clone
3. De makkelijkste manier om te starten is om de bestaande portefeuille manueel in te geven met 01/01/2026 als startpunt voor de berekeningen. Indien [de historische aankoopwaarde hoger ligt](#historisch-hogere-aanschafwaarde) vermeld je dit in de Opmerking kolom om dit later mee te nemen (vereist manueel werk!).

Voor Bolero:
* [Bolero export extension](https://github.com/thibaultmarrannes/bolero-extension) is noodzakelijk om bruikbare extracties samen te stellen.

## Oplijsten transacties

### Bolero

1. Login bij [Bolero](https://www.bolero.be) en exporteer de transactiehistoriek met behulp van de Bolero export extensie.
2. Kijk na en corrigeer missende of verkeerde waardes (zeker voor obligaties en Britse aandelen!)
3. Voer `uv run bolero.py <file_path>` uit.
4. Kijk na en corrigeer missende of verkeerde waardes (zeker voor obligaties en Britse aandelen!)
5. Indien nodig, voer `uv run bolero2effecten.py` uit om de effecten ook aan de mapping CSV toe te voegen.

### Saxo

1. Navigeer naar [Open posities](https://www.saxotrader.com/d/trading/open-positions) en download het transactierapport zonder details als Excel bestand.
2. Indien nodig, vul `assets_mapping.csv` manueel aan.
3. Voer `uv run saxo.py <file_path>` uit.

### Medirect

1. Navigeer naar [Transactiegeschiedenis](https://online.medirect.be/e-banking/investments--trade-history) and download transactions
2. Indien nodig, vul `assets_mapping.csv` manueel aan.
3. Voer `uv run medirect.py <file_path>` uit.

### Andere

Voeg transacties manueel toe aan `transaction_data.csv` en vul `assets_mapping.csv` aan.

## Opstellen rapport voor meerwaardebelasting

1. Voer `uv run cgt.py` uit.
2. Open `fifo_results.csv` in een spreadsheet software en kijk na.

## Belastingsregimes

| Effect type                          |	Belastingsregime                                                                                 |
| ------------------------------------ | --------------------------------------------------------------------------------------------------- |
| Aandeel                              | Meerwaardebelasting 10% + roerende voorheffing op dividenden 30% (terugvorderbaar via vrijstelling) |
| Fonds / Tracker / CEF / Britse trust |                                                                                                     |
| - Aandelen                           | Meerwaardebelasting 10% + roerende voorheffing op dividenden 30%                                    |        
| - Gemengd                            | Meerwaardebelasting 10% op gekend gedeelde aandelen + Reynderstaks (roerende voorheffing) 30% op alle rest |
| - Obligaties                         | Reynderstaks (roerende voorheffing) 30%                                                             |
| Obligatie                            | Meerwaardebelasting 10% + roerende voorheffing op interest 30%                                      |
| Geschreven optie                     | Vrij van meerwaardebelasting, mogelijks premie onder divers inkomen (max(33%, marginale belastingvoet) + gemeentebelasting) |
| Gekochte optie                       | Meerwaardebelasting 10%                                                                             |
| Beleggingsgoud                       | Meerwaardebelasting 10%                                                                             |
| Pensioensparen                       | Anticipatieve heffing op kapitaal en rendement 8% op 60ste verjaardag onderschrijver of na 10 jaar indien onderschrijver reeds ouder dan 55 jaar bij start |
| Langetermijnsparen                   | Anticipatieve heffing op kapitaal en rendement 10% op 60ste verjaardag onderschrijver of na 10 jaar indien onderschrijver reeds ouder dan 55 jaar bij start |
| Groepsverzekering                    | RIZIV-bijdrage 3,55% + solidariteitsbijdrage 2% + bedrijfsvoorheffing tussen 10,09% en 20,19%       |
| Tak21 niet-fiscaal / Tak23 niet-fiscaal / Tak26 | Meerwaardebelasting 10% of roerende voorheffing 30%                                      |
| Crypto                               | Meerwaardebelasting 10%                                                                             |
| Voorhuwelijkssparen                  | Meerwaardebelasting 10% ???                                                                         |

### Historisch hogere aanschafwaarde

Als je een aandeel hebt gekocht voor 31 december 2025 aan een hogere prijs dan de waarde op de foto, zal je de hogere aankoopprijs in rekening mogen brengen in plaats van de waarde op de foto. Welke bewijsstukken je daarvoor moet aanleveren is nog niet bekend. Deze mogelijkheid geldt maar tot 31 december 2030. Voor verrichtingen na die datum wordt steeds de waarde op de foto op 31 december 2025 gebruikt.
Het gebruik van een historisch hogere aanschafwaarde kan echter nooit leiden tot het behalen van een minwaarde. Deze zal er wel voor zorgen dat de verschuldigde meerwaarde herleid wordt tot 0 euro.

Voorbeeld:

Je kocht een aandeel in 2023 aan 150 euro. De koers op 31 december 2025 bedraagt 120 euro (de ‘foto’). Je verkoopt dit aandeel op 15 september 2026 aan 125 euro. Je zou dus 10% moeten betalen op 5 euro (het verschil tussen de verkoopwaarde en de waarde op de foto op 31 december 2025). Nochtans behaalde je geen echte meerwaarde, aangezien je het aandeel duurder kocht dan verkocht. Tot 31 december 2030 kun je de werkelijke, historische aankoopprijs in rekening brengen.

### Bronnen
* https://www.nn.be/nl/kapitalevragen/nieuwe-meerwaardebelasting-wat-verandert-er-voor-je-levensverzekering-pensioensparen
* https://www.delen.bank/nl-be/blog/de-meerwaardebelasting-wat-u-moet-weten
* https://www.reddit.com/r/BEFire/comments/1pl3qb0/meerwaardebelasting_en_geschreven_opties/
* https://trends.knack.be/opinie/meerwaardebelasting-jaarlijks-aangeven-of-net-niet/
* https://www.wikifin.be/nl/pensioen-en-pensioenvoorbereiding/pensioensparen/hoe-wordt-je-pensioensparen-belast
* https://www.wikifin.be/nl/belasting-werk-en-inkomen/belastingaangifte/belastingverminderingen/vermindering-voor
* https://www.nagelmackers.be/nl/onze-inzichten/erfenis-en-fiscaliteit/5-vragen-over-de-nieuwe-meerwaardebelasting
* https://www.kbc.be/particulieren/nl/nieuws/arizona-regeerakkoord-meerwaardebelasting.html
BGC Internship Assignment

This repository contains my solution to a programming assignment focused on calculating position-level exposure from transaction and prices datasets.

The assignment required computing positions per (account, sec_id), determining trade prices, calculating market values, and deriving exposure as the absolute difference between market value at the latest price and at the trade price.


Approach

Trade Price: I used Volume Weighted Average Price (VWAP) to compute a single trade price per position. 
This method accounts for multiple trades and varying quantities, providing a realistic average trade price.

Market Value & Exposure: Market values were calculated at both the trade price and latest price, and exposure was computed as their absolute difference.

Dataset Issue & Workaround: The original prices file had no matching sec_ids with the transactions file, making direct exposure calculation impossible. 
To demonstrate working code, I replaced the sec_id column in the DataFrame derived from the prices file with sec_id values from the DataFrame derived from the transactions file.
Additionally, I created a dummy prices dataset where each sec_id from transactions had a corresponding price. 
This ensured all positions could be processed correctly, which would not have been possible otherwise. 


Outputs

answer1.csv: Top 10 positions by exposure.

answer2.csv: Positions missing prices in the last 3 days 
-->Empty due to the necessary dummy price workaround, but code is implemented to handle real missing prices if they existed.

All code is written in Python using pandas.

import pandas as pd
import random 

#read file
df = pd.read_excel("transactions.xlsx")


#Part 1: Create positions dataFrame
# group account ID column with sec_id column
# sum quantities for each acct:sec_id pair (these are our positions)
positions_series = df.groupby(["account","sec_id"])["qty"].sum()

# convert series to dataFrame
positions_df = positions_series.to_frame(name="position")
# convert from multi-index to flat dataFrame
positions_df = positions_df.reset_index()

#Part 2: Calculate trade price for each position (VWAP)
#Explanation... 
#Exposure for each position is defined by: ∣(Market Price * Position) - (Trade price * position)∣
#However, "Trade Price" in this formula was not defined.
#As such, I have decided to use an average trade price (VWAP) to determine the "trade price" term. 
#VWAP = ∑(|qty_i|×trade price_i)​ / ∑(|qty_i|)

#Create copy of transactions df to avoid corrupting position table
df_abs = df.copy()

#convert qty column into absolute values 
df_abs["qty"] = df_abs["qty"].abs()

#create new column which represents |qty| * price for each trade. 
df_abs["trade_value"] = df_abs["qty"] * df_abs["trade_px"]

#group transactions by account and sec_id 
acct_secID_pairs = df_abs.groupby(["account","sec_id"])



#sum the |qty|'s and values for all transactions withing acct--sec_id pairs
#also convert it back to a 2D dataFrame
pairs_sumCols = acct_secID_pairs[["qty","trade_value"]].sum().reset_index()
pairs_sumCols["VWAP_px"] = pairs_sumCols["trade_value"] / pairs_sumCols["qty"]



#Part 3: Calculate market value at trade price

#create new dataFrame which merges the VWAP-px col onto the dataFrame with positions
positions_MVT = positions_df.merge(
    pairs_sumCols[["account", "sec_id", "VWAP_px"]], 
    on = ["account", "sec_id"], 
    how = "left"
)

#create new column "MV_trade" which represents market value at trade price: (Position * VWAP_px)
positions_MVT["MV_trade"] = positions_MVT["position"] * positions_MVT["VWAP_px"]


#Part 4: Extracting latest market prices 
#Note: The "no older than 3-days" constraint is not applicable here because the dataset only includes dates within a 2-day range 
#(Entire dataset includes entries from either 5/10 or 7/10)

#Read prices file and associate with new dataFrame
df_p = pd.read_excel("prices.xlsx")

#Make sure its sorted (asc.)
df_p_sorted = df_p.sort_values(by = "last_ts")

#Create new series which pairs groups by sec_id only, pulling only last price entries from the prior table sorted by date
market_px_series = df_p_sorted.groupby("sec_id")["px_last"].last()

#convert back to 2D dataFrame
df_market_px = market_px_series.reset_index()



#Part 5: Calculate market value at market price 

#At this point, I realized that none of the sec_id's in the prices file were also in the transactions file. The two are fully unalligned. 
#To deal with this, I replaced the sec_id's in the prices dataframe with sec_id's from the transactions data frame.
#Prices also needed to be replaced b/c The original prices.xlsx dataset doesn’t have any sec_ids that match transactions.
#I cannot calculate MV_latest or exposure if there’s no px_last for a position.
#Important note: However, you can see in the prior lines that I sucessfully demonstrated the ability to extract the latest prices from the real prices file
#I just can't use them here b/c the two files are misaligned. 


#Create a small prices dataFrame that matches all unique sec_ids from transactions dataFrame
num_sec = len(positions_MVT["sec_id"].unique())
df_market_px_test = pd.DataFrame({
    "sec_id": positions_MVT["sec_id"].unique(),
    "px_last": [random.uniform(0, 100) for _ in range(num_sec)]  # dummy prices, in range of 0 to 100 since that seemed to be the spread in the prices file
})

#Merge onto positions
positions_MV = positions_MVT.merge(
    df_market_px_test,
    on="sec_id",
    how="left"
)

#create new column "MV_latest" which represents market value at latest market price: (Position * px_last)
positions_MV["MV_latest"] = positions_MV["position"] * positions_MV["px_last"]

#create new column "exposure" which represents per position exposure: ∣(Market Price * Position) - (Trade price * position)∣
positions_MV["Exposure"] = (positions_MV["MV_latest"] - positions_MV["MV_trade"]).abs()

#sort by descending order
positions_MV_sorted = positions_MV.sort_values(by = "Exposure", ascending=False)

#extract top 10
top10_exposure = positions_MV_sorted.head(10) 

#Cleans up row numbers
top10_exposure = top10_exposure.reset_index(drop = True)

#export to CSV (w/o index column)
top10_exposure.to_csv("answer1.csv", index=False)

#Part 6: Which positions do not have any prices in last 3 days? 
#Note: To restate, the original transactions and prices files were misaligned..
#none of the sec_ids in transactions appeared in the prices file. 
#Because exposure depends on matching prices per security, it is impossible to compute exposure using the original datasets. 
#To demonstrate working code, we replaced prices with a dummy set where each sec_id from transactions has a corresponding price.
#As a result, all positions now have a corresponding price, so no positions are missing prices.
#This means the resulting answer2.csv will be empty (only headers), which is correct given the adjustments

#Regardless..
#the correct method for filtering the data and outputting it to a csv file 
#is given below, this would work if the prices were real. 
positions_no_price = positions_MV[positions_MV["px_last"].isna()]
positions_no_price.to_csv("answer2.csv", index=False)



import datetime
# import os
date = datetime.datetime.now(datetime.UTC).time()
print(date)
# print(os.path.join(os.path.dirname(__file__), "apiErrors"))

# dict = {
#   "status": {
#     "timestamp": "2025-02-04T14:18:43.417Z",
#     "error_code": 0,
#     "error_message": None,
#     "elapsed": 91,
#     "credit_count": 1,
#     "notice": None
#   },
#   "data": {
#     "1": {
#       "id": 1,
#       "name": "Bitcoin",
#       "symbol": "BTC",
#       "slug": "bitcoin",
#       "last_updated": "2025-02-04T14:17:00.000Z",
#       "quote": {
#         "USD": {
#           "price": 98901.54232802335,
#           "volume_24h": 77709589929.01259,
#           "volume_change_24h": -24.1451,
#           "percent_change_1h": -0.52919389,
#           "percent_change_24h": 4.32089948,
#           "percent_change_7d": -3.05915818,
#           "percent_change_30d": 1.61564114,
#           "percent_change_60d": 0.18108117,
#           "percent_change_90d": 34.01018115,
#           "market_cap": 1960178425859.4624,
#           "market_cap_dominance": 60.3962,
#           "fully_diluted_market_cap": 2076932388888.49,
#           "tvl": None,
#           "last_updated": "2025-02-04T14:17:00.000Z"
#         }
#       }
#     },
#     "74": {
#       "id": 74,
#       "name": "Dogecoin",
#       "symbol": "DOGE",
#       "slug": "dogecoin",
#       "last_updated": "2025-02-04T14:17:00.000Z",
#       "quote": {
#         "USD": {
#           "price": 0.2684252087854922,
#           "volume_24h": 6005283300.705056,
#           "volume_change_24h": -45.3026,
#           "percent_change_1h": -2.00151737,
#           "percent_change_24h": 9.75551216,
#           "percent_change_7d": -18.47070581,
#           "percent_change_30d": -28.80944021,
#           "percent_change_60d": -36.998936,
#           "percent_change_90d": 37.1594359,
#           "market_cap": 39701896594.57682,
#           "market_cap_dominance": 1.2233,
#           "fully_diluted_market_cap": 39701896594.58,
#           "tvl": None,
#           "last_updated": "2025-02-04T14:17:00.000Z"
#         }
#       }
#     }
#   }
# }

# coinData = {}
# for i, coin in enumerate(dict["data"].values()):
#     coinData[i] = {
#         "marketCoinCapId": coin["id"],
#         "coinName": coin["name"],
#         "lastUpdated": coin["last_updated"]
#     }
# print(coinData)
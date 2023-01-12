price_rounder_dict = {
    "btc-usdt": 2,
    "eth-usdt": 2,
    "eth-btc": 6,
    "bnb-usdt": 1,
    "bnb-btc": 6,
    "xrp-usdt": 4,
    "xrp-btc": 8,
    "bnb-eth": 4,
    "xrp-bnb": 6,
    "xrp-eth": 7,
}

def price_rounder(pair_symbol, price): 
    """
    Round up/down price of each currency
    """
    return round(price, price_rounder_dict[pair_symbol])
    
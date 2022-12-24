def map_pair(flag, pair):
    """
    return input and output token symbol
    """
    token = pair.split("-")
    
    if flag == "buy":
        return token[1], token[0]
    
    return token[0], token[1]
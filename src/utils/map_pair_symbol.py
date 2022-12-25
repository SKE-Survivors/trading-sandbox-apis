def map_pair(flag, pair):
    """
    return input and output token symbol
    """
    try:
        token = pair.split("-")
        input_token, output_token = token[0], token[1]
    except Exception:
        raise Exception("Wrong pair symbol format")
    
    if flag == "buy":
        input_token, output_token = token[1], token[0]
    
    return input_token, output_token
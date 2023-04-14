def percent_change(old_value, new_value):
    if old_value == 0:
        if new_value == 0:
            return 0
        return 100
    return ((new_value - old_value) / old_value) * 100
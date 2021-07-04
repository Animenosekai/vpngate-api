def str_to_bool(value: str):
    return str(value).lower() in {'yes', 'true', 't', 'y', '1'}
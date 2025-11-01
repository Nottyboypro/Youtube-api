import random, string

def generate_api_key(owner: str):
    part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"NottyBoy-{part}"

def individual_serial(user) -> dict:
    return {
        'id': str(user['_id']),
        'gameName': user['gameName'],
        'tagLine': user['tagLine'],
        'first_blood_wr': user['first_blood_wr'],
        'ward_placed_wr': user['ward_placed_wr']
    }

def list_serial(users) -> list:
    return[individual_serial(user) for user in users]
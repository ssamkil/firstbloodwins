import httpx, time
from fastapi         import APIRouter
from config.database import usersCollection
from settings        import RIOT_API_KEY

router = APIRouter()

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6',
        'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://developer.riotgames.com',
        'X-Riot-Token': RIOT_API_KEY,
    }

async def get_match_ids(gameName: str, tagLine: str):

    ''' get puuid using in-game name & tag line '''

    URL = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}'

    response = httpx.get(URL, headers=headers)
    puuid = response.json()['puuid']

    URL2 = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=40'

    response = httpx.get(URL2, headers=headers)
    match_ids = response.json()

    return match_ids

async def winrate_calc(won_matches: int, total_matches: int):
    result = round(won_matches / total_matches, 1)

    return result

async def get_win_rate_data(match_ids):

    ''' get first blood + ward placed data and calculate win rate accordingly for each match '''

    first_blood_total = []
    ward_placed_total = []
    first_blood_role  = []
    pings_total       = []

    for match_id in match_ids:
        ward_placed_count = []
        total_pings_per_player = []

        URL = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}'
        response = httpx.get(URL, headers=headers)
        match_info = response.json()

        participants = match_info['info']['participants']
        team_data = match_info['info']['teams'][0]
        first_blood_bool = team_data['objectives']['champion']['first']

        if first_blood_bool and team_data['win']:
            first_blood_total.append(True)
        else:
            first_blood_total.append(False)

        for participant in participants:
            search_key = 'Pings'

            if participant['firstBloodKill']:
                first_blood_role.append(participant['teamPosition'])

            ping_count_per_player = [val for key, val in participant.items() if search_key in key]
            total_pings_per_player.append(sum(ping_count_per_player))
            ward_placed_count.append(participant['wardsPlaced'])

        if sum(ward_placed_count[0:5]) > sum(ward_placed_count[5:10]):
            if participants[0]['win']:
                ward_placed_total.append(True)
            else:
                ward_placed_total.append(False)
        elif sum(ward_placed_count[0:5]) < sum(ward_placed_count[5:10]):
            if participants[5]['win']:
                ward_placed_total.append(True)
            else:
                ward_placed_total.append(False)

        if total_pings_per_player[0:5] > sum(total_pings_per_player)[5:10]:
            if participants[0]['win']:
                pings_total.append(True)
            else:
                pings_total.append(False)
        elif total_pings_per_player[0:5] < sum(total_pings_per_player)[5:10]:
            if participants[5]['win']:
                pings_total.append(True)
            else:
                pings_total.append(False)

    total_match = len(first_blood_total)
    first_blood_win_rate = await winrate_calc(first_blood_total.count(True), total_match)
    ward_placed_win_rate = await winrate_calc(ward_placed_total.count(True), total_match)
    pings_called_win_rate = await winrate_calc(pings_total.count(True), total_match)
    Top = await winrate_calc(first_blood_role.count('TOP'), total_match)
    Jug = await winrate_calc(first_blood_role.count('JUNGLE'), total_match)
    Mid = await winrate_calc(first_blood_role.count('MIDDLE'), total_match)
    Adc = await winrate_calc(first_blood_role.count('BOTTOM'), total_match)
    Sup = await winrate_calc(first_blood_role.count('UTILITY'), total_match)

    first_blood_role_win_rate = {
        'TOP': Top,
        'JUNGLE': Jug,
        'MIDDLE': Mid,
        'BOTTOM': Adc,
        'SUPPORT': Sup
    }

    result = {
        'first_blood_win_rate': first_blood_win_rate,
        'ward_placed_win_rate': ward_placed_win_rate,
        'first_blood_role_win_rate': first_blood_role_win_rate,
        'pings_called_win_rate': pings_called_win_rate
    }

    return result

@router.get('/')
async def get_user_win_rate(gameName: str, tagLine: str):
    start = time.time()
    match_ids = await get_match_ids(gameName, tagLine)
    win_rate = await get_win_rate_data(match_ids)

    user = {
        'gameName': gameName,
        'tagLine': tagLine,
        'first_blood_wr': win_rate['first_blood_win_rate'],
        'ward_placed_wr': win_rate['ward_placed_win_rate']
    }

    if usersCollection.find_one({'gameName': gameName, 'tagLine': tagLine}):
        usersCollection.update_one({
            'gameName': gameName
        },
            {'$set': {
                'first_blood_wr': win_rate['first_blood_win_rate'],
                'ward_placed_wr': win_rate['ward_placed_win_rate']
                }
            }
        )
    else:
        usersCollection.insert_one(user)

    end = time.time()
    print(f'{end - start: .5f} sec')
    return win_rate
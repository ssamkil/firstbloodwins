import httpx, time, asyncio
from fastapi           import APIRouter, status
from fastapi.responses import JSONResponse
from config.database   import usersCollection
from settings          import RIOT_API_KEY


user = APIRouter(
    prefix='/user',
    tags=['User']
)

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

    URL2 = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=20'

    response = httpx.get(URL2, headers=headers)
    match_ids = response.json()

    return match_ids

async def winrate_calc(won_matches: int, total_matches: int, early_forfeit_matches: int):

    ''' basic win rate calculation '''

    result = round(won_matches / (total_matches - early_forfeit_matches), 1)

    return result

async def get_win_rate_data(match_id):

    ''' get first blood + ward placed data and calculate win rate accordingly for each match '''

    start = time.time()

    first_blood_total: bool
    ward_placed_total: bool
    pings_total      : bool
    first_blood_role = 'NONE'

    # for match_id in match_ids:
    ward_placed_count = []
    total_pings_per_player = []
    URL = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}'

    # async with httpx.AsyncClient() as client:
    #     response = await client.get(URL, headers=headers)
    response = httpx.get(URL, headers=headers)
    match_info = response.json()

    participants = match_info['info']['participants']
    team_data = match_info['info']['teams'][0]
    first_blood_bool = team_data['objectives']['champion']['first']

    if first_blood_bool and team_data['win']:
        first_blood_total = True
    else:
        first_blood_total = False

    for participant in participants:
        if participant['firstBloodKill']:
            first_blood_role = participant['teamPosition']

        search_key = 'Pings'
        ping_count_per_player = [val for key, val in participant.items() if search_key in key]
        total_pings_per_player.append(sum(ping_count_per_player))
        ward_placed_count.append(participant['wardsPlaced'])

    if sum(ward_placed_count[0:5]) >= sum(ward_placed_count[5:10]):
        if participants[0]['win']:
            ward_placed_total = True
        else:
            ward_placed_total = False
    elif sum(ward_placed_count[0:5]) <= sum(ward_placed_count[5:10]):
        if participants[5]['win']:
            ward_placed_total = True
        else:
            ward_placed_total = False

    if sum(total_pings_per_player[0:5]) >= sum(total_pings_per_player[5:10]):
        if participants[0]['win']:
            pings_total = True
        else:
            pings_total = False
    elif sum(total_pings_per_player[0:5]) <= sum(total_pings_per_player[5:10]):
        if participants[5]['win']:
            pings_total = True
        else:
            pings_total = False

    result = {
        'first_blood_total' : first_blood_total,
        'ward_placed_total' : ward_placed_total,
        'first_blood_role' : first_blood_role,
        'pings_total' : pings_total
    }

    end = time.time()
    print(f'{end - start: .5f} sec')

    return result

async def make_multiple_requests(match_ids):

    ''' async programming to perform multiple API calls concurrently '''

    first_blood_total = []
    ward_placed_total = []
    first_blood_role  = []
    pings_total       = []

    cycle = len(match_ids) // 20
    leftover = len(match_ids) % 20

    if len(match_ids) <= 20:
        for match_id in match_ids:
            match_data = await get_win_rate_data(match_id)
            print(match_data)
            first_blood_total.append(match_data['first_blood_total'])
            first_blood_role.append(match_data['first_blood_role'])
            ward_placed_total.append(match_data['ward_placed_total'])
            pings_total.append(match_data['pings_total'])
    else:
        for i in range(cycle):
            for match_id in match_ids[0+(i*20):20+(i*20)]:
                match_data = await get_win_rate_data(match_id)
                first_blood_total.append(match_data['first_blood_total'])
                first_blood_role.append(match_data['first_blood_role'])
                ward_placed_total.append(match_data['ward_placed_total'])
                pings_total.append(match_data['pings_total'])
        if leftover > 0:
            for match_id in match_ids[cycle*20:20+leftover+(cycle*20)]:
                match_data = await get_win_rate_data(match_id)
                first_blood_total.append(match_data['first_blood_total'])
                first_blood_role.append(match_data['first_blood_role'])
                ward_placed_total.append(match_data['ward_placed_total'])
                pings_total.append(match_data['pings_total'])

    total_match = len(first_blood_total)
    early_forfeit_match = first_blood_role.count('NONE')
    first_blood_win_rate = await winrate_calc(first_blood_total.count(True), total_match, early_forfeit_match)
    ward_placed_win_rate = await winrate_calc(ward_placed_total.count(True), total_match, early_forfeit_match)
    pings_called_win_rate = await winrate_calc(pings_total.count(True), total_match, early_forfeit_match)
    Top = await winrate_calc(first_blood_role.count('TOP'), total_match, early_forfeit_match)
    Jug = await winrate_calc(first_blood_role.count('JUNGLE'), total_match, early_forfeit_match)
    Mid = await winrate_calc(first_blood_role.count('MIDDLE'), total_match, early_forfeit_match)
    Adc = await winrate_calc(first_blood_role.count('BOTTOM'), total_match, early_forfeit_match)
    Sup = await winrate_calc(first_blood_role.count('UTILITY'), total_match, early_forfeit_match)

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

@user.get('')
async def get_user_win_rate(gameName: str, tagLine: str):
    try:
        match_ids = await get_match_ids(gameName, tagLine)
        win_rate = await make_multiple_requests(match_ids)

        user = {
            'gameName': gameName,
            'tagLine': tagLine,
            'first_blood_wr': win_rate['first_blood_win_rate'],
            'ward_placed_wr': win_rate['ward_placed_win_rate'],
            'first_blood_role_wr': win_rate['first_blood_role_win_rate'],
            'pings_called_wr': win_rate['pings_called_win_rate']
        }

        if usersCollection.find_one({'gameName': gameName, 'tagLine': tagLine}):
            usersCollection.update_one({
                'gameName': gameName
            },
                {'$set': {
                    'first_blood_wr': win_rate['first_blood_win_rate'],
                    'ward_placed_wr': win_rate['ward_placed_win_rate'],
                    'first_blood_role_wr': win_rate['first_blood_role_win_rate'],
                    'pings_called_wr': win_rate['pings_called_win_rate']
                    }
                }
            )

            return JSONResponse({'MESSAGE': 'SUCCESS', 'RESULT': win_rate}, status_code=status.HTTP_200_OK)

        else:
            usersCollection.insert_one(user)
            return JSONResponse({'MESSAGE': 'CREATED', 'RESULT': win_rate}, status_code=status.HTTP_201_CREATED)

    except ValueError as e:
        return JSONResponse({'ERROR': e.message}, status_code=status.HTTP_400_BAD_REQUEST)
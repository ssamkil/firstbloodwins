from fastapi import FastAPI
import httpx, leaguepedia_parser as lp, time

app = FastAPI()

RIOT_API_KEY = 'RGAPI-64a5d535-afb6-4e62-8a7f-cd7b10530095'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6',
        'Accept-Charset': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://developer.riotgames.com',
        'X-Riot-Token': RIOT_API_KEY,
    }

async def get_match_ids(gameName, tagLine):

    ''' get puuid using in-game name & tag line '''

    URL = f'https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}'

    response = httpx.get(URL, headers=headers)
    puuid = response.json()['puuid']

    URL2 = f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=10'

    response = httpx.get(URL2, headers=headers)
    match_ids = response.json()

    return match_ids

async def get_first_kill_data(match_ids):

    ''' get first blood data for each match from the match ids already retrieved '''

    total = []

    for match_id in match_ids:
        URL = f'https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}'
        response = httpx.get(URL, headers=headers)
        match_info = response.json()

        participants = match_info['info']['participants']
        for participant in participants:
            if participant['firstBloodKill'] == True:
                first_blood_participant = participant
                first_blood_win_bool = first_blood_participant['win']
                total.append(first_blood_win_bool)

    first_kill_win_rate = round(sum(total) / len(total), 1)

    return first_kill_win_rate

@app.get('/')
async def test(gameName: str, tagLine: str):
    start = time.time()
    match_ids = await get_match_ids(gameName, tagLine)
    result = await get_first_kill_data(match_ids)
    end = time.time()
    print(f'{end - start: .5f} sec')

    return result
# Vedic astrological calendar for farming
from datetime import datetime

TITHI_NAMES = [
    'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
    'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
    'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi', 'Amavasya/Purnima'
]

def get_paksha():
    today = datetime.now()
    new_moon = datetime(2026, 5, 1)
    days_since = (today - new_moon).days
    lunar_day = days_since % 30
    if lunar_day < 15:
        return 'waxing', 'Shukla Paksha - good for sowing'
    else:
        return 'waning', 'Krishna Paksha - good for harvesting'

def get_farming_muhurta():
    paksha, desc = get_paksha()
    if paksha == 'waxing':
        return {'activity': 'sowing', 'reason': 'Moon waxing increases sap flow in plants'}
    else:
        return {'activity': 'harvesting/ploughing', 'reason': 'Moon waning draws energy to roots'}

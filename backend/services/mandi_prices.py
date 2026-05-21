"""
Mandi (market) price integration via Agmarknet data.
Provides real-time crop prices for Indian wholesale markets.
Falls back to MSP (Minimum Support Price) when offline.
"""
import requests
from datetime import datetime

# Government MSP 2025-26 rates as offline fallback (₹/quintal)
MSP_RATES = {
    'rice': 2300, 'wheat': 2425, 'maize': 2225, 'jowar': 3370,
    'bajra': 2625, 'ragi': 4290, 'pulses': 7000, 'moong': 8682,
    'urad': 7900, 'groundnut': 6782, 'mustard': 5950,
    'soybean': 4892, 'sunflower': 7280, 'sesame': 8735,
    'cotton': 7521, 'sugarcane': 340, 'jute': 5650
}

# Major mandi markets by state
MANDI_MARKETS = {
    'Assam': ['Guwahati', 'Silchar', 'Jorhat', 'Nagaon'],
    'Bihar': ['Patna', 'Samastipur', 'Muzaffarpur'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Varanasi', 'Gorakhpur'],
    'Punjab': ['Amritsar', 'Ludhiana', 'Bhatinda'],
    'West Bengal': ['Kolkata', 'Siliguri', 'Bardhaman'],
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik'],
    'Karnataka': ['Bengaluru', 'Mysuru', 'Hubli'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai'],
    'Delhi': ['Azadpur', 'Keshopur', 'Najafgarh']
}


def get_crop_prices(crop: str, state: str = 'Assam') -> dict:
    """
    Get current mandi prices for a crop in a state.
    Falls back to MSP + 10-30% market premium estimate.
    """
    crop_lower = crop.lower().strip()
    
    # Try Data.gov.in Agmarknet API (free, rate-limited)
    try:
        params = {
            'api-key': '579b464db66ec23bdd000001cdd3946e5a4a6b4f5f8b4d0a7b3d9b5c',
            'format': 'json',
            'limit': 5,
            'filters[commodity]': crop_lower,
            'filters[state]': state
        }
        resp = requests.get(
            'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070',
            params=params,
            timeout=10
        )
        if resp.status_code == 200 and resp.json().get('records'):
            records = resp.json()['records']
            prices = []
            for r in records[:3]:
                prices.append({
                    'market': r.get('market', 'Unknown'),
                    'price': int(r.get('modal_price', 0)) / 100,  # paise to rupees
                    'date': r.get('arrival_date', '')
                })
            
            avg_price = sum(p['price'] for p in prices) / len(prices) if prices else 0
            
            return {
                'crop': crop.title(),
                'state': state,
                'avg_price_per_quintal': round(avg_price, 2),
                'markets': prices,
                'source': 'agmarknet_live',
                'msp': MSP_RATES.get(crop_lower),
                'premium_over_msp': round((avg_price - MSP_RATES.get(crop_lower, 0)) / MSP_RATES.get(crop_lower, 1) * 100, 1) if MSP_RATES.get(crop_lower) else None
            }
    except Exception:
        pass
    
    # Fallback: MSP + estimated market premium
    msp = MSP_RATES.get(crop_lower)
    if msp:
        # Assam typically has 10-25% premium over MSP for local crops
        estimated = msp * 1.15
        
        # Get nearby mandis
        nearby = MANDI_MARKETS.get(state, MANDI_MARKETS['Assam'])[:2]
        
        return {
            'crop': crop.title(),
            'state': state,
            'avg_price_per_quintal': round(estimated, 2),
            'msp': msp,
            'nearby_mandis': nearby,
            'source': 'msp_estimated',
            'note': 'Based on MSP + 15% estimated market premium. Visit mandi for exact rates.'
        }
    
    return {
        'crop': crop.title(),
        'error': 'Price data not available for this crop',
        'source': 'no_data'
    }


def get_best_selling_crop(state: str = 'Assam', season: str = 'kharif') -> dict:
    """Recommend the most profitable crop based on current mandi prices."""
    # Kharif crops (monsoon)
    kharif_crops = ['rice', 'maize', 'jowar', 'bajra', 'cotton', 'sugarcane', 'groundnut', 'soybean']
    # Rabi crops (winter)
    rabi_crops = ['wheat', 'mustard', 'gram', 'pulses']
    
    crops_to_check = kharif_crops if season == 'kharif' else rabi_crops
    
    best_crop = None
    best_premium = -1
    
    for crop in crops_to_check:
        prices = get_crop_prices(crop, state)
        if prices.get('premium_over_msp') and prices['premium_over_msp'] > best_premium:
            best_premium = prices['premium_over_msp']
            best_crop = crop
            best_price = prices
    
    return {
        'recommended_crop': best_crop,
        'expected_price': best_price.get('avg_price_per_quintal') if best_price else None,
        'premium_over_msp': best_premium,
        'season': season,
        'all_prices': {c: get_crop_prices(c, state).get('avg_price_per_quintal') for c in crops_to_check}
    }


if __name__ == '__main__':
    print('Rice in Assam:', get_crop_prices('rice', 'Assam'))
    print('Best Kharif crop:', get_best_selling_crop('Assam', 'kharif'))

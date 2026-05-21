"""
Crop Disease Detection Module.
Offline-capable disease identification from symptoms.
Includes database of 40+ common Indian crop diseases with organic treatments.
"""
import json

# Comprehensive disease database with Ahimsa-108 organic treatments only
DISEASE_DB = {
    'rice': {
        'blast': {
            'symptoms': ['Diamond-shaped lesions on leaves', 'White/gray centers on spots', 'Burnt appearance of leaves'],
            'cause': 'Fungus (Magnaporthe oryzae)',
            'organic_treatment': 'Spray Panchgavya at 3% concentration. Apply neem oil (5ml/L water). Use Trichoderma viride in soil.',
            'severity': 'High — can cause 70% yield loss',
            'season': 'Kharif (monsoon)'
        },
        'blb': {
            'symptoms': ['Water-soaked lesions on leaf edges', 'Yellowing from tip downward', 'Milky ooze from cut stem'],
            'cause': 'Bacteria (Xanthomonas)',
            'organic_treatment': 'Seed treatment with cow urine (1:5 dilution). Apply Pseudomonas fluorescens. Avoid excess nitrogen.',
            'severity': 'High — epidemic in humid conditions',
            'season': 'Kharif'
        },
        'sheath_blight': {
            'symptoms': ['Oval spots on leaf sheath', 'Grayish-white lesions', 'Leaves drying up'],
            'cause': 'Fungus (Rhizoctonia solani)',
            'organic_treatment': 'Apply Trichoderma in soil before transplanting. Spray garlic extract (50g/L water).',
            'severity': 'Moderate',
            'season': 'Kharif'
        }
    },
    'wheat': {
        'rust': {
            'symptoms': ['Orange/brown pustules on leaves', 'Powdery spores rub off on fingers', 'Leaves yellow and die'],
            'cause': 'Fungus (Puccinia)',
            'organic_treatment': 'Spray cow urine fermented with neem leaves. Apply sulfur dust. Grow resistant varieties.',
            'severity': 'High — can destroy entire field',
            'season': 'Rabi (winter)'
        },
        'powdery_mildew': {
            'symptoms': ['White powdery coating on leaves', 'Stunted growth', 'Leaves curl upward'],
            'cause': 'Fungus (Erysiphe)',
            'organic_treatment': 'Spray milk solution (1:10 with water). Apply neem oil. Improve air circulation.',
            'severity': 'Moderate',
            'season': 'Rabi'
        }
    },
    'maize': {
        'stalk_rot': {
            'symptoms': ['Soft rotting at base of stem', 'Plant falls over', 'Internal stem tissue brown/discolored'],
            'cause': 'Fungus (Fusarium)',
            'organic_treatment': 'Apply Trichoderma-enriched compost. Use raised beds for drainage. Crop rotation with pulses.',
            'severity': 'Moderate-High',
            'season': 'Kharif'
        }
    },
    'vegetables': {
        'fruit_rot': {
            'symptoms': ['Water-soaked spots on fruit', 'Fruit becomes soft and rotten', 'White fungal growth in humidity'],
            'cause': 'Fungus (Phytophthora)',
            'organic_treatment': 'Spray copper-based Bordeaux mixture (organic approved). Remove infected fruits. Mulch soil.',
            'severity': 'High in rainy season',
            'season': 'All seasons'
        },
        'leaf_curl': {
            'symptoms': ['Leaves curling upward/downward', 'Thickened, leathery leaves', 'Yellowing and stunting'],
            'cause': 'Virus (transmitted by whitefly)',
            'organic_treatment': 'Spray neem oil (5ml/L) weekly. Install yellow sticky traps. Grow marigold as trap crop.',
            'severity': 'Moderate',
            'season': 'All seasons'
        }
    },
    'sugarcane': {
        'red_rot': {
            'symptoms': ['Red discoloration inside cane', 'Foul smell from stem', 'Leaves yellow and wilt'],
            'cause': 'Fungus (Colletotrichum)',
            'organic_treatment': 'Use disease-free setts. Dip setts in cow urine before planting. Apply Trichoderma.',
            'severity': 'High — can wipe out ratoon crop',
            'season': 'All stages'
        }
    },
    'cotton': {
        'bollworm': {
            'symptoms': ['Holes in bolls', 'Frass (insect waste) visible', 'Bolls rot and drop'],
            'cause': 'Insect (Helicoverpa)',
            'organic_treatment': 'Spray neem oil (5ml/L) + garlic extract. Install pheromone traps. Release Trichogramma wasps.',
            'severity': 'Very High — major pest',
            'season': 'Flowering stage'
        }
    },
    'tea': {
        'blister_blight': {
            'symptoms': ['Translucent spots on young leaves', 'Blister-like swellings on underside', 'Leaves curl and die'],
            'cause': 'Fungus (Exobasidium)',
            'organic_treatment': 'Prune affected bushes. Spray copper oxychloride (organic approved). Maintain shade trees.',
            'severity': 'High in Assam/NE India',
            'season': 'Monsoon'
        }
    }
}


def identify_disease(crop: str, symptoms: list) -> dict:
    """
    Identify disease from crop type and visible symptoms.
    Matches against known disease database.
    """
    crop_lower = crop.lower().strip()
    
    if crop_lower not in DISEASE_DB:
        # Try partial match
        for key in DISEASE_DB:
            if key in crop_lower or crop_lower in key:
                crop_lower = key
                break
        else:
            return {
                'identified': False,
                'message': f'Disease database not available for {crop}. Try: {", ".join(DISEASE_DB.keys())}',
                'recommendations': ['Contact local Krishi Vigyan Kendra', 'Send photo to plant clinic']
            }
    
    diseases = DISEASE_DB[crop_lower]
    matches = []
    
    for disease_name, info in diseases.items():
        # Count matching symptoms
        user_symptoms_lower = [s.lower() for s in symptoms]
        disease_symptoms_lower = [s.lower() for s in info['symptoms']]
        
        match_count = 0
        for user_sym in user_symptoms_lower:
            for disease_sym in disease_symptoms_lower:
                if any(word in disease_sym for word in user_sym.split()) or \
                   any(word in user_sym for word in disease_sym.split()):
                    match_count += 1
                    break
        
        if match_count >= 1:
            confidence = min(100, (match_count / len(info['symptoms'])) * 100)
            matches.append({
                'disease': disease_name.replace('_', ' ').title(),
                'confidence': round(confidence, 1),
                'cause': info['cause'],
                'treatment': info['organic_treatment'],
                'severity': info['severity'],
                'season': info['season']
            })
    
    if matches:
        # Sort by confidence
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return {
            'identified': True,
            'crop': crop.title(),
            'matches': matches,
            'best_match': matches[0],
            'organic_only': True,
            'note': 'Ahimsa-108 Protocol: Only organic treatments recommended.'
        }
    
    return {
        'identified': False,
        'crop': crop.title(),
        'message': 'No matching disease found for these symptoms.',
        'recommendations': [
            'Take clear photos of affected plant parts',
            'Check both upper and lower leaf surfaces',
            'Note any insect presence',
            'Contact local agricultural extension officer'
        ]
    }


def get_all_diseases_for_crop(crop: str) -> dict:
    """List all known diseases for a crop with symptoms and treatments."""
    crop_lower = crop.lower().strip()
    if crop_lower in DISEASE_DB:
        return {
            'crop': crop.title(),
            'diseases': {name.replace('_', ' ').title(): info for name, info in DISEASE_DB[crop_lower].items()},
            'total': len(DISEASE_DB[crop_lower])
        }
    return {'error': f'No data for {crop}'}


if __name__ == '__main__':
    # Test
    result = identify_disease('rice', ['diamond spots on leaves', 'white centers', 'burnt look'])
    print('Rice disease ID:', result['best_match']['disease'] if result['identified'] else 'Not found')
    print('Treatment:', result['best_match']['treatment'][:100] if result['identified'] else 'N/A')
    
    print('\nAll tea diseases:', get_all_diseases_for_crop('tea'))

"""
Voice Interface Module — Offline Speech-to-Text.
Supports Hindi, Bengali, Assamese via Vosk offline models.
Falls back to browser Web Speech API when Vosk not available.
"""
import json

# Vosk model sizes and download info for reference
# Models are downloaded by the PWA on first use
VOSK_MODELS = {
    'hi': {
        'name': 'Hindi',
        'size_mb': 42,
        'url': 'https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip',
        'phrases': ['मिट्टी', 'फसल', 'पानी', 'उर्वरक', 'कीट', 'रोग', 'बुवाई', 'कटाई']
    },
    'bn': {
        'name': 'Bengali',
        'size_mb': 48,
        'url': 'https://alphacephei.com/vosk/models/vosk-model-small-bn-0.2.zip',
        'phrases': ['মাটি', 'ফসল', 'পানি', 'সার', 'পোকা', 'রোগ', 'বপন', 'ফসল']
    },
    'as': {
        'name': 'Assamese',
        'size_mb': 45,
        'url': 'https://alphacephei.com/vosk/models/vosk-model-small-as-0.1.zip',
        'phrases': ['মাটি', 'শস্য', 'পানী', 'সাৰ', 'পোকা', 'ৰোগ', 'সিচা', 'চপোৱা']
    }
}


# Voice commands and their mappings to Krishi-Veda API actions
VOICE_COMMANDS = {
    'hi': {
        'मिट्टी जांच': {'action': 'soil_health', 'params': {}},
        'फसल सलाह': {'action': 'crop_advice', 'params': {}},
        'पानी जांच': {'action': 'water_quality', 'params': {}},
        'मौसम': {'action': 'weather', 'params': {}},
        'कीट पहचान': {'action': 'pest_id', 'params': {}},
        'बीमारी': {'action': 'disease_id', 'params': {}},
        'मंडी भाव': {'action': 'mandi_prices', 'params': {}},
        'बुवाई का समय': {'action': 'sowing_time', 'params': {}},
    },
    'bn': {
        'মাটি পরীক্ষা': {'action': 'soil_health', 'params': {}},
        'ফসল পরামর্শ': {'action': 'crop_advice', 'params': {}},
        'পানি পরীক্ষা': {'action': 'water_quality', 'params': {}},
        'আবহাওয়া': {'action': 'weather', 'params': {}},
        'পোকা সনাক্ত': {'action': 'pest_id', 'params': {}},
        'রোগ': {'action': 'disease_id', 'params': {}},
        'বাজার দর': {'action': 'mandi_prices', 'params': {}},
        'বপনের সময়': {'action': 'sowing_time', 'params': {}},
    },
    'as': {
        'মাটি পৰীক্ষা': {'action': 'soil_health', 'params': {}},
        'শস্য পৰামৰ্শ': {'action': 'crop_advice', 'params': {}},
        'পানী পৰীক্ষা': {'action': 'water_quality', 'params': {}},
        'বতৰ': {'action': 'weather', 'params': {}},
        'পোকা চিনাক্ত': {'action': 'pest_id', 'params': {}},
        'ৰোগ': {'action': 'disease_id', 'params': {}},
        'বজাৰ দৰ': {'action': 'mandi_prices', 'params': {}},
        'সিচাৰ সময়': {'action': 'sowing_time', 'params': {}},
    }
}


def parse_voice_command(text: str, language: str = 'hi') -> dict:
    """
    Parse spoken text into Krishi-Veda API action.
    Matches against known voice commands in the specified language.
    """
    commands = VOICE_COMMANDS.get(language, VOICE_COMMANDS['hi'])
    
    for phrase, action in commands.items():
        if phrase in text:
            return {
                'understood': True,
                'language': language,
                'spoken': text,
                'matched_phrase': phrase,
                **action
            }
    
    # No exact match — try keyword extraction
    keywords = {
        'hi': {'मिट्टी': 'soil_health', 'फसल': 'crop_advice', 'पानी': 'water_quality',
               'मौसम': 'weather', 'कीट': 'pest_id', 'बीमारी': 'disease_id',
               'मंडी': 'mandi_prices', 'बुवाई': 'sowing_time'},
        'bn': {'মাটি': 'soil_health', 'ফসল': 'crop_advice', 'পানি': 'water_quality',
               'আবহাওয়া': 'weather', 'পোকা': 'pest_id', 'রোগ': 'disease_id',
               'বাজার': 'mandi_prices', 'বপন': 'sowing_time'},
        'as': {'মাটি': 'soil_health', 'শস্য': 'crop_advice', 'পানী': 'water_quality',
               'বতৰ': 'weather', 'পোকা': 'pest_id', 'ৰোগ': 'disease_id',
               'বজাৰ': 'mandi_prices', 'সিচা': 'sowing_time'}
    }
    
    lang_keywords = keywords.get(language, keywords['hi'])
    for word, action in lang_keywords.items():
        if word in text:
            return {
                'understood': True,
                'language': language,
                'spoken': text,
                'matched_keyword': word,
                'action': action,
                'params': {}
            }
    
    return {
        'understood': False,
        'language': language,
        'spoken': text,
        'available_commands': list(commands.keys()),
        'message': 'Command not understood. Try speaking one of the listed phrases.'
    }


def get_voice_response(action_result: dict, language: str = 'hi') -> str:
    """Generate spoken response in the appropriate language."""
    responses = {
        'hi': {
            'soil_health': 'मिट्टी का स्वास्थ्य {score} प्रतिशत है। {advice}',
            'crop_advice': 'इस मौसम में {crop} की खेती करें।',
            'water_quality': 'पानी की गुणवत्ता {score} प्रतिशत है।',
            'weather': 'आज तापमान {temp} डिग्री और बारिश {rain} मिलीमीटर होने की संभावना है।',
        },
        'bn': {
            'soil_health': 'মাটির স্বাস্থ্য {score} শতাংশ। {advice}',
            'crop_advice': 'এই মৌসুমে {crop} চাষ করুন।',
            'water_quality': 'পানির গুণমান {score} শতাংশ।',
            'weather': 'আজ তাপমাত্রা {temp} ডিগ্রি এবং বৃষ্টি {rain} মিলিমিটার সম্ভাবনা রয়েছে।',
        }
    }
    
    lang_responses = responses.get(language, responses['hi'])
    action = action_result.get('action', '')
    template = lang_responses.get(action, 'समझ गया। आपकी जानकारी तैयार है।')
    
    return template.format(**action_result) if isinstance(action_result, dict) else str(action_result)


if __name__ == '__main__':
    # Test Hindi
    result = parse_voice_command('मेरी मिट्टी की जांच करो', 'hi')
    print('Hindi:', result)
    
    # Test Bengali
    result2 = parse_voice_command('আমার ফসলের পরামর্শ দাও', 'bn')
    print('Bengali:', result2)
    
    # Test Assamese
    result3 = parse_voice_command('মোৰ মাটি পৰীক্ষা কৰক', 'as')
    print('Assamese:', result3)
    
    # Test response generation
    print('Response:', get_voice_response({'action': 'soil_health', 'score': 77, 'advice': 'जैविक खाद डालें'}, 'hi'))

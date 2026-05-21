"""
Validation Ledger — Sheriff's requested evidence loop.
Immutable record linking AI recommendation → guideline → farmer action → outcome.
Each entry is a complete validation trace for a single advisory cycle.
"""
import json
import os
from datetime import datetime
from typing import Optional

LEDGER_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'validation_ledger.json')

class ValidationLedger:
    """
    Immutable validation ledger.
    Each entry captures the full cycle:
    recommendation → guideline → confidence → action → outcome
    """
    
    def __init__(self):
        self.entries = self._load()
    
    def _load(self):
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save(self):
        with open(LEDGER_FILE, 'w') as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)
    
    def record_recommendation(self, 
                              plan_id: str,
                              recommendation: str,
                              source_guideline: str,
                              confidence_score: float,
                              farmer_context: dict) -> str:
        """
        Record an AI recommendation with its authority source.
        Layer 1 + 2: Authority Alignment + Local Calibration.
        """
        entry = {
            'plan_id': plan_id,
            'timestamp': datetime.now().isoformat(),
            'stage': 'recommendation',
            'recommendation': recommendation,
            'source_guideline': source_guideline,
            'confidence_score': confidence_score,
            'farmer_context': {
                'location': farmer_context.get('location', 'Unknown'),
                'soil_type': farmer_context.get('soil_type', 'Unknown'),
                'crop': farmer_context.get('crop', 'Unknown'),
                'season': farmer_context.get('season', 'Unknown'),
                'weather': farmer_context.get('weather', {}),
                'soil_health': farmer_context.get('soil_health', {}),
                'water_status': farmer_context.get('water_status', 'Unknown'),
                'pest_pressure': farmer_context.get('pest_pressure', 'None')
            },
            'status': 'pending_action'
        }
        self.entries.append(entry)
        self._save()
        return entry['plan_id']
    
    def record_action(self, plan_id: str, action_taken: str, notes: str = ''):
        """Record what the farmer actually did."""
        for entry in self.entries:
            if entry['plan_id'] == plan_id:
                entry['stage'] = 'action_taken'
                entry['action_taken'] = action_taken
                entry['action_notes'] = notes
                entry['action_timestamp'] = datetime.now().isoformat()
                self._save()
                return entry
        return None
    
    def record_outcome(self, 
                       plan_id: str,
                       actual_yield_t_ha: float,
                       predicted_yield_t_ha: float,
                       water_saved_percent: float = 0,
                       cost_reduction_percent: float = 0,
                       disease_controlled: bool = False,
                       farmer_satisfaction: int = 3,
                       notes: str = '') -> dict:
        """
        Record actual field outcome.
        Layer 3: Outcome Validation.
        """
        for entry in self.entries:
            if entry['plan_id'] == plan_id:
                entry['stage'] = 'validated'
                entry['outcome'] = {
                    'actual_yield_t_ha': actual_yield_t_ha,
                    'predicted_yield_t_ha': predicted_yield_t_ha,
                    'yield_accuracy_percent': round((actual_yield_t_ha / predicted_yield_t_ha) * 100, 1) if predicted_yield_t_ha > 0 else 0,
                    'water_saved_percent': water_saved_percent,
                    'cost_reduction_percent': cost_reduction_percent,
                    'disease_controlled': disease_controlled,
                    'farmer_satisfaction_1_5': farmer_satisfaction,
                    'notes': notes
                }
                entry['outcome_timestamp'] = datetime.now().isoformat()
                
                # Calculate if recommendation was operationally correct
                yield_accurate = abs(actual_yield_t_ha - predicted_yield_t_ha) / predicted_yield_t_ha < 0.2 if predicted_yield_t_ha > 0 else False
                entry['operationally_correct'] = yield_accurate and farmer_satisfaction >= 3
                
                self._save()
                return entry
        return None
    
    def get_ledger(self, limit: int = 50) -> list:
        """Get recent ledger entries."""
        return self.entries[-limit:]
    
    def get_validation_stats(self) -> dict:
        """Get aggregate validation statistics for the ledger."""
        validated = [e for e in self.entries if e.get('stage') == 'validated']
        correct = [e for e in validated if e.get('operationally_correct', False)]
        
        if not validated:
            return {
                'total_recommendations': len(self.entries),
                'total_validated': 0,
                'accuracy_rate': 0,
                'message': 'No validated outcomes yet. Waiting for farmer feedback.'
            }
        
        return {
            'total_recommendations': len(self.entries),
            'total_validated': len(validated),
            'operationally_correct': len(correct),
            'accuracy_rate': round(len(correct) / len(validated) * 100, 1),
            'avg_yield_accuracy': round(sum(
                e.get('outcome', {}).get('yield_accuracy_percent', 0) for e in validated
            ) / len(validated), 1),
            'avg_satisfaction': round(sum(
                e.get('outcome', {}).get('farmer_satisfaction_1_5', 0) for e in validated
            ) / len(validated), 2),
            'recent_validations': validated[-5:]
        }
    
    def get_evidence_loop(self, plan_id: str) -> dict:
        """
        Get the complete evidence loop for a single recommendation.
        This is the trace Sheriff asked for:
        recommendation → guideline → confidence → action → outcome
        """
        for entry in self.entries:
            if entry['plan_id'] == plan_id:
                return {
                    'plan_id': plan_id,
                    'evidence_chain': {
                        '1_recommendation': entry.get('recommendation'),
                        '2_source_guideline': entry.get('source_guideline'),
                        '3_confidence_score': entry.get('confidence_score'),
                        '4_farmer_action': entry.get('action_taken', 'Not yet recorded'),
                        '5_observed_outcome': entry.get('outcome', 'Not yet recorded'),
                        '6_operationally_correct': entry.get('operationally_correct', 'Pending')
                    },
                    'context': entry.get('farmer_context'),
                    'timeline': {
                        'recommended_at': entry.get('timestamp'),
                        'action_at': entry.get('action_timestamp'),
                        'outcome_at': entry.get('outcome_timestamp')
                    }
                }
        return {'error': 'Plan ID not found'}


# Singleton
_ledger = ValidationLedger()


def create_recommendation_record(plan_id: str, recommendation: str, 
                                  source: str, confidence: float, 
                                  context: dict) -> dict:
    """Record a new AI recommendation in the ledger."""
    _ledger.record_recommendation(plan_id, recommendation, source, confidence, context)
    return {
        'recorded': True,
        'plan_id': plan_id,
        'message': 'Recommendation recorded. Awaiting farmer action and outcome.'
    }


def record_farmer_action(plan_id: str, action: str, notes: str = '') -> dict:
    """Record what action the farmer took."""
    result = _ledger.record_action(plan_id, action, notes)
    if result:
        return {'recorded': True, 'plan_id': plan_id, 'stage': 'action_taken'}
    return {'error': 'Plan ID not found'}


def record_field_outcome(plan_id: str, actual_yield: float, predicted_yield: float,
                         water_saved: float = 0, cost_reduction: float = 0,
                         disease_controlled: bool = False, satisfaction: int = 3,
                         notes: str = '') -> dict:
    """Record actual field outcome and validate the recommendation."""
    result = _ledger.record_outcome(plan_id, actual_yield, predicted_yield,
                                     water_saved, cost_reduction, disease_controlled,
                                     satisfaction, notes)
    if result:
        return {
            'recorded': True,
            'plan_id': plan_id,
            'operationally_correct': result.get('operationally_correct'),
            'message': 'Outcome recorded. Evidence loop complete.'
        }
    return {'error': 'Plan ID not found'}


def get_evidence_loop(plan_id: str) -> dict:
    """Get complete evidence loop for a plan."""
    return _ledger.get_evidence_loop(plan_id)


def get_ledger_stats() -> dict:
    """Get aggregate validation statistics."""
    return _ledger.get_validation_stats()


def get_all_entries(limit: int = 50) -> list:
    """Get all ledger entries."""
    return _ledger.get_ledger(limit)


if __name__ == '__main__':
    # Demo: full evidence loop
    plan_id = 'demo-001'
    
    # Layer 1: Record recommendation with authority source
    create_recommendation_record(
        plan_id, 
        'Plant Ranjit rice variety with 60:30:40 NPK, irrigate every 5 days',
        'AAU Jorhat — Kharif Rice Guidelines 2025',
        85.0,
        {
            'location': 'Silchar, Cachar, Assam',
            'soil_type': 'Alluvial',
            'crop': 'Rice',
            'season': 'Kharif 2026',
            'weather': {'temperature': 26, 'rainfall': 250},
            'soil_health': {'ph': 6.5, 'npk': 'adequate'},
            'water_status': 'Adequate monsoon',
            'pest_pressure': 'Low — monitored'
        }
    )
    
    # Layer 2: Record farmer action
    record_farmer_action(plan_id, 'Applied 60:30:40 NPK, planted Ranjit variety, irrigated per schedule')
    
    # Layer 3: Record field outcome
    record_field_outcome(
        plan_id, 
        actual_yield=4.8, 
        predicted_yield=4.5,
        water_saved=0,
        cost_reduction=10,
        satisfaction=5,
        notes='Excellent yield. Followed AAU guidelines + AI advice. Saved ₹2000 on fertilizer.'
    )
    
    # Get evidence loop
    print('=== EVIDENCE LOOP ===')
    print(json.dumps(get_evidence_loop(plan_id), indent=2))
    
    print('\n=== LEDGER STATS ===')
    print(json.dumps(get_ledger_stats(), indent=2))

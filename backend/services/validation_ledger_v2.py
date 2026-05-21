"""
Validation Ledger v2 — Sheriff's Advanced Evidence Model.
Implements all 5 validation requirements for operational trust.

1. Ground-truth quality with evidence types
2. Counterfactual baseline comparison
3. Confidence calibration tracking
4. Partial adoption / deviation tracking
5. Stratified validation by crop, district, soil, season
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

LEDGER_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'validation_ledger_v2.json')

# Evidence quality tiers
EVIDENCE_TIERS = {
    'tier_1_self_report': {'weight': 0.3, 'description': 'Farmer self-reported without verification'},
    'tier_2_photo': {'weight': 0.5, 'description': 'Photo evidence of crop/yield/condition'},
    'tier_3_sensor': {'weight': 0.7, 'description': 'Sensor data (soil moisture, NPK, weather station)'},
    'tier_4_kvc': {'weight': 0.85, 'description': 'Verified by Krishi Vigyan Kendra officer'},
    'tier_5_control_plot': {'weight': 1.0, 'description': 'Side-by-side control plot with measurements'}
}


class ValidationLedgerV2:
    """Advanced validation ledger with Sheriff's 5 requirements."""
    
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
    
    def create_entry(self, 
                     plan_id: str,
                     recommendation: dict,
                     farmer_context: dict,
                     baseline_practice: dict) -> dict:
        """
        Create a new validation entry with full context.
        
        recommendation: {crop, variety, npk, irrigation, pest_control, sowing_date, ...}
        farmer_context: {district, state, soil_type, season, irrigation_type, ...}
        baseline_practice: {what_farmer_normally_does, local_standard, control_plot_yield}
        """
        entry = {
            'plan_id': plan_id,
            'created_at': datetime.now().isoformat(),
            'status': 'recommendation_issued',
            
            # RECOMMENDATION — what AI advised, broken into components
            'recommendation': {
                'crop': recommendation.get('crop'),
                'variety': recommendation.get('variety'),
                'npk_kg_ha': recommendation.get('npk_kg_ha'),
                'irrigation_schedule': recommendation.get('irrigation_schedule'),
                'pest_control': recommendation.get('pest_control'),
                'sowing_date': recommendation.get('sowing_date'),
                'harvest_date': recommendation.get('harvest_date'),
                'full_text': recommendation.get('full_text', '')
            },
            
            # SOURCE — which authority backs this
            'authority_source': recommendation.get('source', 'Unknown'),
            'confidence_score': recommendation.get('confidence', 0),
            
            # CONTEXT — where and under what conditions
            'context': {
                'district': farmer_context.get('district', 'Unknown'),
                'state': farmer_context.get('state', 'Unknown'),
                'soil_type': farmer_context.get('soil_type', 'Unknown'),
                'season': farmer_context.get('season', 'Unknown'),
                'irrigation_type': farmer_context.get('irrigation_type', 'rainfed'),
                'crop_stage': farmer_context.get('crop_stage', 'pre-sowing'),
                'weather_summary': farmer_context.get('weather_summary', {}),
                'stress_conditions': farmer_context.get('stress_conditions', [])
            },
            
            # BASELINE — what to compare against
            'baseline': {
                'farmer_usual_practice': baseline_practice.get('farmer_usual', ''),
                'local_standard_practice': baseline_practice.get('local_standard', ''),
                'control_plot_yield_t_ha': baseline_practice.get('control_yield'),
                'control_plot_cost_inr': baseline_practice.get('control_cost'),
                'previous_season_yield_t_ha': baseline_practice.get('previous_yield')
            },
            
            # ADOPTION — tracked per component
            'adoption': {},
            
            # OUTCOME — what actually happened
            'outcome': {},
            
            # EVIDENCE — quality tier
            'evidence_tier': 'tier_1_self_report',
            'evidence_details': {}
        }
        
        self.entries.append(entry)
        self._save()
        return entry
    
    def record_adoption(self, 
                        plan_id: str,
                        crop_adopted: bool = True,
                        variety_adopted: bool = True,
                        npk_adopted: float = 1.0,  # 0.0 to 1.0
                        irrigation_adopted: float = 1.0,
                        pest_control_adopted: float = 1.0,
                        sowing_on_time: bool = True,
                        deviation_notes: str = '') -> dict:
        """
        Record partial adoption — Sheriff's requirement #4.
        Tracks exactly which parts of the recommendation were followed.
        """
        for entry in self.entries:
            if entry['plan_id'] == plan_id:
                entry['adoption'] = {
                    'crop_adopted': crop_adopted,
                    'variety_adopted': variety_adopted,
                    'npk_adherence': npk_adopted,
                    'irrigation_adherence': irrigation_adopted,
                    'pest_control_adherence': pest_control_adopted,
                    'sowing_on_time': sowing_on_time,
                    'overall_adherence': round(
                        (int(crop_adopted) + int(variety_adopted) + npk_adopted + 
                         irrigation_adopted + pest_control_adopted + int(sowing_on_time)) / 6, 2
                    ),
                    'deviation_notes': deviation_notes,
                    'recorded_at': datetime.now().isoformat()
                }
                entry['status'] = 'adoption_recorded'
                self._save()
                return entry
        return {'error': 'Plan ID not found'}
    
    def record_outcome(self,
                       plan_id: str,
                       actual_yield_t_ha: float,
                       actual_cost_inr: float,
                       water_used_liters: float = 0,
                       disease_incidence_percent: float = 0,
                       farmer_satisfaction: int = 3,
                       evidence_tier: str = 'tier_1_self_report',
                       evidence_notes: str = '',
                       photo_urls: List[str] = None,
                       verifier_name: str = '',
                       verifier_role: str = '') -> dict:
        """
        Record outcome with evidence quality — Sheriff's requirement #1.
        """
        tier = EVIDENCE_TIERS.get(evidence_tier, EVIDENCE_TIERS['tier_1_self_report'])
        
        for entry in self.entries:
            if entry['plan_id'] == plan_id:
                entry['outcome'] = {
                    'actual_yield_t_ha': actual_yield_t_ha,
                    'actual_cost_inr': actual_cost_inr,
                    'water_used_liters': water_used_liters,
                    'disease_incidence_percent': disease_incidence_percent,
                    'farmer_satisfaction_1_5': farmer_satisfaction
                }
                
                # Counterfactual comparison — Sheriff's requirement #2
                baseline_yield = entry['baseline'].get('control_plot_yield_t_ha')
                previous_yield = entry['baseline'].get('previous_season_yield_t_ha')
                baseline_cost = entry['baseline'].get('control_plot_cost_inr')
                
                entry['counterfactual'] = {
                    'yield_vs_control': round(actual_yield_t_ha - baseline_yield, 2) if baseline_yield else None,
                    'yield_vs_previous': round(actual_yield_t_ha - previous_yield, 2) if previous_yield else None,
                    'yield_improvement_percent': round(
                        ((actual_yield_t_ha - baseline_yield) / baseline_yield) * 100, 1
                    ) if baseline_yield and baseline_yield > 0 else None,
                    'cost_vs_control': round(actual_cost_inr - baseline_cost, 2) if baseline_cost else None,
                    'cost_savings_percent': round(
                        ((baseline_cost - actual_cost_inr) / baseline_cost) * 100, 1
                    ) if baseline_cost and baseline_cost > 0 else None,
                    'recommendation_beat_baseline': (
                        actual_yield_t_ha > baseline_yield if baseline_yield else None
                    )
                }
                
                # Evidence quality
                entry['evidence_tier'] = evidence_tier
                entry['evidence_details'] = {
                    'tier_name': tier['description'],
                    'tier_weight': tier['weight'],
                    'notes': evidence_notes,
                    'photo_urls': photo_urls or [],
                    'verifier_name': verifier_name,
                    'verifier_role': verifier_role,
                    'recorded_at': datetime.now().isoformat()
                }
                
                entry['status'] = 'outcome_recorded'
                entry['outcome_timestamp'] = datetime.now().isoformat()
                self._save()
                return entry
        return {'error': 'Plan ID not found'}
    
    def get_stratified_stats(self) -> dict:
        """
        Stratified validation — Sheriff's requirement #5.
        Slices performance by crop, district, soil, season, irrigation.
        """
        validated = [e for e in self.entries if e.get('status') == 'outcome_recorded']
        
        if not validated:
            return {'message': 'No validated outcomes yet', 'total_entries': len(self.entries)}
        
        def slice_by(key_path, entries):
            """Slice entries by a nested key."""
            slices = {}
            for e in entries:
                val = e
                for k in key_path:
                    val = val.get(k, {}) if isinstance(val, dict) else 'Unknown'
                val = str(val) if val else 'Unknown'
                if val not in slices:
                    slices[val] = []
                slices[val].append(e)
            return slices
        
        def compute_slice_stats(sliced):
            result = {}
            for key, entries in sliced.items():
                beat_baseline = [
                    e.get('counterfactual', {}).get('recommendation_beat_baseline')
                    for e in entries
                    if e.get('counterfactual', {}).get('recommendation_beat_baseline') is not None
                ]
                result[key] = {
                    'count': len(entries),
                    'beat_baseline_rate': round(
                        sum(1 for b in beat_baseline if b) / len(beat_baseline) * 100, 1
                    ) if beat_baseline else 'N/A',
                    'avg_satisfaction': round(
                        sum(e.get('outcome', {}).get('farmer_satisfaction_1_5', 0) for e in entries) / len(entries), 2
                    ),
                    'avg_yield_improvement': round(
                        sum(
                            e.get('counterfactual', {}).get('yield_improvement_percent', 0) or 0
                            for e in entries
                        ) / len(entries), 1
                    )
                }
            return result
        
        return {
            'total_validated': len(validated),
            'total_entries': len(self.entries),
            'stratified': {
                'by_crop': compute_slice_stats(slice_by(['context', 'district'], validated)),
                'by_district': compute_slice_stats(slice_by(['context', 'district'], validated)),
                'by_soil': compute_slice_stats(slice_by(['context', 'soil_type'], validated)),
                'by_season': compute_slice_stats(slice_by(['context', 'season'], validated)),
                'by_irrigation': compute_slice_stats(slice_by(['context', 'irrigation_type'], validated))
            }
        }
    
    def get_confidence_calibration(self) -> dict:
        """
        Confidence calibration — Sheriff's requirement #3.
        When system says X% confidence, how often was it correct?
        """
        validated = [e for e in self.entries if e.get('status') == 'outcome_recorded']
        
        if not validated:
            return {'message': 'Not enough data for calibration'}
        
        # Group by confidence ranges
        buckets = {'50-60': [], '60-70': [], '70-80': [], '80-90': [], '90-100': []}
        for e in validated:
            conf = e.get('confidence_score', 0)
            beat = e.get('counterfactual', {}).get('recommendation_beat_baseline')
            if beat is None:
                continue
            if conf < 60:
                buckets['50-60'].append(beat)
            elif conf < 70:
                buckets['60-70'].append(beat)
            elif conf < 80:
                buckets['70-80'].append(beat)
            elif conf < 90:
                buckets['80-90'].append(beat)
            else:
                buckets['90-100'].append(beat)
        
        calibration = {}
        for bucket, results in buckets.items():
            if results:
                calibration[bucket] = {
                    'claimed_confidence_range': bucket,
                    'actual_success_rate': round(sum(1 for r in results if r) / len(results) * 100, 1),
                    'sample_size': len(results),
                    'calibrated': abs(
                        int(bucket.split('-')[0]) - 
                        round(sum(1 for r in results if r) / len(results) * 100, 1)
                    ) < 15  # Within 15% is considered calibrated
                }
        
        return {
            'calibration_data': calibration,
            'overall_calibrated': all(
                c.get('calibrated', False) for c in calibration.values()
            ) if calibration else False
        }
    
    def get_evidence_loop(self, plan_id: str) -> dict:
        """Complete evidence loop with all 5 Sheriff requirements."""
        for entry in self.entries:
            if entry['plan_id'] == plan_id:
                return {
                    'plan_id': plan_id,
                    '1_recommendation_components': entry.get('recommendation'),
                    '2_authority_source': entry.get('authority_source'),
                    '3_confidence_claimed': entry.get('confidence_score'),
                    '4_adoption_tracking': entry.get('adoption'),
                    '5_outcome': entry.get('outcome'),
                    '6_counterfactual': entry.get('counterfactual'),
                    '7_evidence_quality': {
                        'tier': entry.get('evidence_tier'),
                        'details': entry.get('evidence_details')
                    },
                    '8_context_stratification': entry.get('context'),
                    'recommendation_beat_baseline': entry.get('counterfactual', {}).get('recommendation_beat_baseline')
                }
        return {'error': 'Plan ID not found'}


# Singleton
_ledger_v2 = ValidationLedgerV2()


# Public API functions
def create_validation_entry(plan_id: str, recommendation: dict, context: dict, baseline: dict) -> dict:
    return _ledger_v2.create_entry(plan_id, recommendation, context, baseline)

def record_adoption(plan_id: str, **kwargs) -> dict:
    return _ledger_v2.record_adoption(plan_id, **kwargs)

def record_outcome(plan_id: str, **kwargs) -> dict:
    return _ledger_v2.record_outcome(plan_id, **kwargs)

def get_evidence_loop(plan_id: str) -> dict:
    return _ledger_v2.get_evidence_loop(plan_id)

def get_stratified_stats() -> dict:
    return _ledger_v2.get_stratified_stats()

def get_confidence_calibration() -> dict:
    return _ledger_v2.get_confidence_calibration()


if __name__ == '__main__':
    # Full demo: Sheriff's 5 requirements
    plan_id = 'demo-sheriff-v2-001'
    
    # Create entry
    create_validation_entry(
        plan_id,
        recommendation={
            'crop': 'Rice', 'variety': 'Ranjit', 'npk_kg_ha': '60:30:40',
            'irrigation_schedule': 'Every 5 days', 'pest_control': 'Neem oil 5ml/L',
            'sowing_date': '2026-06-15', 'source': 'AAU Jorhat Kharif Guidelines 2025',
            'confidence': 85, 'full_text': 'Plant Ranjit rice with 60:30:40 NPK'
        },
        context={
            'district': 'Cachar', 'state': 'Assam', 'soil_type': 'Alluvial',
            'season': 'Kharif', 'irrigation_type': 'Canal', 'stress_conditions': ['occasional flooding']
        },
        baseline={
            'farmer_usual': 'Traditional variety, 40:20:20 NPK, rainfed',
            'local_standard': 'Swarna variety, 50:30:30 NPK',
            'control_yield': 3.8, 'control_cost': 12000, 'previous_yield': 3.5
        }
    )
    
    # Record partial adoption
    record_adoption(plan_id, npk_adopted=1.0, irrigation_adopted=0.8, 
                    pest_control_adopted=0.5, deviation_notes='Used half neem oil dose, relied on rain')
    
    # Record outcome with photo evidence
    record_outcome(plan_id, actual_yield_t_ha=4.5, actual_cost_inr=10000,
                   farmer_satisfaction=4, evidence_tier='tier_2_photo',
                   evidence_notes='Photos of harvest and weighing verified by village coordinator')
    
    print('=== EVIDENCE LOOP ===')
    print(json.dumps(get_evidence_loop(plan_id), indent=2))
    
    print('\n=== STRATIFIED STATS ===')
    print(json.dumps(get_stratified_stats(), indent=2))
    
    print('\n=== CONFIDENCE CALIBRATION ===')
    print(json.dumps(get_confidence_calibration(), indent=2))

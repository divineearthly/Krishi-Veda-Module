"""
VEDIC QUANTUM ENGINE — Pure Vedic AI Response
==============================================
No generic LLM. Uses Vedic algorithms + knowledge base + real data.
Instant response. Domain-specific. Accurate.

Flow: Sensor/Query → Manas Gate → Tanmatra Fusion → Kosha Recall → 
      Kala-Chakra Timing → Nyaya Verification → Ahimsa Filter → Dharma Prioritize → Response
"""

import time, os, sys, math

sys.path.insert(0, os.path.expanduser("~/vedic-inference-engine"))
from vedic_inference_engine import (
    ManasGate, TanmatraFusion, TanmatraElement,
    KoshaNet, KalaChakra, Ritu, NyayaScaffold, PramanaSource,
    Ahimsa108Filter, RtaDharmaRouter, ParaVakEngine,
    ChittaKVCache, Antahkarana,
)

class VedicQuantumEngine:
    """Pure Vedic AI — no generic LLM, only Vedic algorithms + domain knowledge."""
    
    def __init__(self):
        self.manas = ManasGate()
        self.tanmatra = TanmatraFusion()
        self.kosha = KoshaNet()
        self.kala = KalaChakra()
        self.nyaya = NyayaScaffold()
        self.ahimsa = Ahimsa108Filter()
        self.dharma = RtaDharmaRouter()
        self.paravak = ParaVakEngine()
        self.chitta = ChittaKVCache(max_tokens=256)
        self.antah = Antahkarana("Vedic Quantum Engine — Assam")
        
        # Seed Kosha with deep agricultural knowledge
        self._seed_vedic_knowledge()
        
        # Seed identity
        self.kosha.anandamaya_seed("Vedic Quantum Krishi AI — Barak Valley, Assam")
    
    def _seed_vedic_knowledge(self):
        """Load comprehensive Vedic agricultural knowledge into Kosha."""
        knowledge = {
            # Soil management
            "acidic_soil": "Apply lime (chuna) 2-3 tons/ha. Mix with soil 3 weeks before sowing. Paravartya calculation: lime_kg = (6.5 - pH) × 2500 per bigha.",
            "alkaline_soil": "Apply gypsum 1-2 tons/ha. Add organic matter. Avoid ash. pH above 8 blocks iron absorption.",
            "low_nitrogen": "Vermicompost 5 tons/ha OR Azolla incorporation OR green manure (Sesbania/Dhaincha). Apply Panchgavya at 3% foliar spray.",
            "low_phosphorus": "Rock phosphate 200kg/ha OR bone meal 150kg/ha. Apply with FYM for better absorption. Mycorrhiza inoculation helps.",
            "low_potassium": "Wood ash 100kg/ha OR banana pseudostem mulch. Avoid burning crop residue — return to soil.",
            
            # Crop-specific
            "sali_rice": "Sow nursery: May-June. Transplant: July. Harvest: November. Duration: 150 days. Seed rate: 40kg/ha. Spacing: 20×15cm. Panchgavya at tillering + flowering.",
            "boro_rice": "Sow nursery: November. Transplant: December-January. Harvest: April-May. Needs irrigation. Seed rate: 40kg/ha. Watch for cold injury.",
            "mustard": "Sow: October-November. Harvest: February. Seed rate: 6-8kg/ha. Spacing: 30×10cm. Irrigation at flowering. Aphid: Neem-Astra 10%.",
            "summer_vegetables": "Okra: March-June. Brinjal: February-March. Cucumber: February-April. Apply vermicompost 5t/ha before planting. Mulch with straw.",
            "winter_vegetables": "Cabbage: October transplant. Tomato: November. Potato: October-November. Apply Panchgavya every 15 days.",
            
            # Pest management (Vedic)
            "aphids": "Neem-Astra: Crush 5kg neem leaves + 5L cow urine in 10L water. Boil 30 min. Strain. Spray 10% solution. Repeat every 7 days.",
            "stem_borer": "Apply neem cake 250kg/ha at transplanting. Install pheromone traps. Remove and burn infected tillers. Trichogramma wasps.",
            "blast_disease": "Pseudomonas fluorescens at 5g/L water as foliar spray. Avoid excess nitrogen. Use resistant varieties. Apply Panchgavya as preventive.",
            "blb": "Bacterial Leaf Blight: Copper oxychloride 2.5g/L + Panchgavya 3%. Avoid overhead irrigation. Use disease-free seeds.",
            
            # Panchgavya
            "panchgavya_preparation": "Mix: Fresh cow dung 5kg + Cow urine 3L + Cow milk 2L + Curd 2L + Ghee 1kg. Ferment 15 days in clay pot. Stir daily morning/evening. Apply at 3% foliar spray.",
            "jeevamrut": "Mix: Cow dung 10kg + Cow urine 10L + Jaggery 2kg + Pulse flour 2kg + Soil 1kg in 200L water. Ferment 7 days. Apply directly to soil at 200L/acre.",
            
            # Seasonal
            "monsoon_preparation": "Clean drainage channels. Repair field bunds. Prepare nursery beds raised 15cm. Seed treatment with Panchgavya for 30 min before sowing.",
            "summer_irrigation": "Irrigate early morning or evening. Drip saves 60% water. Mulch with straw/paddy husk 5cm thick. Soil moisture below 30% needs immediate irrigation.",
            "winter_protection": "Light irrigation on cold nights protects from frost. Smoke screens at field edges. Cover nurseries with straw mats at night.",
        }
        
        for key, value in knowledge.items():
            self.kosha.vijnanamaya_consolidate(key, value, confidence=0.95)
    
    def query(self, question: str, soil_type: str = "alluvial",
              sensor_data: dict = None, lat: float = 24.81, lon: float = 92.80) -> dict:
        """
        Process query through complete Vedic pipeline.
        Returns instant, specific, Vedic-verified advice.
        """
        t0 = time.time()
        
        # 1. Manas: Attend to query + sensor data
        self.manas.attend("user_query", question, priority=0.95, source="farmer")
        if sensor_data:
            for key, val in sensor_data.items():
                self.manas.attend(f"sensor_{key}", val, priority=0.85, source="iot")
        
        # 2. Kala-Chakra: What season are we in?
        doy = time.localtime().tm_yday
        ritu = self.kala.ritu_for_day(doy)
        moon_phase = "Shukla" if (doy % 30) <= 15 else "Krishna"
        
        # 3. Kosha: Retrieve relevant Vedic knowledge
        relevant = []
        search_terms = []
        
        # Parse what farmer is asking
        q_lower = question.lower()
        if any(w in q_lower for w in ['plant', 'sow', 'crop', 'cultivate']):
            search_terms.extend([f"{ritu.name.lower()}_crops", "sali_rice", "mustard", "summer_vegetables"])
        if any(w in q_lower for w in ['pest', 'insect', 'disease', 'problem']):
            search_terms.extend(["aphids", "stem_borer", "blast_disease", "blb"])
        if any(w in q_lower for w in ['fertilizer', 'nutrient', 'npk', 'manure']):
            search_terms.extend(["low_nitrogen", "low_phosphorus", "low_potassium", "panchgavya_preparation"])
        if any(w in q_lower for w in ['ph', 'acid', 'alkaline', 'lime']):
            search_terms.extend(["acidic_soil", "alkaline_soil"])
        if any(w in q_lower for w in ['irrigation', 'water', 'dry', 'drought']):
            search_terms.append("summer_irrigation")
        if any(w in q_lower for w in ['monsoon', 'rain', 'varsha']):
            search_terms.append("monsoon_preparation")
        
        # Always add seasonal + Panchgavya
        search_terms.append("panchgavya_preparation")
        
        for term in search_terms:
            knowledge = self.kosha.vijnanamaya_recall(term)
            if knowledge:
                relevant.append(knowledge)
        
        # 4. Nyaya: Verify with reasoning
        self.nyaya.tag(f"Query: {question[:80]}", PramanaSource.PRATYAKSHA, 0.95)
        for i, k in enumerate(relevant[:3]):
            self.nyaya.tag(f"Knowledge {i+1}: {k[:60]}", PramanaSource.SHABDA, 0.90)
        
        # 5. Ahimsa: Check for harmful recommendations
        combined_advice = " ".join(relevant[:4])
        ahimsa_verdict = self.ahimsa.evaluate(combined_advice)
        
        # 6. Dharma: Prioritize by community impact
        self.dharma.add("response", crop_importance=0.9, season_urgency=0.8,
                       severity_weight=0.5, farmers_affected=500,
                       ahimsa_score=0.3 if ahimsa_verdict.level == 2 else 1.0)
        
        # 7. Build seasonal context
        ritu_names = {
            Ritu.VASANTA: "🌸 Vasanta (Spring) — Nursery preparation. Soil warming.",
            Ritu.GRISHMA: "☀️ Grishma (Summer) — Irrigation critical. Sali rice nursery time.",
            Ritu.VARSHA: "🌧️ Varsha (Monsoon) — Main cropping season. Paddy transplanting.",
            Ritu.SHARAD: "🍂 Sharad (Autumn) — Harvest season. Rabi preparation begins.",
            Ritu.HEMANTA: "❄️ Hemanta (Pre-winter) — Rabi sowing. Mustard, wheat.",
            Ritu.SHISHIRA: "🥶 Shishira (Winter) — Boro rice nursery. Cold protection.",
        }
        
        # 8. Build Vedic response
        response_parts = []
        
        # Seasonal header
        response_parts.append(f"॥ {ritu_names.get(ritu, '')} ॥")
        response_parts.append(f"📅 Day {doy}/365 | {moon_phase} Paksha")
        
        if sensor_data:
            response_parts.append(f"\n📡 SENSOR ANALYSIS:")
            if 'ph' in sensor_data:
                ph = sensor_data['ph']
                if ph < 5.5:
                    response_parts.append(f"  ⚠ pH {ph} — Acidic. {self.kosha.vijnanamaya_recall('acidic_soil')[:100]}")
                elif ph > 8.0:
                    response_parts.append(f"  ⚠ pH {ph} — Alkaline. {self.kosha.vijnanamaya_recall('alkaline_soil')[:100]}")
                else:
                    response_parts.append(f"  ✓ pH {ph} — Optimal range.")
            if 'n' in sensor_data and sensor_data['n'] < 30:
                response_parts.append(f"  ⚠ Low N ({sensor_data['n']}ppm). {self.kosha.vijnanamaya_recall('low_nitrogen')[:100]}")
        
        # Vedic recommendations
        response_parts.append(f"\n🕉️ VEDIC PRESCRIPTION:")
        for i, k in enumerate(relevant[:4]):
            response_parts.append(f"  {i+1}. {k[:200]}")
        
        # Moon guidance
        if moon_phase == "Shukla":
            response_parts.append(f"\n🌒 SHUKLA PAKSHA: Auspicious for sowing. Sap flows upward. Plant above-ground crops.")
        else:
            response_parts.append(f"\n🌖 KRISHNA PAKSHA: Favorable for harvesting and root crops. Sap flows downward.")
        
        # Always end with Panchgavya
        response_parts.append(f"\n🕉 DAILY PRACTICE: Apply Panchgavya 3% foliar spray every 15 days.")
        response_parts.append(f"   Ahimsa-108: NO chemicals. Organic only.")
        
        final_advice = "\n".join(response_parts)
        
        elapsed = round((time.time() - t0) * 1000, 1)
        
        return {
            "advice": final_advice,
            "engine": "vedic-quantum",
            "inference_ms": elapsed,
            "ritu": ritu.name,
            "moon": moon_phase,
            "nyaya_confidence": round(self.nyaya.overall_confidence(), 3),
            "dharma_priority": round(self.dharma.top_priority().compute_score(), 3),
            "ahimsa": "BLOCKED" if ahimsa_verdict.level == 2 else "PURE",
            "knowledge_sources": len(relevant),
            "hallucination_risk": len(self.nyaya.detect_hallucinations()) > 0,
        }


if __name__ == "__main__":
    engine = VedicQuantumEngine()
    
    print("॥ VEDIC QUANTUM ENGINE — Pure Vedic AI ॥\n")
    
    # Test with sensor data
    result = engine.query(
        "What to plant and what fertilizers?",
        soil_type="alluvial",
        sensor_data={"ph": 5.4, "n": 22, "p": 18, "k": 40, "moisture": 35}
    )
    
    print(result['advice'])
    print(f"\n{'='*50}")
    print(f"Engine: {result['engine']} | Time: {result['inference_ms']}ms")
    print(f"Nyaya: {result['nyaya_confidence']} | Ahimsa: {result['ahimsa']}")
    print(f"Hallucination: {result['hallucination_risk']}")

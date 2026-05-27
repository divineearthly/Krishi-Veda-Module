"""
Add comprehensive crop knowledge to Shabda Pramana database
"""
import sqlite3

db = sqlite3.connect('krishi_veda.db')

# Assam-specific crop knowledge
crop_knowledge = [
    # Rice varieties
    ("sali rice", "Sali is the main winter rice crop of Assam, transplanted in June-July and harvested in November-December. Requires 150-200cm rainfall. Popular varieties: Ranjit, Bahadur, Mahsuri."),
    ("ahu rice", "Ahu is summer rice grown March-August in Assam. Direct seeded. Varieties: Luit, Kapilee, Disang. Requires irrigation."),
    ("bao rice", "Bao is deepwater rice grown in flood-prone areas of Assam. Sown March-April, harvested November-December. Tolerates 1-3m water depth."),
    
    # Fertilizers
    ("vermicompost", "Vermicompost is organic manure produced by earthworms. NPK ratio approx 1.5:1:1. Apply 2-3 tons/ha for rice. Improves soil structure and water holding capacity."),
    ("green manure", "Green manuring with Sesbania (Dhaincha) adds 60-80kg N/ha. Sow at 50kg seed/ha, incorporate at 45 days. Ideal for organic rice cultivation."),
    ("fym", "Farm Yard Manure - decomposed cow dung. Apply 10-15 tons/ha during land preparation. Contains 0.5% N, 0.2% P, 0.5% K. Slow release organic fertilizer."),
    ("neem cake", "Neem cake is residue after oil extraction. Contains 5% N, 1% P, 1.5% K. Also acts as natural pesticide against soil pests. Apply 250-500 kg/ha."),
    
    # Pest management
    ("stem borer", "Major rice pest in Assam. Symptoms: dead heart at vegetative stage, white ear at reproductive stage. Control: Trichogramma cards @ 50,000/ha, neem oil 5ml/L spray."),
    ("blast disease", "Rice blast caused by Magnaporthe oryzae. Symptoms: spindle-shaped lesions on leaves. Control: Seed treatment with Trichoderma, avoid excess nitrogen, spray Pseudomonas fluorescens."),
    
    # Soil types
    ("alluvial soil assam", "Brahmaputra and Barak alluvial soils: pH 5.5-7.5, rich in potash but deficient in phosphorus and nitrogen. Ideal for rice, jute, mustard. Requires organic matter addition."),
    
    # Seasonal practices
    ("monsoon planting", "June-July is optimal for Sali rice transplanting in Assam. 25-30 day old seedlings, 2-3 per hill, spacing 20x15cm. Ensure proper drainage channels."),
    ("winter crops assam", "Rabi crops in Assam: Mustard (Oct-Nov sowing), Potato (Oct-Dec), Wheat (Nov-Dec), Vegetables (cabbage, cauliflower, tomato). Use residual soil moisture after rice harvest."),
]

for keyword, context in crop_knowledge:
    db.execute(
        "INSERT OR REPLACE INTO shabda_pramana (keyword, factual_context) VALUES (?, ?)",
        (keyword, context)
    )

db.commit()
count = db.execute("SELECT COUNT(*) FROM shabda_pramana").fetchone()[0]
print(f"✅ Added {len(crop_knowledge)} knowledge entries")
print(f"   Total knowledge base: {count} verified facts")
db.close()

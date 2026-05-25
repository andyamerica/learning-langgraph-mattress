# -----------------------------
# Mattress Product Catalog Data
# -----------------------------

PRODUCT_FAMILIES = {
    "Luxury": {
        "description": "Premium comfort with advanced cooling and pressure relief.",
        "firmness": "Medium-Firm",
        "layers": ["Cooling Gel Foam", "Memory Foam", "Support Core"],
        "warranty_years": 12
    },
    "Essential": {
        "description": "Affordable comfort with balanced support.",
        "firmness": "Medium",
        "layers": ["Comfort Foam", "Support Core"],
        "warranty_years": 8
    },
    "Base": {
        "description": "Entry-level mattress for basic comfort needs.",
        "firmness": "Firm",
        "layers": ["Support Foam"],
        "warranty_years": 5
    }
}

SIZES = {
    "6x6": {"label": "King", "dimensions": "72in x 72in"},
    "6x7": {"label": "Super King", "dimensions": "72in x 84in"},
    "5x6": {"label": "Queen", "dimensions": "60in x 72in"}
}

# -----------------------------
# Pricing Matrix
# -----------------------------

PRICES = {
    ("Luxury", "6x6"): 1200,
    ("Luxury", "6x7"): 1350,
    ("Luxury", "5x6"): 1100,

    ("Essential", "6x6"): 800,
    ("Essential", "6x7"): 900,
    ("Essential", "5x6"): 750,

    ("Base", "6x6"): 500,
    ("Base", "6x7"): 600,
    ("Base", "5x6"): 450
}

# -----------------------------
# FAQ / Q&A Data
# -----------------------------

FAQS = [
    {
        "question": "what types of mattresses do you have",
        "answer": "We offer three mattress lines: Luxury, Essential, and Base."
    },
    {
        "question": "what sizes do you offer",
        "answer": "We offer 6x6 (King), 6x7 (Super King), and 5x6 (Queen)."
    },
    {
        "question": "what is the warranty",
        "answer": "Luxury has 12 years, Essential has 8 years, and Base has 5 years of warranty."
    },
    {
        "question": "which mattress is best for back support",
        "answer": "Luxury (Medium-Firm) and Base (Firm) are generally better for back support."
    },
    {
        "question": "do you have cooling mattresses",
        "answer": "Yes, the Luxury line includes a cooling gel foam layer for temperature regulation."
    }
]

# -----------------------------
# Full Catalog (Flattened)
# -----------------------------

CATALOG = []

for model_name, model_info in PRODUCT_FAMILIES.items():
    for size_code, size_info in SIZES.items():
        CATALOG.append({
            "model": model_name,
            "size_code": size_code,
            "size_label": size_info["label"],
            "dimensions": size_info["dimensions"],
            "description": model_info["description"],
            "firmness": model_info["firmness"],
            "layers": model_info["layers"],
            "warranty_years": model_info["warranty_years"],
            "price": PRICES[(model_name, size_code)]
        })

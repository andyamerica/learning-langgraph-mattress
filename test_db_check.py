from db_tools import get_price

tests = [
    ("Luxury", None),
    ("Luxury", "King"),
    ("Luxury", "Queen"),
    ("Essential", None),
    ("Base", None),
]

for model, size in tests:
    print(model, size, "→", get_price(model, size))

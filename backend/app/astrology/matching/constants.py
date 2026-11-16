from decimal import Decimal
from types import MappingProxyType

from app.astrology.constants import NAKSHATRAS

RULESET_ID = "muhurta_chintamani_joshi_v1"
CALCULATION_VERSION = "1.0.0"
KOOTA_MAXIMA = MappingProxyType({
    "varna": Decimal("1"), "vashya": Decimal("2"), "tara": Decimal("3"),
    "yoni": Decimal("4"), "graha_maitri": Decimal("5"), "gana": Decimal("6"),
    "bhakoot": Decimal("7"), "nadi": Decimal("8"),
})
assert sum(KOOTA_MAXIMA.values(), Decimal(0)) == Decimal(36)

RASHI_NAMES = ("Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena")
RASHI_LORDS = ("Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter")
VARNA_BY_RASHI = ("Kshatriya", "Vaishya", "Shudra", "Brahmin", "Kshatriya", "Vaishya", "Shudra", "Brahmin", "Kshatriya", "Vaishya", "Shudra", "Brahmin")
VARNA_RANK = MappingProxyType({"Shudra": 0, "Vaishya": 1, "Kshatriya": 2, "Brahmin": 3})

# Muhurta Chintamani, Joshi commentary chart: whole-sign Vashya classes.
VASHYA_BY_RASHI = ("Chatushpada", "Chatushpada", "Dvipada", "Jalachara", "Chatushpada", "Dvipada", "Dvipada", "Keeta", "Chatushpada", "Jalachara", "Jalachara", "Jalachara")
VASHYA_CLASSES = ("Dvipada", "Chatushpada", "Jalachara", "Keeta")
VASHYA_MATRIX = (("2", "0.5", "0.5", "1"), ("0.5", "2", "2", "2"), ("0.5", "2", "2", "2"), ("1", "2", "2", "2"))

TARA_NAMES = ("Janma", "Sampat", "Vipat", "Kshema", "Pratyari", "Sadhaka", "Vadha", "Maitra", "Parama Maitra")
UNFAVOURABLE_TARAS = frozenset({3, 5, 7})

YONI_CLASSES = ("Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion")
YONI_BY_NAKSHATRA = (
    "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant",
)
# Ordered bride-row/groom-column chart. Includes the documented Horse/Buffalo
# and Mongoose/Monkey corrections described by the selected source.
YONI_MATRIX = (
    (4,2,3,2,2,3,3,3,0,1,3,2,2,1),
    (2,4,3,2,2,3,3,3,3,2,2,2,2,0),
    (3,3,4,3,2,3,1,3,3,1,3,0,3,1),
    (2,2,3,4,2,2,1,1,2,2,2,2,0,2),
    (2,2,2,2,4,1,1,2,2,1,0,2,2,1),
    (2,2,3,2,1,4,0,2,2,1,2,2,2,2),
    (2,2,2,1,1,0,4,2,2,2,2,2,2,1),
    (3,2,3,1,2,2,2,4,3,0,3,2,3,1),
    (0,3,3,2,2,2,2,3,4,1,2,2,2,3),
    (1,2,1,2,1,1,2,0,1,4,2,1,2,2),
    (3,2,3,2,0,2,2,3,2,1,4,2,2,2),
    (2,3,0,2,2,2,2,2,2,1,2,4,2,3),
    (2,2,3,0,2,2,2,3,2,2,2,2,4,2),
    (1,0,1,2,1,2,1,1,3,2,2,2,2,4),
)

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
GRAHA_MAITRI_MATRIX = (
    ("5","5","5","4","5","0","0"), ("5","5","4","1","4","0.5","0.5"),
    ("5","4","5","0.5","5","3","0.5"), ("4","1","0.5","5","0.5","5","4"),
    ("5","4","5","0.5","5","0.5","3"), ("0","0.5","3","5","0.5","5","5"),
    ("0","0.5","0.5","4","3","5","5"),
)
GANA_BY_NAKSHATRA = (
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya", "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva",
)
GANA_CLASSES = ("Deva", "Manushya", "Rakshasa")
GANA_MATRIX = ((6,5,1),(6,6,0),(0,0,6))
NADI_BY_NAKSHATRA = (
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi", "Adi", "Madhya", "Antya",
)
assert len(NAKSHATRAS) == len(YONI_BY_NAKSHATRA) == len(GANA_BY_NAKSHATRA) == len(NADI_BY_NAKSHATRA) == 27

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional
import base64
import io
import json
import re

import requests
from PIL import Image

from translations_hi import ITEMS as HI_ITEMS, MESSAGES as HI_MESSAGES
from translations_te import ITEMS as TE_ITEMS, MESSAGES as TE_MESSAGES


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="IP-SAKTHI Sahayak API",
    description="Multilingual Multimodal Ayurveda IP and Innovation Assistant",
    version="4.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen3-vl:2b"


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

SUPPORTED_LANGS = ["en", "hi", "te"]
DEFAULT_LANG = "en"

LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu"
}

TRANSLATIONS = {
    "hi": HI_ITEMS,
    "te": TE_ITEMS
}

MESSAGES = {
    "en": {
        "empty_name": "Please provide a plant, component or product name.",
        "text_not_found": (
            "The requested item is not currently available "
            "in the prototype knowledge base."
        ),
        "image_not_found": (
            "The AI identified the uploaded item, "
            "but detailed information for this item "
            "is not yet available in the prototype knowledge base."
        )
    },
    "hi": HI_MESSAGES,
    "te": TE_MESSAGES
}


def resolve_lang(lang: str) -> str:

    if not lang:
        return DEFAULT_LANG

    lang = lang.lower().strip()

    if lang in SUPPORTED_LANGS:
        return lang

    return DEFAULT_LANG


def get_message(key: str, lang: str) -> str:

    lang = resolve_lang(lang)

    return (
        MESSAGES.get(lang, {})
        .get(key)
        or MESSAGES["en"][key]
    )


def localize_item(key: str, item: dict, lang: str) -> dict:

    lang = resolve_lang(lang)

    if lang == DEFAULT_LANG:
        return item

    overrides = TRANSLATIONS.get(lang, {}).get(key)

    if not overrides:
        return item

    localized = dict(item)
    localized.update(overrides)

    return localized


# ============================================================
# PLANT DATABASE
# ============================================================

PLANTS = {

    "ashwagandha": {
        "name": "Ashwagandha",
        "scientific_name": "Withania somnifera",
        "category": "Plant",
        "family": "Solanaceae",
        "rarity": "Common",
        "confidence": 96,

        "parts": [
            "Root",
            "Leaves",
            "Seeds"
        ],

        "locations": [
            "India",
            "Sri Lanka",
            "Nepal",
            "Dry regions of South Asia"
        ],

        "growth_time": "6–12 months",

        "growth_timeline": [
            {
                "stage": "Germination",
                "duration": "1–3 weeks"
            },
            {
                "stage": "Seedling",
                "duration": "3–8 weeks"
            },
            {
                "stage": "Vegetative growth",
                "duration": "2–5 months"
            },
            {
                "stage": "Root development",
                "duration": "5–8 months"
            },
            {
                "stage": "Maturity / Harvest",
                "duration": "6–12 months"
            }
        ],

        "traditional_uses": [
            "Traditionally used in Ayurveda",
            "Traditional wellness preparations",
            "Traditional herbal formulations"
        ],

        "safety": {
            "level": "Evidence-dependent",
            "toxicity": "Safety depends on plant part, preparation, dose and individual factors.",
            "adverse_effects": "Some preparations may cause adverse effects in certain individuals.",
            "interactions": "Potential interactions should be checked before medicinal use."
        },

        "innovation": [
            "Standardized herbal extract",
            "Herbal wellness formulation",
            "Plant-based functional product",
            "Ayurvedic cosmetic concept"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Brahmi",
                "shared": "Both are Ayurvedic rasayana herbs used for stress support and mental wellbeing.",
                "difference": "Ashwagandha is mainly a physical adaptogen for strength, sleep and endurance, while Brahmi primarily supports memory, focus and nervous-system function."
            },
            {
                "compared_with": "Tulsi",
                "shared": "Both are widely used Ayurvedic herbs that help the body cope with stress.",
                "difference": "Ashwagandha is a warming root tonic used for vitality and recovery, whereas Tulsi is a leaf used mainly for respiratory comfort and daily immune support."
            }
        ]
    },


    "neem": {
        "name": "Neem",
        "scientific_name": "Azadirachta indica",
        "category": "Plant",
        "family": "Meliaceae",
        "rarity": "Common",
        "confidence": 95,

        "parts": [
            "Leaves",
            "Bark",
            "Seeds",
            "Flowers",
            "Oil"
        ],

        "locations": [
            "India",
            "South Asia",
            "Southeast Asia",
            "Tropical regions"
        ],

        "growth_time": "3–5 years for substantial maturity",

        "growth_timeline": [
            {
                "stage": "Seed germination",
                "duration": "1–3 weeks"
            },
            {
                "stage": "Seedling",
                "duration": "1–6 months"
            },
            {
                "stage": "Young plant",
                "duration": "6 months–2 years"
            },
            {
                "stage": "Tree establishment",
                "duration": "2–5 years"
            },
            {
                "stage": "Mature tree",
                "duration": "5+ years"
            }
        ],

        "traditional_uses": [
            "Traditional skin preparations",
            "Traditional dental-care practices",
            "Traditional agricultural applications"
        ],

        "safety": {
            "level": "Preparation-dependent",
            "toxicity": "Different plant parts and preparations can have different safety profiles.",
            "adverse_effects": "Safety should be assessed according to preparation and intended use.",
            "interactions": "Potential interactions require evidence-based evaluation."
        },

        "innovation": [
            "Herbal personal-care formulation",
            "Botanical cosmetic concept",
            "Plant-based agricultural product",
            "Standardized neem extract"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Tulsi",
                "shared": "Both are widely grown plants with traditional antimicrobial and skin-related uses in Ayurveda.",
                "difference": "Neem is bitter and used mainly externally or in blood-purifying preparations, while Tulsi is gentler and used mainly for respiratory and fever-related care."
            },
            {
                "compared_with": "Turmeric",
                "shared": "Both are used in traditional preparations for inflammation and infection.",
                "difference": "Turmeric is valued for curcumin's internal anti-inflammatory action, while neem is valued for its bitter, antimicrobial, blood-cleansing properties, mostly applied topically."
            }
        ]
    },


    "tulsi": {
        "name": "Tulsi",
        "scientific_name": "Ocimum tenuiflorum",
        "category": "Plant",
        "family": "Lamiaceae",
        "rarity": "Common",
        "confidence": 94,

        "parts": [
            "Leaves",
            "Flowers",
            "Seeds",
            "Stems"
        ],

        "locations": [
            "India",
            "Nepal",
            "Bangladesh",
            "Tropical and subtropical regions"
        ],

        "growth_time": "3–5 months",

        "growth_timeline": [
            {
                "stage": "Germination",
                "duration": "5–15 days"
            },
            {
                "stage": "Seedling",
                "duration": "2–5 weeks"
            },
            {
                "stage": "Vegetative growth",
                "duration": "1–3 months"
            },
            {
                "stage": "Flowering",
                "duration": "3–5 months"
            },
            {
                "stage": "Seed production",
                "duration": "4–6 months"
            }
        ],

        "traditional_uses": [
            "Traditional herbal preparations",
            "Traditional wellness practices",
            "Traditional herbal beverages"
        ],

        "safety": {
            "level": "Preparation-dependent",
            "toxicity": "Safety depends on preparation, dose and individual circumstances.",
            "adverse_effects": "Potential adverse effects should be considered before medicinal use.",
            "interactions": "Interactions should be evaluated using reliable evidence."
        },

        "innovation": [
            "Herbal beverage",
            "Functional wellness product",
            "Botanical cosmetic formulation",
            "Standardized Tulsi extract"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Neem",
                "shared": "Both are culturally sacred plants with a long record of antimicrobial traditional use.",
                "difference": "Tulsi is aromatic and used for respiratory comfort and stress support; neem is bitter and used for skin, dental and agricultural purposes."
            },
            {
                "compared_with": "Licorice",
                "shared": "Both are used to soothe the respiratory tract in traditional systems.",
                "difference": "Tulsi acts more as an aromatic expectorant and immune stimulant, while licorice is a demulcent that soothes irritated mucous membranes and sweetens formulations."
            }
        ]
    },


    "turmeric": {
        "name": "Turmeric",
        "scientific_name": "Curcuma longa",
        "category": "Plant",
        "family": "Zingiberaceae",
        "rarity": "Common",
        "confidence": 97,

        "parts": [
            "Rhizome",
            "Leaves"
        ],

        "locations": [
            "India",
            "Bangladesh",
            "Sri Lanka",
            "Southeast Asia"
        ],

        "growth_time": "7–10 months",

        "growth_timeline": [
            {
                "stage": "Planting",
                "duration": "Initial stage"
            },
            {
                "stage": "Sprouting",
                "duration": "2–8 weeks"
            },
            {
                "stage": "Vegetative growth",
                "duration": "2–5 months"
            },
            {
                "stage": "Rhizome development",
                "duration": "5–8 months"
            },
            {
                "stage": "Maturity / Harvest",
                "duration": "7–10 months"
            }
        ],

        "traditional_uses": [
            "Traditional culinary use",
            "Traditional herbal preparations",
            "Traditional topical preparations"
        ],

        "safety": {
            "level": "Dose and preparation dependent",
            "toxicity": "Concentrated preparations can have different safety considerations from culinary quantities.",
            "adverse_effects": "Some individuals may experience adverse effects.",
            "interactions": "Potential interactions should be reviewed."
        },

        "innovation": [
            "Standardized curcumin formulation",
            "Functional food product",
            "Herbal cosmetic concept",
            "Plant-based wellness product"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Ginger",
                "shared": "Both are rhizomes from the Zingiberaceae family used together in food and medicine.",
                "difference": "Turmeric is prized for curcumin's anti-inflammatory and antioxidant effects; ginger is prized for its pungent digestive and anti-nausea action."
            },
            {
                "compared_with": "Neem",
                "shared": "Both have a long history in traditional medicine for skin and inflammatory conditions.",
                "difference": "Turmeric is warming and used internally as well as topically as a golden paste; neem is bitter and mostly used externally as an oil or paste."
            }
        ]
    },


    "ginger": {
        "name": "Ginger",
        "scientific_name": "Zingiber officinale",
        "category": "Plant",
        "family": "Zingiberaceae",
        "rarity": "Common",
        "confidence": 96,

        "parts": [
            "Rhizome"
        ],

        "locations": [
            "India",
            "China",
            "Southeast Asia",
            "Tropical regions"
        ],

        "growth_time": "8–10 months",

        "growth_timeline": [
            {
                "stage": "Planting",
                "duration": "Initial stage"
            },
            {
                "stage": "Sprouting",
                "duration": "2–6 weeks"
            },
            {
                "stage": "Vegetative growth",
                "duration": "2–5 months"
            },
            {
                "stage": "Rhizome development",
                "duration": "5–8 months"
            },
            {
                "stage": "Harvest",
                "duration": "8–10 months"
            }
        ],

        "traditional_uses": [
            "Traditional digestive preparations",
            "Traditional herbal beverages",
            "Traditional culinary applications"
        ],

        "safety": {
            "level": "Dose-dependent",
            "toxicity": "Safety depends on quantity and preparation.",
            "adverse_effects": "High amounts may cause adverse effects in some individuals.",
            "interactions": "Potential interactions should be reviewed."
        },

        "innovation": [
            "Herbal beverage",
            "Functional food product",
            "Standardized ginger extract",
            "Wellness formulation"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Turmeric",
                "shared": "Closely related rhizomes often used together in cooking and formulation.",
                "difference": "Ginger stimulates digestion and circulation with a pungent taste; turmeric provides curcumin, valued more for inflammation than digestion."
            },
            {
                "compared_with": "Piperine",
                "shared": "Both are pungent principles that stimulate digestion.",
                "difference": "Ginger is a whole rhizome with warming, anti-nausea effects; piperine is an isolated black-pepper alkaloid best known for increasing the bioavailability of other compounds."
            }
        ]
    },


    "brahmi": {
        "name": "Brahmi",
        "scientific_name": "Bacopa monnieri",
        "category": "Plant",
        "family": "Plantaginaceae",
        "rarity": "Uncommon",
        "confidence": 91,

        "parts": [
            "Leaves",
            "Stems"
        ],

        "locations": [
            "India",
            "Sri Lanka",
            "Nepal",
            "Wet and marshy regions"
        ],

        "growth_time": "4–6 months",

        "growth_timeline": [
            {
                "stage": "Germination / establishment",
                "duration": "2–6 weeks"
            },
            {
                "stage": "Vegetative growth",
                "duration": "1–3 months"
            },
            {
                "stage": "Creeping growth",
                "duration": "3–5 months"
            },
            {
                "stage": "Maturity",
                "duration": "4–6 months"
            }
        ],

        "traditional_uses": [
            "Traditional Ayurvedic preparations",
            "Traditional herbal formulations"
        ],

        "safety": {
            "level": "Evidence-dependent",
            "toxicity": "Safety depends on preparation and dose.",
            "adverse_effects": "Potential gastrointestinal effects have been reported with some preparations.",
            "interactions": "Potential interactions require evidence review."
        },

        "innovation": [
            "Standardized botanical extract",
            "Functional wellness product",
            "Herbal formulation"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Ashwagandha",
                "shared": "Both are rasayana herbs used for stress, calm and overall resilience.",
                "difference": "Brahmi targets the mind — memory, learning and focus; ashwagandha targets the body — strength, sleep, stamina and hormonal balance."
            },
            {
                "compared_with": "Amla",
                "shared": "Both are cooling rasayana herbs used in rejuvenation formulations.",
                "difference": "Brahmi is a wetland herb used mainly for cognition and nervous health; amla is a fruit used mainly as a nutritive antioxidant and hair/digestive tonic."
            }
        ]
    },


    "amla": {
        "name": "Amla",
        "scientific_name": "Phyllanthus emblica",
        "category": "Plant",
        "family": "Phyllanthaceae",
        "rarity": "Common",
        "confidence": 94,

        "parts": [
            "Fruit",
            "Seeds",
            "Bark",
            "Leaves"
        ],

        "locations": [
            "India",
            "Sri Lanka",
            "Nepal",
            "Southeast Asia"
        ],

        "growth_time": "4–6 years to fruit-bearing maturity",

        "growth_timeline": [
            {
                "stage": "Seed germination",
                "duration": "2–8 weeks"
            },
            {
                "stage": "Seedling",
                "duration": "6–12 months"
            },
            {
                "stage": "Young tree",
                "duration": "1–3 years"
            },
            {
                "stage": "Tree establishment",
                "duration": "3–5 years"
            },
            {
                "stage": "Fruit-bearing maturity",
                "duration": "4–6+ years"
            }
        ],

        "traditional_uses": [
            "Traditional dietary preparations",
            "Traditional Ayurvedic formulations",
            "Traditional wellness products"
        ],

        "safety": {
            "level": "Preparation-dependent",
            "toxicity": "Safety depends on dose and formulation.",
            "adverse_effects": "Individual response can vary.",
            "interactions": "Potential interactions should be evaluated."
        },

        "innovation": [
            "Functional food product",
            "Herbal beverage",
            "Botanical cosmetic product",
            "Standardized fruit extract"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Moringa",
                "shared": "Both are highly nutritious plants rich in vitamins and antioxidants.",
                "difference": "Amla is a fruit famous for exceptionally high vitamin C and hair/skin tonics; moringa is a leafy tree used more as a broad-spectrum nutritional supplement."
            },
            {
                "compared_with": "Brahmi",
                "shared": "Both are cooling Ayurvedic rejuvenators used in long-term wellness formulations.",
                "difference": "Amla primarily nourishes tissues, digestion and hair; brahmi primarily supports memory, focus and the nervous system."
            }
        ]
    },


    "moringa": {
        "name": "Moringa",
        "scientific_name": "Moringa oleifera",
        "category": "Plant",
        "family": "Moringaceae",
        "rarity": "Common",
        "confidence": 95,

        "parts": [
            "Leaves",
            "Seeds",
            "Pods",
            "Flowers"
        ],

        "locations": [
            "India",
            "South Asia",
            "Africa",
            "Tropical regions"
        ],

        "growth_time": "6–12 months",

        "growth_timeline": [
            {
                "stage": "Germination",
                "duration": "1–3 weeks"
            },
            {
                "stage": "Seedling",
                "duration": "1–2 months"
            },
            {
                "stage": "Rapid vegetative growth",
                "duration": "2–5 months"
            },
            {
                "stage": "Flowering",
                "duration": "5–8 months"
            },
            {
                "stage": "Pod development",
                "duration": "6–12 months"
            }
        ],

        "traditional_uses": [
            "Traditional dietary use",
            "Traditional wellness preparations",
            "Traditional plant-based products"
        ],

        "safety": {
            "level": "Part and preparation dependent",
            "toxicity": "Different plant parts have different safety considerations.",
            "adverse_effects": "Potential effects depend on quantity and preparation.",
            "interactions": "Potential interactions should be evaluated."
        },

        "innovation": [
            "Nutritional product",
            "Functional food",
            "Plant-based powder",
            "Botanical wellness formulation"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Amla",
                "shared": "Both are nutrient-dense plants used as daily nourishing tonics.",
                "difference": "Moringa leaves deliver protein, iron and micronutrients as a food supplement; amla concentrates vitamin C and is used more for immunity, hair and digestion."
            },
            {
                "compared_with": "Turmeric",
                "shared": "Both have anti-inflammatory nutritional value and are used in wellness products.",
                "difference": "Turmeric delivers concentrated curcumin with strong research attention; moringa works as a whole-food leaf powder with broad nutritional support."
            }
        ]
    },


    "aloe vera": {
        "name": "Aloe Vera",
        "scientific_name": "Aloe barbadensis Mill.",
        "category": "Plant",
        "family": "Asphodelaceae",
        "rarity": "Common",
        "confidence": 94,

        "parts": [
            "Leaf gel",
            "Leaf latex"
        ],

        "locations": [
            "India",
            "North Africa",
            "Middle East",
            "Dry and tropical regions"
        ],

        "growth_time": "8–12 months for established leaves",

        "growth_timeline": [
            {
                "stage": "Plant establishment",
                "duration": "1–2 months"
            },
            {
                "stage": "Leaf development",
                "duration": "2–5 months"
            },
            {
                "stage": "Mature leaf formation",
                "duration": "5–8 months"
            },
            {
                "stage": "Established plant",
                "duration": "8–12 months"
            }
        ],

        "traditional_uses": [
            "Traditional topical preparations",
            "Traditional cosmetic applications"
        ],

        "safety": {
            "level": "Part-dependent",
            "toxicity": "Leaf gel and latex have different safety profiles.",
            "adverse_effects": "Preparation and plant part are important safety considerations.",
            "interactions": "Potential interactions require evidence review."
        },

        "innovation": [
            "Botanical cosmetic product",
            "Topical formulation",
            "Plant-based skincare concept"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Neem",
                "shared": "Both are commonly used in topical skin-care and Ayurvedic external preparations.",
                "difference": "Aloe gel cools, hydrates and soothes burns and irritation; neem is bitter and antimicrobial, targeting infections, acne and scalp problems."
            },
            {
                "compared_with": "Turmeric",
                "shared": "Both are classic ingredients of traditional topical pastes.",
                "difference": "Aloe is cooling and demulcent, used for burns and dryness; turmeric is warming and antiseptic, used for wounds and inflammation."
            }
        ]
    },


    "licorice": {
        "name": "Licorice",
        "scientific_name": "Glycyrrhiza glabra",
        "category": "Plant",
        "family": "Fabaceae",
        "rarity": "Uncommon",
        "confidence": 89,

        "parts": [
            "Root"
        ],

        "locations": [
            "India",
            "Mediterranean region",
            "Central Asia",
            "West Asia"
        ],

        "growth_time": "2–3 years",

        "growth_timeline": [
            {
                "stage": "Germination",
                "duration": "2–4 weeks"
            },
            {
                "stage": "Seedling",
                "duration": "1–3 months"
            },
            {
                "stage": "Root establishment",
                "duration": "3–12 months"
            },
            {
                "stage": "Root development",
                "duration": "1–2 years"
            },
            {
                "stage": "Harvest maturity",
                "duration": "2–3 years"
            }
        ],

        "traditional_uses": [
            "Traditional herbal preparations",
            "Traditional formulations"
        ],

        "safety": {
            "level": "Dose-dependent",
            "toxicity": "Excessive intake of some licorice preparations can present safety concerns.",
            "adverse_effects": "High or prolonged intake may produce adverse effects.",
            "interactions": "Potential interactions should be reviewed."
        },

        "innovation": [
            "Standardized botanical extract",
            "Herbal formulation",
            "Functional beverage concept"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Tulsi",
                "shared": "Both support respiratory health in traditional medicine.",
                "difference": "Licorice soothes and moistens dry, irritated airways and acts as a formulation harmonizer; tulsi provides aromatic, expectorant action that clears congestion and supports immunity."
            },
            {
                "compared_with": "Ashwagandha",
                "shared": "Both are rejuvenating tonics used in long-term wellness formulations.",
                "difference": "Licorice is sweet, demulcent and focused on throat, digestion and hormonal balance; ashwagandha is warming and focused on strength, sleep and stress adaptation."
            }
        ]
    }
}


# ============================================================
# COMPONENT DATABASE
# ============================================================

COMPONENTS = {

    "curcumin": {
        "name": "Curcumin",
        "scientific_name": "Curcuma longa derived compound",
        "category": "Ayurvedic Component",
        "source": "Turmeric rhizome",
        "rarity": "Commonly researched",
        "confidence": 93,

        "locations": [
            "Derived primarily from turmeric cultivated in India and other tropical regions"
        ],

        "growth_time": "Depends on turmeric cultivation: approximately 7–10 months",

        "growth_timeline": [
            {
                "stage": "Source plant cultivation",
                "duration": "7–10 months"
            },
            {
                "stage": "Rhizome harvesting",
                "duration": "At maturity"
            },
            {
                "stage": "Extraction",
                "duration": "Processing-dependent"
            },
            {
                "stage": "Standardization",
                "duration": "Processing-dependent"
            }
        ],

        "traditional_uses": [
            "Associated with traditional turmeric preparations",
            "Used in traditional formulations containing turmeric"
        ],

        "safety": {
            "level": "Preparation and dose dependent",
            "toxicity": "Safety depends on concentration, formulation and dose.",
            "adverse_effects": "Some concentrated preparations may cause adverse effects.",
            "interactions": "Potential interactions should be assessed."
        },

        "innovation": [
            "Standardized botanical formulation",
            "Functional food formulation",
            "Research-oriented delivery system",
            "Herbal cosmetic formulation"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Piperine",
                "shared": "Both are well-researched plant compounds from culinary spices.",
                "difference": "Curcumin provides anti-inflammatory and antioxidant activity but is poorly absorbed; piperine itself has mild activity but sharply increases curcumin's absorption, so they are often combined."
            },
            {
                "compared_with": "Ashwagandha Extract",
                "shared": "Both are standardized botanical extracts used in modern supplements.",
                "difference": "Curcumin targets inflammation and oxidative stress pathways; ashwagandha extract targets stress adaptation, sleep and hormonal support."
            }
        ]
    },


    "piperine": {
        "name": "Piperine",
        "scientific_name": "Piper nigrum derived alkaloid",
        "category": "Ayurvedic Component",
        "source": "Black pepper",
        "rarity": "Commonly available",
        "confidence": 91,

        "locations": [
            "India",
            "Southeast Asia",
            "Tropical regions"
        ],

        "growth_time": "Black pepper plant generally requires multiple years for full establishment",

        "growth_timeline": [
            {
                "stage": "Plant establishment",
                "duration": "Several months"
            },
            {
                "stage": "Vegetative growth",
                "duration": "1–2 years"
            },
            {
                "stage": "Fruit-bearing development",
                "duration": "Approximately 2–4 years"
            },
            {
                "stage": "Harvest",
                "duration": "Seasonal"
            }
        ],

        "traditional_uses": [
            "Traditional black pepper preparations",
            "Traditional spice formulations"
        ],

        "safety": {
            "level": "Dose-dependent",
            "toxicity": "Concentrated piperine can behave differently from culinary quantities.",
            "adverse_effects": "High amounts may cause irritation or other adverse effects.",
            "interactions": "Piperine can affect metabolism of some substances; evidence review is important."
        },

        "innovation": [
            "Botanical formulation research",
            "Standardized herbal formulation",
            "Controlled-delivery concept"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Curcumin",
                "shared": "Both are plant-derived compounds commonly formulated together.",
                "difference": "Piperine mainly acts as a bioavailability enhancer and digestive stimulant; curcumin is the primary anti-inflammatory agent in the pair."
            },
            {
                "compared_with": "Ginger",
                "shared": "Both are pungent digestive stimulants derived from spices.",
                "difference": "Ginger is a whole rhizome with anti-nausea and warming effects; piperine is an isolated alkaloid used mainly to enhance absorption of other compounds."
            }
        ]
    },


    "ashwagandha extract": {
        "name": "Ashwagandha Extract",
        "scientific_name": "Withania somnifera extract",
        "category": "Ayurvedic Component",
        "source": "Ashwagandha root",
        "rarity": "Commonly available",
        "confidence": 94,

        "locations": [
            "India",
            "South Asia"
        ],

        "growth_time": "Source plant generally requires approximately 6–12 months",

        "growth_timeline": [
            {
                "stage": "Ashwagandha cultivation",
                "duration": "6–12 months"
            },
            {
                "stage": "Root harvesting",
                "duration": "At maturity"
            },
            {
                "stage": "Extraction",
                "duration": "Processing-dependent"
            },
            {
                "stage": "Standardization",
                "duration": "Processing-dependent"
            }
        ],

        "traditional_uses": [
            "Traditional Ashwagandha formulations",
            "Traditional herbal preparations"
        ],

        "safety": {
            "level": "Preparation and dose dependent",
            "toxicity": "Safety depends on concentration, preparation and individual factors.",
            "adverse_effects": "Some individuals may experience adverse effects.",
            "interactions": "Potential interactions require evidence review."
        },

        "innovation": [
            "Standardized extract",
            "Herbal formulation",
            "Functional wellness product",
            "Controlled formulation research"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Curcumin",
                "shared": "Both are standardized Ayurvedic botanical extracts used in research and supplements.",
                "difference": "Ashwagandha extract supports adaptogenic stress response, sleep and strength; curcumin extract targets inflammatory pathways."
            },
            {
                "compared_with": "Ashwagandha",
                "shared": "Both deliver the same medicinal plant's benefits.",
                "difference": "The extract offers concentrated, standardized withanolides with convenient dosing; the whole root provides a broader spectrum of constituents in a traditional preparation."
            }
        ]
    }
}


# ============================================================
# PRODUCT DATABASE
# ============================================================

PRODUCTS = {

    "chyawanprash": {
        "name": "Chyawanprash",
        "category": "Ayurvedic Product",
        "rarity": "Common",
        "confidence": 90,

        "components": [
            "Amla",
            "Multiple traditional herbal ingredients",
            "Spices and botanical ingredients"
        ],

        "locations": [
            "Widely available across India"
        ],

        "growth_time": "Not applicable as a single product; depends on constituent plants",

        "growth_timeline": [
            {
                "stage": "Raw material cultivation",
                "duration": "Varies by botanical ingredient"
            },
            {
                "stage": "Raw material harvesting",
                "duration": "Ingredient-dependent"
            },
            {
                "stage": "Processing",
                "duration": "Manufacturing-dependent"
            },
            {
                "stage": "Product preparation",
                "duration": "Manufacturing-dependent"
            }
        ],

        "traditional_uses": [
            "Traditional Ayurvedic dietary preparation",
            "Traditional wellness formulation"
        ],

        "safety": {
            "level": "Formulation-dependent",
            "toxicity": "Safety depends on ingredients, formulation and consumption amount.",
            "adverse_effects": "Individual responses may vary.",
            "interactions": "Ingredients should be reviewed for potential interactions."
        },

        "innovation": [
            "Personalized herbal formulation research",
            "Ingredient traceability system",
            "Standardized botanical product",
            "Modern delivery-format concept"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Triphala",
                "shared": "Both are classical multi-herb Ayurvedic preparations used daily.",
                "difference": "Chyawanprash is a sweet amla-based jam for nourishment, immunity and respiratory strength; triphala is a simple three-fruit formulation mainly for gentle digestion and elimination."
            },
            {
                "compared_with": "Amla",
                "shared": "Both are centered on amla (Indian gooseberry).",
                "difference": "Chyawanprash combines amla with dozens of herbs, ghee and sugar in a cooked paste; raw amla is simpler, more acidic and used mainly for vitamin C and digestion."
            }
        ]
    },


    "triphala": {
        "name": "Triphala",
        "category": "Ayurvedic Product",
        "rarity": "Common",
        "confidence": 91,

        "components": [
            "Amla",
            "Haritaki",
            "Bibhitaki"
        ],

        "locations": [
            "India",
            "South Asia"
        ],

        "growth_time": "Depends on cultivation cycles of constituent plants",

        "growth_timeline": [
            {
                "stage": "Amla cultivation",
                "duration": "Several years to fruit-bearing maturity"
            },
            {
                "stage": "Haritaki cultivation",
                "duration": "Multiple years"
            },
            {
                "stage": "Bibhitaki cultivation",
                "duration": "Multiple years"
            },
            {
                "stage": "Processing and blending",
                "duration": "Manufacturing-dependent"
            }
        ],

        "traditional_uses": [
            "Traditional Ayurvedic formulation",
            "Traditional herbal preparation"
        ],

        "safety": {
            "level": "Formulation and dose dependent",
            "toxicity": "Safety depends on composition and amount consumed.",
            "adverse_effects": "Individual responses may vary.",
            "interactions": "Potential interactions should be evaluated."
        },

        "innovation": [
            "Standardized multi-herb formulation",
            "Ingredient traceability",
            "Modern dosage-format concept",
            "Quality-control system"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Chyawanprash",
                "shared": "Both are foundational classical Ayurvedic formulations.",
                "difference": "Triphala is a simple three-fruit blend used for digestion, cleansing and eye care; chyawanprash is a rich cooked jam used for nourishment and immunity."
            },
            {
                "compared_with": "Amla",
                "shared": "Both contain amla and support long-term wellness.",
                "difference": "Triphala balances amla with haritaki and bibhitaki for elimination; amla alone is a nutritive tonic stronger in vitamin C and hair/skin support."
            }
        ]
    },


    "neem oil": {
        "name": "Neem Oil",
        "category": "Ayurvedic / Botanical Product",
        "rarity": "Common",
        "confidence": 93,

        "components": [
            "Neem seed oil",
            "Botanical compounds"
        ],

        "locations": [
            "India",
            "South Asia",
            "Tropical regions"
        ],

        "growth_time": "Depends on neem tree maturity and seed production",

        "growth_timeline": [
            {
                "stage": "Neem cultivation",
                "duration": "Several years"
            },
            {
                "stage": "Seed production",
                "duration": "Seasonal"
            },
            {
                "stage": "Seed collection",
                "duration": "Seasonal"
            },
            {
                "stage": "Oil extraction",
                "duration": "Processing-dependent"
            }
        ],

        "traditional_uses": [
            "Traditional topical preparations",
            "Traditional personal-care applications",
            "Traditional agricultural applications"
        ],

        "safety": {
            "level": "Topical/use dependent",
            "toxicity": "Safety depends on concentration and route of use.",
            "adverse_effects": "Potential irritation or other effects may occur.",
            "interactions": "Use-specific evidence should be reviewed."
        },

        "innovation": [
            "Botanical personal-care formulation",
            "Natural crop-protection research",
            "Standardized neem oil product",
            "Sustainable botanical product"
        ],

        "medicinal_comparisons": [
            {
                "compared_with": "Neem",
                "shared": "Both come from the neem tree and share bitter, antimicrobial properties.",
                "difference": "Neem oil is a concentrated topical product for skin, scalp and crop protection; leaf and bark preparations are used as decoctions in traditional care."
            },
            {
                "compared_with": "Aloe Vera",
                "shared": "Both are popular topical skin-care agents.",
                "difference": "Neem oil combats microbes, pests and excess oil; aloe gel cools, hydrates and repairs irritated or sunburned skin."
            }
        ]
    }
}


# ============================================================
# COMBINED DATABASE
# ============================================================

DATABASE = {}

DATABASE.update(PLANTS)
DATABASE.update(COMPONENTS)
DATABASE.update(PRODUCTS)


# ============================================================
# CATEGORY KEYS (stable ids for UI icons)
# ============================================================

CATEGORY_KEYS = {}

for item_key in PLANTS:
    CATEGORY_KEYS[item_key] = "plant"

for item_key in COMPONENTS:
    CATEGORY_KEYS[item_key] = "component"

for item_key in PRODUCTS:
    CATEGORY_KEYS[item_key] = "product"


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_name(value: str) -> str:
    if not value:
        return ""

    value = value.lower().strip()

    # Keep unicode letters/digits (Hindi, Telugu searches)
    value = "".join(
        ch for ch in value
        if ch.isalnum() or ch.isspace()
    )

    value = re.sub(r"\s+", " ", value)

    return value


# ============================================================
# ALIASES
# ============================================================

ALIASES = {

    "ashwagandha root": "ashwagandha",
    "withania somnifera": "ashwagandha",

    "neem plant": "neem",
    "azadirachta indica": "neem",

    "holy basil": "tulsi",
    "ocimum sanctum": "tulsi",
    "ocimum tenuiflorum": "tulsi",

    "haldi": "turmeric",
    "curcuma longa": "turmeric",

    "adrak": "ginger",
    "zingiber officinale": "ginger",

    "bacopa": "brahmi",
    "bacopa monnieri": "brahmi",

    "indian gooseberry": "amla",
    "phyllanthus emblica": "amla",

    "drumstick": "moringa",
    "moringa oleifera": "moringa",

    "aloe": "aloe vera",
    "aloe barbadensis": "aloe vera",

    "glycyrrhiza glabra": "licorice",

    "curcumin compound": "curcumin",

    "piperine compound": "piperine",

    "chyawanprash": "chyawanprash",
    "chavanprash": "chyawanprash",

    "triphala": "triphala",

    "neem oil": "neem oil",

    # Hindi native names
    "अश्वगंधा": "ashwagandha",
    "नीम": "neem",
    "तुलसी": "tulsi",
    "हल्दी": "turmeric",
    "अदरक": "ginger",
    "ब्राह्मी": "brahmi",
    "आंवला": "amla",
    "मोरिंगा": "moringa",
    "एलोवेरा": "aloe vera",
    "मुलेठी": "licorice",
    "कर्क्यूमिन": "curcumin",
    "पाइपरिन": "piperine",
    "अश्वगंधा अर्क": "ashwagandha extract",
    "च्यवनप्राश": "chyawanprash",
    "त्रिफला": "triphala",
    "नीम तेल": "neem oil",

    # Telugu native names
    "అశ్వగంధ": "ashwagandha",
    "వేప": "neem",
    "తులసి": "tulsi",
    "పసుపు": "turmeric",
    "అల్లం": "ginger",
    "బ్రాహ్మి": "brahmi",
    "ఉసిరి": "amla",
    "మునగ": "moringa",
    "అలోవేరా": "aloe vera",
    "యష్టిమధు": "licorice",
    "కర్కుమిన్": "curcumin",
    "పైపెరిన్": "piperine",
    "అశ్వగంధ సారం": "ashwagandha extract",
    "చ్యవన్‌ప్రాశ్": "chyawanprash",
    "త్రిఫల": "triphala",
    "వేప నూనె": "neem oil",

    # Regional/common Indian language names
    "सहजन": "moringa",
    "मुनगा": "moringa",
    "यष्टिमधु": "licorice",
    "muringa": "moringa",
    "drumstick tree": "moringa"
}


# ============================================================
# LOCALIZED NAME INDEX
# (so searching the Hindi/Telugu display name also works)
# ============================================================

LOCALIZED_NAME_INDEX = {}

for lang_entries in TRANSLATIONS.values():

    for item_key, overrides in lang_entries.items():

        localized_name = overrides.get("name")

        if localized_name:
            LOCALIZED_NAME_INDEX[
                normalize_name(localized_name)
            ] = item_key


# ============================================================
# FIND DATABASE ITEM
# ============================================================

def find_item(name: str):

    normalized = normalize_name(name)

    if normalized in DATABASE:
        return normalized, DATABASE[normalized]

    if normalized in ALIASES:
        key = ALIASES[normalized]

        if key in DATABASE:
            return key, DATABASE[key]

    if normalized in LOCALIZED_NAME_INDEX:
        key = LOCALIZED_NAME_INDEX[normalized]

        if key in DATABASE:
            return key, DATABASE[key]

    # Partial matching
    for key in DATABASE:

        if normalized in key or key in normalized:

            return key, DATABASE[key]

    return None, None


# ============================================================
# LIST ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "application": "IP-SAKTHI Sahayak",
        "version": "4.0.0",
        "vision_model": OLLAMA_MODEL,
        "languages": SUPPORTED_LANGS
    }


@app.get("/api/items")
def get_items(lang: str = DEFAULT_LANG):

    lang = resolve_lang(lang)

    def pack(keys):

        return [
            {
                "key": key,
                "name": localize_item(
                    key, DATABASE[key], lang
                ).get("name", key)
            }
            for key in keys
        ]

    return {
        "plants": pack(list(PLANTS.keys())),
        "components": pack(list(COMPONENTS.keys())),
        "products": pack(list(PRODUCTS.keys()))
    }


# ============================================================
# ANALYZE TEXT / NAME
# ============================================================

@app.post("/api/analyze")
async def analyze_name(
    name: str,
    lang: str = DEFAULT_LANG
):

    lang = resolve_lang(lang)

    if not name or not name.strip():

        raise HTTPException(
            status_code=400,
            detail=get_message("empty_name", lang)
        )

    key, item = find_item(name)

    if not item:

        return {
            "success": False,
            "source": "text",
            "message": get_message("text_not_found", lang),
            "query": name
        }

    localized = localize_item(key, item, lang)

    return {
        "success": True,
        "source": "text",
        "identified_name": localized.get("name", name),
        "database_key": key,
        "category_key": CATEGORY_KEYS.get(key, "plant"),
        "data": localized
    }


# ============================================================
# IMAGE -> OLLAMA
# ============================================================

def ask_vision_model(image_bytes: bytes, lang: str = DEFAULT_LANG) -> str:

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    lang = resolve_lang(lang)
    language_name = LANG_NAMES[lang]

    prompt = f"""
You are the visual identification module of an Ayurveda research prototype.

Analyze the uploaded image carefully.

The image may contain:

1. An Ayurvedic medicinal plant
2. A plant part
3. An Ayurvedic raw component
4. An Ayurvedic medicine/product
5. A packaged herbal/Ayurvedic product

Identify the most likely item visible in the image.

Return ONLY JSON in this exact structure:

{{
  "identified_name": "name",
  "category": "plant/component/product",
  "confidence": 0,
  "visual_reason": "short reason"
}}

Important:
- identified_name must be an English common or botanical plant name
  (for example: Ashwagandha, Neem, Turmeric, Curcumin, Triphala).
- Do not invent brand information.
- If uncertain, give the closest likely identification.
- confidence should be a number from 0 to 100.
- Keep visual_reason short.
- Write visual_reason in {language_name}.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "images": [encoded_image],
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    return result.get("response", "")


# ============================================================
# PARSE VISION RESPONSE
# ============================================================

def parse_vision_result(raw_response: str):

    try:

        parsed = json.loads(raw_response)

        if isinstance(parsed, dict):

            return parsed

    except Exception:
        pass

    # Fallback if model returns extra text
    match = re.search(
        r"\{.*\}",
        raw_response,
        re.DOTALL
    )

    if match:

        try:

            return json.loads(match.group(0))

        except Exception:
            pass

    return {
        "identified_name": "",
        "category": "unknown",
        "confidence": 0,
        "visual_reason": raw_response[:300]
    }


# ============================================================
# IMAGE ANALYSIS ENDPOINT
# ============================================================

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    lang: str = Form(DEFAULT_LANG)
):

    lang = resolve_lang(lang)

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No image was uploaded."
        )

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/jpg"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG, PNG or WEBP image."
        )

    image_bytes = await file.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    # Validate image
    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image.verify()

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image."
        )

    # Send image to local vision model
    try:

        raw_response = ask_vision_model(
            image_bytes,
            lang
        )

    except requests.exceptions.ConnectionError:

        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama is not reachable. "
                "Please make sure Ollama is running."
            )
        )

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail=(
                "Vision analysis timed out. "
                "Please try a smaller image."
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Vision analysis failed: {str(error)}"
        )

    vision = parse_vision_result(
        raw_response
    )

    identified_name = vision.get(
        "identified_name",
        ""
    )

    model_confidence = vision.get(
        "confidence",
        0
    )

    visual_reason = vision.get(
        "visual_reason",
        ""
    )

    # Find item in prototype knowledge base
    key, item = find_item(
        identified_name
    )

    # If found
    if item:

        localized = localize_item(key, item, lang)

        return {

            "success": True,

            "source": "image",

            "identified_name":
                localized.get(
                    "name",
                    identified_name
                ),

            "database_key": key,

            "category_key": CATEGORY_KEYS.get(key, "plant"),

            "model_confidence":
                model_confidence,

            "visual_reason":
                visual_reason,

            "data": localized
        }

    # Unknown item
    return {

        "success": False,

        "source": "image",

        "identified_name":
            identified_name,

        "model_confidence":
            model_confidence,

        "visual_reason":
            visual_reason,

        "message": get_message("image_not_found", lang)
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    ollama_status = False

    try:

        response = requests.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=5
        )

        ollama_status = response.status_code == 200

    except Exception:

        ollama_status = False

    return {

        "backend": "online",

        "ollama": ollama_status,

        "vision_model":
            OLLAMA_MODEL,

        "plants":
            len(PLANTS),

        "components":
            len(COMPONENTS),

        "products":
            len(PRODUCTS)
    }

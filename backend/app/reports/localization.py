import json
from functools import lru_cache
from app.reports.config import SUPPORTED_LANGUAGES, TRANSLATION_ROOT

class MissingTranslationError(ValueError): pass

@lru_cache(maxsize=3)
def catalog(language: str) -> dict[str, str]:
    if language not in SUPPORTED_LANGUAGES: raise ValueError(f"Unsupported report language: {language}")
    values = json.loads((TRANSLATION_ROOT / f"{language}.json").read_text(encoding="utf-8"))
    baseline = json.loads((TRANSLATION_ROOT / "en.json").read_text(encoding="utf-8"))
    missing = sorted(set(baseline) - set(values))
    if missing: raise MissingTranslationError(f"Missing {language} translations: {', '.join(missing)}")
    return values

def translator(language: str):
    values = catalog(language)
    def translate(key: str) -> str:
        if key not in values: raise MissingTranslationError(f"Missing translation key: {key}")
        return values[key]
    return translate

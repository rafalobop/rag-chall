import re
from typing import Tuple

class GuardrailValidator:
    """Validates and corrections LLM outputs against formatting, emoji, and perspective rules."""

    PRONOUNS_1ST_2ND = [
        # Spanish
        r'\byo\b', r'\bnosotros\b', r'\bnosotras\b', r'\btú\b', r'\bvosotros\b', r'\bvosotras\b',
        r'\busted\b', r'\bustedes\b', r'\bmi\b', r'\bmis\b', r'\bnuestro\b', r'\bnuestra\b',
        r'\bnuestros\b', r'\bnuestras\b', r'\btu\b', r'\btus\b', r'\bvuestro\b', r'\bvuestra\b',
        r'\bme\b', r'\bnos\b', r'\bte\b', r'\bos\b', r'\bconmigo\b', r'\bcontigo\b',
        # English
        r'\bi\b', r'\bme\b', r'\bmy\b', r'\bmine\b', r'\bmyself\b', r'\bwe\b', r'\bus\b',
        r'\bour\b', r'\bours\b', r'\bourselves\b', r'\byou\b', r'\byour\b', r'\byours\b',
        r'\byourself\b', r'\byourselves\b',
        # Portuguese
        r'\beu\b', r'\bnós\b', r'\btu\b', r'\bvocê\b', r'\bvocês\b', r'\bmeu\b', r'\bmeus\b',
        r'\bminha\b', r'\bminhas\b', r'\bnosso\b', r'\bnossa\b', r'\bnossos\b', r'\bnossas\b',
        r'\bteu\b', r'\bteus\b', r'\btua\b', r'\btuas\b', r'\bvosso\b', r'\bvossa\b', r'\bme\b',
        r'\bnos\b', r'\bte\b', r'\bvos\b'
    ]

    def __init__(self):
        # Build compile pattern for whole-word case-insensitive pronouns
        self.pronouns_pattern = re.compile(
            "|".join(self.PRONOUNS_1ST_2ND),
            re.IGNORECASE
        )
        
        # Simple emoji identification: matches dingbats, symbols, and supplementary plane codepoints
        self.emoji_pattern = re.compile(
            r'[\U00010000-\U0010FFFF]|[\u2600-\u27BF]',
            re.UNICODE
        )

    def validate(self, text: str) -> Tuple[bool, str]:
        """Validates response against formatting rules. Returns (is_valid, error_reason)."""
        stripped = text.strip()

        # Rule 1: Exactly 1 period (ends with period)
        if stripped.count(".") != 1:
            return False, f"La respuesta debe contener exactamente un punto final. Encontrado: {stripped.count('.')}"

        if not stripped.endswith("."):
            return False, "La respuesta debe terminar con un punto."

        # Rule 2: Contains at least one emoji
        if not self.emoji_pattern.search(stripped):
            return False, "La respuesta debe contener al menos un emoji representativo."

        # Rule 3: Third person (absence of 1st / 2nd person pronouns)
        if self.pronouns_pattern.search(stripped):
            matches = self.pronouns_pattern.findall(stripped)
            return False, f"Se detectaron pronombres en primera o segunda persona: {list(set(matches))}"

        return True, ""

    def validate_and_correct(self, text: str, fallback_emoji: str = "🌌") -> str:
        """Validates LLM output, applies corrections if minor infractions occur, or raises ValueError."""
        is_valid, reason = self.validate(text)
        if is_valid:
            return text.strip()

        # Attempt minor corrections
        corrected = text.strip()

        # If it doesn't end with a period and has no periods, append one
        if corrected.count(".") == 0:
            corrected += "."
        # If it has multiple sentences/periods, keep only the first one
        elif corrected.count(".") > 1:
            parts = corrected.split(".")
            # Find the first part that actually contains letters/emojis
            for part in parts:
                p_strip = part.strip()
                if p_strip:
                    corrected = p_strip + "."
                    break

        # If it lacks emojis, append the fallback emoji before the final period
        if not self.emoji_pattern.search(corrected):
            if corrected.endswith("."):
                corrected = corrected[:-1] + f" {fallback_emoji}."
            else:
                corrected += f" {fallback_emoji}."

        # Final check
        is_valid, reason = self.validate(corrected)
        if not is_valid:
            raise ValueError(f"No se pudo corregir la respuesta de manera segura. Razón del fallo original: {reason}")

        return corrected

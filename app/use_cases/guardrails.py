import re
from typing import Tuple

class GuardrailValidator:
    """Valida y corrige las salidas del LLM de acuerdo a las reglas de formato, emojis y persona gramatical."""

    PRONOUNS_ES = [
        r'\byo\b', r'\bnosotros\b', r'\bnosotras\b', r'\btú\b', r'\bvosotros\b', r'\bvosotras\b',
        r'\busted\b', r'\bustedes\b', r'\bmi\b', r'\bmis\b', r'\bnuestro\b', r'\bnuestra\b',
        r'\bnuestros\b', r'\bnuestras\b', r'\btu\b', r'\btus\b', r'\bvuestro\b', r'\bvuestra\b',
        r'\bme\b', r'\bnos\b', r'\bte\b', r'\bos\b', r'\bconmigo\b', r'\bcontigo\b'
    ]

    PRONOUNS_EN = [
        r'\bi\b', r'\bme\b', r'\bmy\b', r'\bmine\b', r'\bmyself\b', r'\bwe\b', r'\bus\b',
        r'\bour\b', r'\bours\b', r'\bourselves\b', r'\byou\b', r'\byour\b', r'\byours\b',
        r'\byourself\b', r'\byourselves\b'
    ]

    PRONOUNS_PT = [
        r'\beu\b', r'\bnós\b', r'\btu\b', r'\bvocê\b', r'\bvocês\b', r'\bmeu\b', r'\bmeus\b',
        r'\bminha\b', r'\bminhas\b', r'\bnosso\b', r'\bnossa\b', r'\bnossos\b', r'\bnossas\b',
        r'\bteu\b', r'\bteus\b', r'\btua\b', r'\btuas\b', r'\bvosso\b', r'\bvossa\b', r'\bme\b',
        r'\bnos\b', r'\bte\b', r'\bvos\b'
    ]

    def __init__(self):
        self.pattern_es = re.compile("|".join(self.PRONOUNS_ES), re.IGNORECASE)
        self.pattern_en = re.compile("|".join(self.PRONOUNS_EN), re.IGNORECASE)
        self.pattern_pt = re.compile("|".join(self.PRONOUNS_PT), re.IGNORECASE)
        
        # Identificación simple de emojis: coincide con dingbats, símbolos y codepoints de planos suplementarios
        self.emoji_pattern = re.compile(
            r'[\U00010000-\U0010FFFF]|[\u2600-\u27BF]',
            re.UNICODE
        )

    def validate(self, text: str, language: str = "Spanish") -> Tuple[bool, str]:
        """Valida la respuesta contra las reglas de formato. Retorna (es_valido, razon_error)."""
        stripped = text.strip()

        # Regla 1: Exactamente 1 punto (termina en punto)
        if stripped.count(".") != 1:
            return False, f"La respuesta debe contener exactamente un punto final. Encontrado: {stripped.count('.')}"

        if not stripped.endswith("."):
            return False, "La respuesta debe terminar con un punto."

        # Regla 2: Contiene al menos un emoji
        if not self.emoji_pattern.search(stripped):
            return False, "La respuesta debe contener al menos un emoji representativo."

        # Regla 3: Tercera persona (ausencia de pronombres de 1ª o 2ª persona según el idioma)
        lang_lower = language.lower()
        if "en" in lang_lower or "eng" in lang_lower:
            pattern = self.pattern_en
        elif "pt" in lang_lower or "por" in lang_lower:
            pattern = self.pattern_pt
        else:
            pattern = self.pattern_es

        if pattern.search(stripped):
            matches = pattern.findall(stripped)
            return False, f"Se detectaron pronombres en primera o segunda persona: {list(set(matches))}"

        return True, ""

    def validate_and_correct(self, text: str, language: str = "Spanish", fallback_emoji: str = "🌌") -> str:
        """Valida la salida del LLM, aplica correcciones menores si hay infracciones leves, o lanza ValueError."""
        is_valid, reason = self.validate(text, language)
        if is_valid:
            return text.strip()

        # Intentar correcciones menores
        corrected = text.strip()

        # Si no termina con un punto y no tiene puntos, añadir uno
        if corrected.count(".") == 0:
            corrected += "."
        # Si tiene múltiples oraciones/puntos, mantener solo la primera
        elif corrected.count(".") > 1:
            parts = corrected.split(".")
            # Encontrar la primera parte que realmente contenga letras o emojis
            for part in parts:
                p_strip = part.strip()
                if p_strip:
                    corrected = p_strip + "."
                    break

        # Si le faltan emojis, añadir el emoji de respaldo antes del punto final
        if not self.emoji_pattern.search(corrected):
            if corrected.endswith("."):
                corrected = corrected[:-1] + f" {fallback_emoji}."
            else:
                corrected += f" {fallback_emoji}."

        # Verificación final
        is_valid, reason = self.validate(corrected, language)
        if not is_valid:
            raise ValueError(f"No se pudo corregir la respuesta de manera segura. Razón del fallo original: {reason}")

        return corrected

from app.use_cases.guardrails import GuardrailValidator

v = GuardrailValidator()
text = "The explorer Zara travels through hostile planets seeking to unravel the secrets of the ancient Zenthoria artifact to achieve galactic peace 🚀🌌."
is_valid, reason = v.validate(text)
print("Is Valid:", is_valid)
print("Reason:", reason)
if not is_valid:
    try:
        corr = v.validate_and_correct(text)
        print("Corrected:", corr)
    except Exception as e:
        print("Failed correction:", str(e))

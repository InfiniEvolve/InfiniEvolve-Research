"""Test-only evaluator, run by unmodified InfiniEvolve in a clean copy."""
import json
import math
import runpy

try:
    prediction = float(runpy.run_path("solution.py")["prediction"])
    valid = math.isfinite(prediction)
    mse = sum((prediction - target) ** 2 for target in [1.0, 2.0, 3.0]) / 3 if valid else None
except (KeyError, ValueError, TypeError, OSError, SyntaxError):
    valid, mse = False, None
print(json.dumps({"checks": {"finite_prediction": valid}, "metrics": {"mse": mse}}))

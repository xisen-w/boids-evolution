"""Versioned tool-mediated collaboration engineering testbed."""

import os

# Reproducible runtime: don't import user-wide dotenv/provider settings or fetch prices at import.
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["MSWEA_SILENT_STARTUP"] = "1"

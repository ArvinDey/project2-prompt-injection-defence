# Project 2 — Prompt Injection Defence

Flask and Ollama lab comparing an undefended baseline with input validation
and output scanning.

## Files
- app_baseline.py: undefended application
- app.py: defended application
- validate.py: input validation
- output_scanner.py: output scanning

## Run
1. Install dependencies: python -m pip install -r requirements.txt
2. Start Ollama and download the model configured in the application.
3. Run either python app_baseline.py or python app.py, one at a time.
4. Open http://127.0.0.1:5000

Training controls have limitations and require testing before production use.

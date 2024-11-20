test:
	pytest tests --cov=src --cov-report=xml --cov-report=term
run-api:
	uvicorn api.main:app --reload
format:
	black .

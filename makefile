test:
	pytest tests --cov=src --cov-report=xml --cov-report=term
run-api:
	uvicorn api.main:app --reload
format:
	black .
install:
	pip install -r requirements.txt
install-dev:
	make install 
	pip install -r requirements-dev.txt
.PHONY: setup run test clean docker-build docker-run docker-stop

setup:
	uv venv --clear
	uv pip install -e .

run:
	.\.venv\Scripts\python src/main.py

test:
	.\.venv\Scripts\python -m pytest tests -v

clean:
	if exist .venv rmdir /s /q .venv

docker-build:
	docker build -t telegram-llm-assistant .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down
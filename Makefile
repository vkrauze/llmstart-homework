.PHONY: setup run test clean

setup:
	uv venv --clear
	uv pip install -e .

run:
	.\.venv\Scripts\python src/main.py

test:
	.\.venv\Scripts\python -m pytest tests -v

clean:
	if exist .venv rmdir /s /q .venv
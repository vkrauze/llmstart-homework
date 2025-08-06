.PHONY: setup run test clean

setup:
	uv venv
	uv pip install -e .

run:
	python src/main.py

test:
	.\.venv\Scripts\python -m pytest tests -v

clean:
	if exist .venv rmdir /s /q .venv
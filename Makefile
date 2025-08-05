.PHONY: setup run clean

setup:
	uv venv
	uv pip install -e .

run:
	.\.venv\Scripts\python src/main.py

clean:
	rm -rf .venv
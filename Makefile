.PHONY: install test lint lint-fix clean build upload-test upload release

# Install p2p to user local directory and set up shell completion
install:
	pip install --user .
	p2p init
	@echo "Ensure ~/.local/bin is in your PATH to use p2p as a CLI."
	@echo "You can add it by running: export PATH=\$$PATH:~/.local/bin"

# Run tests
test:
	pytest tests/

# Lint the code
lint:
	isort . --check-only
	ruff check .

lint-fix:
	isort .
	ruff check --fix .

# Clean up compiled files
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

# Build distribution packages
build:
	python -m pip install --upgrade build
	python -m build

# Upload to PyPI (test server)
upload-test:
	python -m pip install --upgrade twine
	python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
upload:
	python -m pip install --upgrade twine
	python -m twine upload dist/*

# Clean, build and upload to PyPI
release: clean build upload

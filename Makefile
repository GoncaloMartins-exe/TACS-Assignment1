.PHONY: all run validate clean help

PYTHON = python
INSTANCES = input/4x4_two_queens.json input/4x4_one_queen.json input/5x5_two_queens.json

all: run

run:
	@$(PYTHON) run.py

validate:
	@$(PYTHON) validation.py

clean:
	@$(PYTHON) -c "import shutil, glob, os; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(p) if os.path.isdir(p) else os.remove(p) for p in glob.glob('output/*')]"

help:
	@echo "Available commands:"
	@echo "  make run       - Run the 3 main test instances through the pipeline"
	@echo "  make validate  - Run the full validation suite against the classical baseline"
	@echo "  make clean     - Remove files from output/ directory and Python caches"
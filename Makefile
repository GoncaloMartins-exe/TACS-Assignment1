.PHONY: all run validate clean help

PYTHON = python
INSTANCES = input/4x4_two_queens.json input/4x4_one_queen.json input/5x5_two_queens.json

all: run

# Run the pipeline sequentially on the 3 main test instances
run:
	@for file in $(INSTANCES); do \
		echo "\n========================================"; \
		echo "Executing pipeline for $$file"; \
		echo "========================================"; \
		$(PYTHON) pipeline.py $$file; \
	done

# Run the validation suite and generate output/validation_results.md
validate:
	@$(PYTHON) validation.py

# Clean generated artifacts and Python caches (cross-platform Windows/Linux/macOS)
clean:
	@$(PYTHON) -c "import shutil, glob, os; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(p) if os.path.isdir(p) else os.remove(p) for p in glob.glob('output/*')]"

help:
	@echo "Available commands:"
	@echo "  make run       - Run the 3 main test instances through the pipeline"
	@echo "  make validate  - Run the full validation suite against the classical baseline"
	@echo "  make clean     - Remove files from output/ directory and Python caches"
.PHONY: clean

clean:
	@echo "Cleaning *_report.txt files, *.log files and __pycache__ directories..."
	@find . -type f \( -name "*_report.txt" -o -name "*.log" \) -exec rm -f {} +
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Clean complete."

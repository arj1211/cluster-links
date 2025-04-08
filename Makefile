.PHONY: clean

clean:
	@echo "Cleaning *_report.txt files..."
	@find . -type f \( -name "*_report.txt" \) -exec rm -f {} +
	
	@echo "Cleaning *.log files..."
	@find . -type f \( -name "*.log" \) -exec rm -f {} +
	
	@echo "Cleaning tmp* files..."
	@find . -type f \( -name "tmp*" \) -exec rm -f {} +
	
	@echo "Cleaning DS_Store files..."
	@find . -type f \( -name ".DS_Store" \) -exec rm -f {} +
	
	@echo "Cleaning __pycache__ directories..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	
	@echo "Clean complete."

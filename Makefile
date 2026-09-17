.PHONY: test test-scraper test-unit test-validation

test-scraper:
	python3 -m pytest scraper/tests/ -v

test-unit:
	python3 -m pytest scraper/tests/test_scraper.py scraper/tests/test_validation.py -v

test-validation:
	python3 -m pytest scraper/tests/test_validation.py -v

test: test-scraper

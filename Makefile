.PHONY: install run test clean

install:
	pip install pybuilder
	pyb install_dependencies

run:
	pyb

test:
	pyb run_unit_tests

clean:
	rm -rf target/ dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true

PYTHON=python3
PIP=pip3

%.python_project:
	@echo "new python project"
	@echo "generating project template"
	putup $(basename $@)
	@echo "generating a Makefile"
	mv Makefile $(basename $@)
	@echo "generating venv"
	$(PYTHON) -m venv $(basename $@)/venv

local:
	@echo "quick-build"
	( \
		source venv/bin/activate; \
		pip install -r requirements.txt; \
	        $(PYTHON) setup.py develop; \
	)	

dist:
	$(PYTHON) -m pip install --user --upgrade setuptools wheel
	$(PYTHON) setup.py bdist_wheel

install: dist
	@echo "package gets installed to \$HOME/.local/bin"
	$(PIP) install --user . --no-warn-script-location


.PHONY: dist local

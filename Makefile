install: requirements.txt
	pip install -r requirements.txt
	touch install

notebook: install
	export PYTHONPATH=$$PYTHONPATH:$$(pwd) &&\
	echo $$PYTHONPATH &&\
	jupyter notebook

lint: install
	flake8 gtfs_isochrone
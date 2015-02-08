run:	compile
	python c.py

step:	compile
	python c.py --step

compile:
	python a.py > test



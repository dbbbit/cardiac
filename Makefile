run:	compile
	python cardiac.py

step:	compile
	python cardiac.py --step

compile:
	python asm.py > test



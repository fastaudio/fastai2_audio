SRC = $(wildcard nbs/*.ipynb)

all: fastai2_audio docs

fastai2_audio: $(SRC)
	nbdev_build_lib
	touch fastai2_audio

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist
FROM python:3

WORKDIR /src

USER root

RUN apt-get update && apt-get install python3-dev -y && \
	git clone https://github.com/wannesm/PySDD && \
	python -m pip install cython cysignals numpy problog

COPY problog_libs/sdd-2.0 /src/sdd-2.0

COPY problog_libs/libsdd-2.0 /src/libsdd-2.0

RUN	cp -r /src/libsdd-2.0/ /src/PySDD/pysdd/lib/libsdd-2.0  && \
	cp -r /src/sdd-2.0/ /src/PySDD/pysdd/lib/sdd-2.0  && \
	cd PySDD && python setup.py install

RUN python -m pip install pytest pytest-xdist pytest-cov mypy requests coverage

COPY .coveragerc pytest.ini /src/

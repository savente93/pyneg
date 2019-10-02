FROM python:3

WORKDIR /src

ENV user sam

#make sure we own the files we create so they don't end up being owned by root in the host
RUN useradd  ${user} && \
    chown -R ${user} /src && \
    chmod g+s .;

RUN apt-get update && apt-get install python3-dev -y --no-install-recommends && \
	git clone https://github.com/wannesm/PySDD && \
	python -m pip install cython cysignals numpy problog && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

COPY --chown=${user} problog_libs/sdd-2.0 /src/sdd-2.0

COPY --chown=${user} problog_libs/libsdd-2.0 /src/libsdd-2.0

RUN	cp -r /src/libsdd-2.0/ /src/PySDD/pysdd/lib/libsdd-2.0  && \
	cp -r /src/sdd-2.0/ /src/PySDD/pysdd/lib/sdd-2.0  && \
	cd PySDD && python setup.py install

RUN python -m pip install pytest pytest-xdist pytest-cov mypy requests coverage pandas

COPY --chown=${user} .coveragerc pytest.ini /src/

USER ${user}
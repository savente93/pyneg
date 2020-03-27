FROM problog:latest

ENV user sam

WORKDIR /src

RUN useradd  ${user} && \
    chown -R ${user} /src && \
    chmod -R g+s /src

RUN python -m pip install pytest pytest-xdist pytest-cov mypy 

COPY --chown=${user} . /src/

#COPY --chown=${user} test/ /src/test/
#COPY --chown=${user} .coveragerc pytest.ini setup.py README.md test/ /src/

RUN pip install . 

USER ${user}

cmd ["pytest", "test"]

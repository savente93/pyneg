FROM problog:latest

ENV user sam

WORKDIR /src

RUN useradd  ${user} && \
    chown -R ${user} /src && \
    chmod -R g+s /src

RUN python -m pip install pytest pytest-xdist pytest-cov mypy pyneg

COPY --chown=${user} test/ /src/test/

USER ${user}

cmd ["pytest", "test"]

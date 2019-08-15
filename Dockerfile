FROM python:3

WORKDIR /src

COPY . /src

RUN pip install --upgrade --force-reinstall --no-binary pysdd pysdd

RUN pip install numpy problog uuid pandas

CMD ["python", "-m", "unittest", "tests/test_randomNegotiationAgent.py"]

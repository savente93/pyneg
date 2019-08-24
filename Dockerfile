FROM python:3

WORKDIR /src

COPY . /src

RUN pip install --upgrade --no-binary pysdd pysdd

RUN pip install numpy problog

CMD ["python", "-m", "unittest", "discover", "test/"]

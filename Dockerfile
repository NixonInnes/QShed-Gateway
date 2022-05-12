FROM python:3.10

WORKDIR /code
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

COPY ./pyproject.toml /code/pyproject.toml
COPY ./config.py /code/config.py
COPY ./gateway /code/gateway
COPY ./packages /code/packages

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 4000
CMD ["uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "4000"]
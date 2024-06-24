FROM python:3.12

WORKDIR /bot

EXPOSE 80/udp

COPY src/ /bot

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry

COPY poetry.lock pyproject.toml /bot/

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction


CMD ["poetry", "run", "python", "bot.py" ]

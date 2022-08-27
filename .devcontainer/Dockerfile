FROM lukewiwa/pythons

RUN ln -sf /usr/local/bin/python3.7 /usr/local/bin/python
RUN ln -sf /usr/local/bin/pip3.7 /usr/local/bin/pip

# Install poetry
ENV POETRY_VIRTUALENVS_CREATE="false"
RUN python -m pip install poetry
# Install project deps
COPY poetry.lock pyproject.toml /tmp/pip-tmp/
RUN cd /tmp/pip-tmp && poetry install && rm -rf /tmp/pip-tmp

RUN apt update && apt install -y sqlite3 vim ssh-client

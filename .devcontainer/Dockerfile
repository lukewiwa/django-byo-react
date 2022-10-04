FROM lukewiwa/pythons:36-37-38-39-310

RUN ln -sf /usr/local/bin/python3.7 /usr/local/bin/python
RUN ln -sf /usr/local/bin/pip3.7 /usr/local/bin/pip

# Install poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT="true"
RUN python -m pip install poetry

RUN apt update && apt install -y sqlite3 vim ssh-client

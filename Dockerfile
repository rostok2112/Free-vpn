FROM python:3.12 as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV DATABASE_URL  ${DATABASE_URL}

FROM base AS deps

# Install dependencies
RUN python -m pip install --upgrade pip
RUN pip install pipenv


# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Copy sources
COPY . /code

# Run the application
ENTRYPOINT ["/code/run.sh"]

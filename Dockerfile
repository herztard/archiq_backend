FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV HOME=/home/app
ENV APP_HOME=/code
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update -y && apt-get install -y gettext  \
    build-essential  \
    libssl-dev  \
    git  \
    python3-dev  \
    gcc  \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt $APP_HOME
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . $APP_HOME

RUN python3 manage.py collectstatic --noinput

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

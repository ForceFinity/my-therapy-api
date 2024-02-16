FROM python:3.11.8
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY . $APP_HOME/api
WORKDIR $APP_HOME/api

EXPOSE 8000
CMD ["uvicorn", "main:application", "--host", "0.0.0.0", "--port", "8000"]
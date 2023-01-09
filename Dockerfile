FROM python:3.10
WORKDIR /recipe-backend
copy requirements.txt /recipe-backend
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
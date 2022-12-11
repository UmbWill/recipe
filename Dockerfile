FROM python:3.10
WORKDIR /tsp_solver
copy requirements.txt /tsp_solver
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
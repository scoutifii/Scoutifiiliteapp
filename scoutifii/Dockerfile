FROM python:3.13.7-alpine3.22

# Set the default django project name
ARG PROJ_NAME="Scoutifii"

# create and set working directory
RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# Add current directory code to the working directory
COPY . /app/

# set default environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noniteractive

RUN python3 -m venv /opt/venv /opt/venv/bin/pip install pip --upgrade && \
/opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \ 
chmod +x entrypoint.sh 


CMD ["/app/entrypoint.sh"]
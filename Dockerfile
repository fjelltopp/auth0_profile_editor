FROM ghcr.io/fjelltopp/fjelltopp-base-images/python-fjelltopp-base:3.10

COPY ./ /var/www/ape
WORKDIR /var/www/ape
RUN mkdir .venv && pipenv sync

EXPOSE 5003

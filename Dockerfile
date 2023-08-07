FROM fjelltopp/python-fjelltopp-base:3.9

COPY ./ /var/www/ape
WORKDIR /var/www/ape
RUN mkdir .venv && pipenv sync

EXPOSE 5003

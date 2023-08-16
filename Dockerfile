FROM ghcr.io/fjelltopp/fjelltopp-base-images/python-fjelltopp-base:3.10

COPY ./ /var/www/profile_editor
WORKDIR /var/www/profile_editor
RUN mkdir .venv && pipenv sync

EXPOSE 5003

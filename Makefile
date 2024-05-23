version := $(shell git describe --tags --always)
image_tag := thatisfine/gruhoedb:$(version)

build:
	docker build -t $(image_tag) --no-cache --force-rm .

push:
	docker push $(image_tag)

local:
	gunicorn --log-level=debug -b 127.0.0.1:8080 gruhoedb.webserver:app

localdebug:
	flask --app gruhoedb.webserver:app run --debug

clean:
	docker image prune -a
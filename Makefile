version := $(shell git describe --always)
image_tag := thatisfine/gruhoedb:$(version)

build:
	docker build -t $(image_tag) --no-cache --force-rm .

push:
	docker push $(image_tag)

local:
	docker run -p 8080:8080 --env-file=.env $(image_tag)
version := $(shell git describe --always)
image_tag := thatisfine/gruhoedb:$(version)

build:
	docker build -t $(image_tag) .

push:
	docker push $(image_tag)
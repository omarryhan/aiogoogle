import json
from pathlib import Path

import pytest

from aiogoogle.resource import GoogleAPI


@pytest.fixture
def open_discovery_document():
    def wrapped(name, version):
        json_file = Path(__file__).parent / "data" / f"{name}_{version}_discovery_doc.json"
        with json_file.open("r") as discovery_doc:
            return json.loads(discovery_doc.read())

    return wrapped


@pytest.fixture
def create_api(open_discovery_document):
    def wrapped(name, version):
        disc_doc = open_discovery_document(name, version)
        return GoogleAPI(discovery_document=disc_doc)

    return wrapped


@pytest.fixture
def methods_generator(create_api):
    def wrapped(name, version):
        gapi = create_api(name, version)

        def generator(resource):
            for method_name in resource.methods_available:
                yield resource._get_method(method_name)
            for nested_resource in resource.resources_available:
                yield from generator(resource._get_resource(nested_resource))

        return generator(gapi)

    return wrapped


@pytest.fixture
def resources_generator(create_api):
    def wrapped(name, version):
        gapi = create_api(name, version)

        # Returns a generator that yields either a Resource or a GoogleAPI object
        def generator(resource):
            yield resource
            for resource_name in resource.resources_available:
                yield resource._get_resource(resource_name)
            for nested_resource in resource.resources_available:
                yield from generator(resource._get_resource(nested_resource))

        return generator(gapi)

    return wrapped

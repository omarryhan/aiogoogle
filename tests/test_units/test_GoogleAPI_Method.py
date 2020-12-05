import pytest

from aiogoogle.resource import GoogleAPI, Method, STACK_QUERY_PARAMETERS
from ..ALL_APIS import ALL_APIS


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_parameters_exist_in_discovery_document(open_discovery_document, name, version):
    discovery_document = open_discovery_document(name, version)
    api = GoogleAPI(discovery_document=discovery_document)
    for resource_name, _ in discovery_document.get("resources").items():
        resource = getattr(api, resource_name)
        for method_name in resource.methods_available:
            method = resource._get_method(method_name)
            for parameter_name, _ in method.parameters.items():
                assert (
                    parameter_name in discovery_document.get("parameters")
                    or parameter_name
                    in discovery_document["resources"][resource_name]["methods"][
                        method_name
                    ]["parameters"]
                )


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_optional_parameters_are_filtered_correctly(
    open_discovery_document, name, version, methods_generator
):
    for method in methods_generator(name, version):
        for parameter_name in method.optional_parameters:
            parameter = method.parameters[parameter_name]
            assert parameter.get("required") is not True


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_required_parameters_are_filtered_correctly(
    open_discovery_document, name, version, methods_generator
):
    for method in methods_generator(name, version):
        for parameter_name in method.required_parameters:
            parameter = method.parameters[parameter_name]
            assert parameter.get("required") is True


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_path_parameters_are_filtered_correctly(open_discovery_document, name, version, methods_generator):
    for method in methods_generator(name, version):
        for parameter_name in method.path_parameters:
            parameter = method.parameters[parameter_name]
            assert parameter.get("location") == "path"


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_query_parameters_are_filtered_correctly(
    open_discovery_document, name, version, methods_generator
):
    for method in methods_generator(name, version):
        for parameter_name in method.query_parameters:
            parameter = method.parameters[parameter_name]
            assert parameter.get("location") == "query"


def test_getitem():
    method = Method(
        name="IRRELEVANT",
        method_specs={"am_i_here_1": True, "am_i_here_2": None},
        global_parameters={"IRRELEVANT": "IRRELAVANT"},
        schemas={"IRRELEVANT": "IRRELEVANT"},
        batch_path="IRRELEVANT",
        root_url="IRRELEVANT",
        service_path="IRRELEVANT",
        validate=False,
    )

    assert method["am_i_here_1"] is True
    assert method["am_i_here_2"] is None
    assert method["i_dont_exist"] is None


@pytest.mark.parametrize("name,version", ALL_APIS)
def test__len__returns_int(open_discovery_document, name, version, methods_generator):
    for method in methods_generator(name, version):
        assert isinstance(len(method), int)


@pytest.mark.parametrize("name,version", ALL_APIS)
def test_stack_parameters_are_passed_correctly(open_discovery_document, name, version, methods_generator):
    for method in methods_generator(name, version):
        for stack_param_name in STACK_QUERY_PARAMETERS:
            assert stack_param_name in method.optional_parameters
            assert stack_param_name in method.parameters

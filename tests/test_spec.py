import pytest

from infrared import api
from infrared.core.utils.exceptions import IRRequiredArgsMissingException, \
    IRExtraVarsException, IRInvalidMinMaxRangeException, IRException
from tests.test_execute import spec_fixture  # noqa
from tests.test_workspace import workspace_manager_fixture, test_workspace  # noqa


@pytest.mark.parametrize("cli_args, should_pass", [  # noqa
    ("--req-arg-a=yes", False),
    ("--req-arg-b=yes", True),
    ("--version=10", True),
    ("--version=11", False),
    ("--version=11 --uni-int=uni-str", True),
    ("--req-arg-a=yes --req-arg-b=yes", False),
    ("--req-arg-a=no --req-arg-b=yes", True),
    ("--req-arg-a=yes --req-arg-b=no", False),
    ("--req-arg-a=yes --uni-dep=uni-val", True),
    ("--req-arg-b=yes --multi-dep=multi-val", True),
    ("--req-arg-a=yes --uni-dep=uni-val --multi-dep=multi-val", True),
    ("--req-arg-a=yes --uni-dep=not-uni --multi-dep=multi-val ", False),
    ("--req-arg-a=yes --uni-dep=not-uni --multi-dep=multi-val --uni-neg-dep=uni-neg-val", True),
])
def test_required_when(spec_fixture, workspace_manager_fixture, test_workspace,
                       cli_args, should_pass):
    """Tests the 'required_when' mechanism

    :param spec_fixture: Fixtures which creates 'testing spec' (tests/example)
    :param workspace_manager_fixture: Fixture which sets the default workspace
      directory
    :param test_workspace: Fixture which creates temporary workspace directory
    :param cli_args: CLI arguments
    :param should_pass: Boolean value tells whether the test should pass or not
    :return:
    """
    spec_manager = api.SpecManager()
    spec_manager.register_spec(spec_fixture)

    workspace_manager_fixture.activate(test_workspace.name)

    if should_pass:
        rc = spec_manager.run_specs(args=['example'] + cli_args.split())
        assert rc == 0, "Execution failed, return code is: {}".format(rc)
    else:
        with pytest.raises(IRRequiredArgsMissingException):
            spec_manager.run_specs(args=['example'] + cli_args.split())


def test_extra_vars(spec_fixture, workspace_manager_fixture, test_workspace):
    """ Verify the --extra-vars parameter is validated"""
    spec_manager = api.SpecManager()
    spec_manager.register_spec(spec_fixture)

    workspace_manager_fixture.activate(test_workspace.name)
    assert spec_manager.run_specs(args=['example', '-e', 'key=value']) == 0

    with pytest.raises(IRExtraVarsException):
        spec_manager.run_specs(args=['example', '-e', 'key'])


@pytest.mark.parametrize("cli_args, should_pass", [
    ("--value-minmax=10", False),
    ("--value-minmax=100", True),
    ("--value-minmax=150", True),
    ("--value-minmax=200", True),
    ("--value-minmax=250", False),
])
def test_min_max_args(spec_fixture, workspace_manager_fixture, test_workspace,
                       cli_args, should_pass):
    """Tests the 'minimum' and 'maximum' support

    :param spec_fixture: Fixtures which creates 'testing spec' (tests/example)
    :param workspace_manager_fixture: Fixture which sets the default workspace
      directory
    :param test_workspace: Fixture which creates temporary workspace directory
    :param cli_args: CLI arguments
    :param should_pass: Boolean value tells whether the test should pass or not
    :return:
    """
    spec_manager = api.SpecManager()
    spec_manager.register_spec(spec_fixture)

    workspace_manager_fixture.activate(test_workspace.name)

    if should_pass:
        rc = spec_manager.run_specs(args=['example'] + cli_args.split())
        assert rc == 0, "Execution failed, return code is: {}".format(rc)
    else:
        with pytest.raises(IRInvalidMinMaxRangeException):
            spec_manager.run_specs(args=['example'] + cli_args.split())


def test_min_max_corrupted_spec(spec_fixture, workspace_manager_fixture,
                                test_workspace):
    """Tests the 'minimum' and 'maximum' support

    :param spec_fixture: Fixtures which creates 'testing spec' (tests/example)
    :param workspace_manager_fixture: Fixture which sets the default workspace
      directory
    :param test_workspace: Fixture which creates temporary workspace directory
    :return:
    """
    spec_manager = api.SpecManager()
    spec_manager.register_spec(spec_fixture)

    workspace_manager_fixture.activate(test_workspace.name)

    spec_groups = spec_fixture.specification.parser['example']['groups']
    for group in spec_groups:
        if group['title'] == 'Group F':
            options = group['options']
            # edit value-minimum
            options['value-minmax']['minimum'] = 'text_instead_of_number'
            options['value-minmax']['maximum'] = 'text_instead_of_number'

    with pytest.raises(IRException):
        spec_manager.run_specs(args=['example', '--value-minmax=150'])

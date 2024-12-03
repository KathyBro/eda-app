import shutil
import os

import pytest
import tempfile

from click.testing import CliRunner
from cli.app import main
from tests.integration.cli.utils import schedule_session


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as dir:
        yield dir  # this will be a valid path


# *********** CREATE SCHEDULE TESTS **************
def test_create_schedule_with_new_path_that_doesnt_exist_in_optional_and_fails(
    temp_dir,
):
    runner = CliRunner()
    result = runner.invoke(
        main, ["schedule", "create", "My CLI Test Schedule", "-d", "dne"]
    )
    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_create_schedule_with_new_path_that_exists_in_optional_and_succeeds(temp_dir):
    runner = CliRunner()
    schedule_name = "My CLI Test Schedule"
    result = runner.invoke(main, ["schedule", "create", schedule_name, "-d", temp_dir])
    assert os.path.exists(os.path.join(temp_dir, f"{schedule_name}.yaml"))
    assert result.exit_code == 0


def test_create_schedule_double_slash_in_path_succeeds(temp_dir):
    runner = CliRunner()
    schedule_name = "My CLI Test Schedule"
    real_dir = os.path.join(temp_dir, ".//")
    result = runner.invoke(main, ["schedule", "create", schedule_name, "-d", real_dir])
    assert os.path.exists(os.path.join(real_dir, f"{schedule_name}.yaml"))
    assert result.exit_code == 0


def test_create_schedule_without_directory_path_succeeds(
    default_schedule_in_current_dir,
):
    runner = CliRunner()
    result = runner.invoke(
        main, ["schedule", "create", default_schedule_in_current_dir]
    )
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, f"{default_schedule_in_current_dir}.yaml")
    assert os.path.exists(full_path), f"File did not exist: {full_path}"
    assert result.exit_code == 0, result.output


# *********** CREATE SCHEDULE - INVALID FILE NAME TESTS *********
def test_create_schedule_with_invalid_forward_slash_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test/ Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_invalid_back_slash_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test\\ Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_pipe_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test| Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


# File is not created with the colon, however a file is created with the name before the colon. TODO Ask Milo about this/ research even more about how truncating works
# def test_create_schedule_with_colon_in_file_name_fails():
#     runner = CliRunner()
#     result = runner.invoke(main, ["schedule", "create", "My CLI Test: Schedule"])
#     assert result.exit_code == 1


def test_create_schedule_with_question_mark_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test? Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_asterisk_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test* Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_double_quote_in_file_name_fails():
    runner = CliRunner()
    with schedule_session('My CLI Test" Schedule') as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_less_alligator_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test< Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_greater_alligator_in_file_name_fails():
    runner = CliRunner()
    with schedule_session("My CLI Test> Schedule") as name:
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1


def test_create_schedule_with_space_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", " "])
    assert result.exit_code == 1


def test_create_schedule_with_no_characters_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", ""])
    assert result.exit_code == 1


def test_create_schedule_with_duplicate_name_throws_error():
    with schedule_session("My CLI Test Schedule") as name:
        runner = CliRunner()
        runner.invoke(main, ["schedule", "create", name])
        result = runner.invoke(main, ["schedule", "create", name])
        assert result.exit_code == 1

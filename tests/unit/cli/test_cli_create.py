import shutil
import os

from click.testing import CliRunner
from cli.app import main


# *********** CREATE SCHEDULE TESTS **************
def test_create_schedule_with_new_path_that_doesnt_exist_in_optional_and_fails():
    runner = CliRunner()
    result = runner.invoke(
        main, ["schedule", "create", "My CLI Test Schedule", "-d", "/tmp_test/"]
    )
    assert result.exit_code == 2
    assert "Directory '/tmp_test/' does not exist" in result.output


def test_create_schedule_with_new_path_that_exists_in_optional_and_succeeds():
    runner = CliRunner()
    if not os.path.exists("/tmp_test/"):
        os.mkdir("/tmp_test/")
    result = runner.invoke(
        main, ["schedule", "create", "My CLI Test Schedule", "-d", "/tmp_test/"]
    )
    assert os.path.exists("/tmp_test/My CLI Test Schedule.yaml")
    shutil.rmtree("/tmp_test/")
    assert result.exit_code == 0


def test_create_schedule_double_slash_in_path_succeeds():
    runner = CliRunner()
    if not os.path.exists("/tmp_test/"):
        os.mkdir("/tmp_test/")
    result = runner.invoke(
        main, ["schedule", "create", "My CLI Test Schedule", "-d", "/tmp_test//"]
    )
    assert os.path.exists("/tmp_test/My CLI Test Schedule.yaml")
    shutil.rmtree("/tmp_test/")
    assert result.exit_code == 0


def test_create_schedule_without_directory_path_succeeds():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test Schedule"])
    current_dir = os.getcwd()
    assert os.path.exists(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 0


# *********** CREATE SCHEDULE - INVALID FILE NAME TESTS *********
def test_create_schedule_with_invalid_forward_slash_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test/ Schedule"])
    assert result.exit_code == 1


def test_create_schedule_with_invalid_back_slash_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test\\ Schedule"])
    assert result.exit_code == 1


def test_create_schedule_with_pipe_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test| Schedule"])
    assert result.exit_code == 1


# File is not created with the colon, however a file is created with the name before the colon. TODO Ask Milo about this/ research even more about how truncating works
# def test_create_schedule_with_colon_in_file_name_fails():
#     runner = CliRunner()
#     result = runner.invoke(main, ["schedule", "create", "My CLI Test: Schedule"])
#     assert result.exit_code == 1


def test_create_schedule_with_question_mark_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test? Schedule"])
    assert result.exit_code == 1


def test_create_schedule_with_asterisk_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test* Schedule"])
    assert result.exit_code == 1


def test_create_schedule_with_double_quote_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", 'My CLI Test" Schedule'])
    assert result.exit_code == 1


def test_create_schedule_with_less_alligator_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test< Schedule"])
    assert result.exit_code == 1


def test_create_schedule_with_greater_alligator_in_file_name_fails():
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test> Schedule"])
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
    runner = CliRunner()
    result = runner.invoke(main, ["schedule", "create", "My CLI Test Schedule"])
    result = runner.invoke(main, ["schedule", "create", "My CLI Test Schedule"])
    current_dir = os.getcwd()
    os.remove(os.path.join(current_dir, "My CLI Test Schedule.yaml"))
    assert result.exit_code == 1

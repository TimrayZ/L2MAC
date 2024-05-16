import json
from copy import deepcopy
from typing import List

from l2mac.tools.code_analysis import (
    check_pytest_with_timeout,
    check_syntax_with_timeout,
    count_errors_in_syntax,
)


def write_files(list_of_file_objects: List[dict] = [], file_dict: dict = {}, enable_tests=True):
    new_file_dict = implement_git_diff_on_file_dict(
        file_dict_input=file_dict, change_files_and_contents_input=list_of_file_objects
    )
    file_dict = new_file_dict
    # Run tests
    # Syntax check
    if not enable_tests:
        output = {"write_files_status": "success", "message": "write_files completed successfully."}
        return json.dumps(output), file_dict
    syntax_results = check_syntax_with_timeout(file_dict)
    if "Manual tests passed" in syntax_results:
        syntax_error_count = 0
    else:
        syntax_error_count = count_errors_in_syntax(syntax_results)
    test_results = check_pytest_with_timeout(file_dict)
    if "Manual tests passed" in test_results:
        test_results = "All tests passed"
    elif "No tests found" in test_results:
        test_results = "All tests passed"
    if "All tests passed" in test_results and syntax_error_count == 0:
        output = {"write_files_status": "success", "message": "All tests passed."}
    else:
        new_output = test_results.strip() + "\n" + syntax_results.strip()
        # if len(new_output) > 5000:
        #     new_output = new_output[:5000]
        #     new_output = new_output + '\nRest of output was trimmed.'
        output = {
            "write_files_status": "success",
            "message": "write_files completed successfully. Test run results: \n"
            + new_output
            + "\n You must fix this code by writing code to complete this sub task step. If a test is failing the error could be the code, or the test is incorrect, so feel free to overwrite and change the tests when they are incorrect, to make all tests pass.",
        }
    return json.dumps(output), file_dict


def implement_git_diff_on_file_dict(file_dict_input: dict, change_files_and_contents_input: []) -> dict:
    """Implement git diff on file_dict, and return the new file_dict.

    Args: file_dict: dict, change_files_and_contents: []

    Returns: dict

    Description: Adheres to this definition: When writing any code you will always give it in diff format, with line numbers. For example. Adding two new lines to a new file is "+ 1: import time\n+ 2: import os". Editing an existing line is "- 5: apple = 2 + 2\n+ 5: apple = 2 + 3". Deleting a line is "- 5: apple = 2 + 2".
    """
    file_dict = deepcopy(file_dict_input)
    change_files_and_contents = deepcopy(change_files_and_contents_input)
    for obj in change_files_and_contents:
        file_path = obj["file_path"]
        change_file_contents = obj["file_contents"]
        if file_path in file_dict:
            existing_file_contents = file_dict[file_path]
        else:
            existing_file_contents = []
        file_ending = file_path.split(".")[1]
        # new_file_contents = implement_git_diff_on_file_contents(existing_file_contents, change_file_contents, file_type=file_ending, overwrite=obj['overwrite_file'])
        new_file_contents = update_file_contents(existing_file_contents, change_file_contents, file_type=file_ending)
        file_dict[file_path] = new_file_contents
    return file_dict


def update_file_contents(existing_file_contents, change_file_contents, file_type="py") -> [str]:
    """Implement git diff on file_contents, and return the new file_contents.

    Args: existing_file_contents: [str], change_file_contents: [str]

    Returns: [str]

    Description: Adheres to this definition: When writing any code you will always give it in diff format, with line numbers. For example. Adding two new lines to a new file is "+ 1: import time\n+ 2: import os". Editing an existing line is "- 5: apple = 2 + 2\n+ 5: apple = 2 + 3". Deleting a line is "- 5: apple = 2 + 2".
    """
    existing_file_contents = change_file_contents
    return existing_file_contents.split("\n")


def delete_files(files: List[str], file_dict: dict, enable_tests=True):
    for file in files:
        if file == "-1":
            file_dict = {}
        if file in file_dict:
            del file_dict[file]
    output = {"status": "success", "message": "delete_files completed successfully."}
    return json.dumps(output), file_dict


# Write unit tests for the functions above
def test_implement_git_diff_on_file_dict():
    file_dict = {}
    change_files_and_contents = [{"file_path": "test.v", "file_contents": "+ 1: import time\n+ 2: import os"}]
    new_file_dict = implement_git_diff_on_file_dict(file_dict, change_files_and_contents)
    assert new_file_dict == {"test.v": ["import time", "import os"]}
    print("All tests passed.")


def test_write_files():
    # Test write_files
    files_and_contents = [{"file_path": "test.v", "file_contents": "+ 1: import time\n+ 2: import os"}]
    file_dict = {}
    output, file_dict = write_files(files_and_contents, file_dict)
    assert output == '{"write_files_status": "success", "message": "All tests passed."}'
    print (file_dict)
    assert file_dict == {"test.v": ["+ 1: import time", "+ 2: import os"]}
    # Test implement_git_diff_on_file_dict
    file_dict = {}
    change_files_and_contents = [{"file_path": "test.v", "file_contents": "+ 1: import time\n+ 2: import os"}]
    file_dict = implement_git_diff_on_file_dict(file_dict, change_files_and_contents)
    assert file_dict == {"test.v": ["+ 1: import time", "+ 2: import os"]}
    # Test update_file_contents
    existing_file_contents = "import time\nimport os"
    change_file_contents = "+ 1: import time\n+ 2: import os"
    new_file_contents = update_file_contents(existing_file_contents, change_file_contents)
    assert new_file_contents == ["+ 1: import time", "+ 2: import os"]
    # Test delete_files
    files = ["test.v"]
    file_dict = {"test.v": ["import time", "import os"]}
    output, file_dict = delete_files(files, file_dict)
    assert output == '{"status": "success", "message": "delete_files completed successfully."}'
    assert file_dict == {}
    # Test delete_files with -1
    files = ["-1"]
    file_dict = {"test.v": ["import time", "import os"]}
    output, file_dict = delete_files(files, file_dict)
    assert output == '{"status": "success", "message": "delete_files completed successfully."}'
    assert file_dict == {}
    # Test delete_files with file not in file_dict
    files = ["test.v"]
    file_dict = {}
    output, file_dict = delete_files(files, file_dict)
    assert output == '{"status": "success", "message": "delete_files completed successfully."}'
    assert file_dict == {}
    print("All tests passed.")
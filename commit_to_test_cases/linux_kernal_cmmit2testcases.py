
import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
import git
from git import GitCommandError, exc
from loguru import logger

# inputs commit_id_txt file path and linux_kernel repo path
# before and after the commit, generate test cases for each commit
# output test cases to commit_to_test_cases/linux_kernel_test_cases/{commit_id}/
# only C/C++ files are considered
# example input /root/code_check/commits/commits-debug.txt   /root/code_check/linux
SUPPORTED_EXTENSIONS = {
	".c",
	".h",
	".cc",
	".hh",
	".hpp",
	".cpp",
	".cxx",
}
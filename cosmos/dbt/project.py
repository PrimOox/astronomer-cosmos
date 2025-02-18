from __future__ import annotations

from pathlib import Path
import shutil
import os
from cosmos.constants import DBT_LOG_DIR_NAME, DBT_TARGET_DIR_NAME, DBT_PARTIAL_PARSE_FILE_NAME
from contextlib import contextmanager
from typing import Generator


def create_symlinks(project_path: Path, tmp_dir: Path, ignore_dbt_packages: bool) -> None:
    """Helper function to create symlinks to the dbt project files."""
    ignore_paths = [DBT_LOG_DIR_NAME, DBT_TARGET_DIR_NAME, "profiles.yml"]
    if ignore_dbt_packages:
        # this is linked to dbt deps so if dbt deps is true then ignore existing dbt_packages folder
        ignore_paths.append("dbt_packages")
    for child_name in os.listdir(project_path):
        if child_name not in ignore_paths:
            os.symlink(project_path / child_name, tmp_dir / child_name)


def copy_msgpack_for_partial_parse(project_path: Path, tmp_dir: Path) -> None:
    partial_parse_file = Path(project_path) / DBT_TARGET_DIR_NAME / DBT_PARTIAL_PARSE_FILE_NAME

    if partial_parse_file.exists():
        tmp_target_dir = tmp_dir / DBT_TARGET_DIR_NAME
        tmp_target_dir.mkdir(exist_ok=True)

        shutil.copy(str(partial_parse_file), str(tmp_target_dir / DBT_PARTIAL_PARSE_FILE_NAME))


@contextmanager
def environ(env_vars: dict[str, str]) -> Generator[None, None, None]:
    """Temporarily set environment variables inside the context manager and restore
    when exiting.
    """
    original_env = {key: os.getenv(key) for key in env_vars}
    os.environ.update(env_vars)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value

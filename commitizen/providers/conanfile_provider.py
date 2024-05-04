from commitizen.providers.base_provider import FileProvider
from commitizen.exceptions import CommitizenException, ExitCode
from typing import ClassVar, Generator, Tuple
from os import path
import re


class ConanfileVersionException(CommitizenException):
    exit_code = ExitCode.NO_VERSION_SPECIFIED

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.message = message


class ConanfileProvider(FileProvider):
    """
    Conan provider where the version is explicitly placed in the conanfile.py.
    """

    filename: ClassVar[str] = "conanfile.py"
    re_pattern = re.compile(r"\s*version\s*=\s*(?P<version>.*)$")

    def _check_conanfile_exists(self):
        if not path.exists(self.file):
            message = f"Could not find {self.file} " "in the root of this project."
            raise FileExistsError(message)

    def _conanfile_lines(self) -> Generator[str, None, None]:
        self._check_conanfile_exists()

        with open(self.file) as f:
            lines = f.readlines()

        yield from lines

    def _find_version(self) -> Tuple[str, int, str]:
        """Find the version in the conanfile.py

        Raises:
            ConanfileVersionException: If the version cannot be found

        Returns:
            Tuple[str, int, str]: Tuple of the version, the line number where
                                  it was found and the original line.
        """
        match = None
        for line_num, line in enumerate(self._conanfile_lines()):
            match = re.search(ConanfileProvider.re_pattern, line)
            if match is not None:
                break

        # We got to the end of the conanfile without a match
        if match is None:
            message = (
                f"Could not find a version string in "
                "proveded conanfile at "
                f"{path.realpath(ConanfileProvider.filename)}."
            )
            raise ConanfileVersionException(message=message)

        # Final strip to get rid of white space
        return (match.group("version").strip('"').strip("'").strip(), line_num, line)

    def get_version(self) -> str:
        """Get the version string from the conanfile.py

        Returns:
            str: The version string
        """
        version, _, _ = self._find_version()
        return version

    def set_version(self, version: str) -> None:
        """Write the version to the conanfile.py

        Args:
            version (str): The version string to write
        """
        with open(ConanfileProvider.filename) as f:
            lines = f.readlines()

        prev_version, line_num, line = self._find_version()
        replaced_line = line.replace(prev_version, version)
        lines[line_num] = replaced_line

        with open(ConanfileProvider.filename, "w") as f:
            f.writelines(lines)

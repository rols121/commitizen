from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.conanfile_provider import ConanfileProvider

# Typical layout for conan version 1
CONANFILE_CONAN_V1 = """\
class TestConan(ConanFile):
    name = "test"
    version = "1.0.3"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Test here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run("git clone https://github.com/conan-io/hello.git")
"""

CONANFILE_CONAN_V1_EXPECTED = """\
class TestConan(ConanFile):
    name = "test"
    version = "7.31.67"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Test here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run("git clone https://github.com/conan-io/hello.git")
"""

# Typical layout for conan version 2
CONANFILE_CONAN_V2 = """\
class testRecipe(ConanFile):
    name = "test"
    version = "1.0.3"
    package_type = "library"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of test package here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
"""

CONANFILE_CONAN_V2_EXPECTED = """\
class testRecipe(ConanFile):
    name = "test"
    version = "7.31.67"
    package_type = "library"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of test package here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
"""


@pytest.mark.parametrize(
    "content, expected",
    (
        (CONANFILE_CONAN_V1, CONANFILE_CONAN_V1_EXPECTED),
        (CONANFILE_CONAN_V2, CONANFILE_CONAN_V2_EXPECTED),
    ),
)
def test_conanfile_provider(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = ConanfileProvider.filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "conanfile"

    provider = get_provider(config)
    assert isinstance(provider, ConanfileProvider)
    assert provider.get_version() == "1.0.3"

    provider.set_version("7.31.67")
    assert file.read_text() == dedent(expected)

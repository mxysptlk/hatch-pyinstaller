import os
import shutil
import PyInstaller.__main__ as pyinstaller
from pathlib import Path
from typing import Any, Callable
from hatchling.builders.config import BuilderConfig
from hatchling.builders.plugin.interface import BuilderInterface
from hatchling.builders.utils import normalize_relative_path


class PyInstallerConfig(BuilderConfig):
    def pyinstaller_options(self) -> list[str]:
        path_options_single = (
            "distpath",
            "workpath",
            "upx-dir",
            "specpath",
            "name",
            "contents-directroy",
            "paths ",
            "icon",
            "splash",
            "upx-exclude",
            "runtime-tmpdir",
        )
        path_options_multi = (
            "add-data",
            "add-binary",
            "hidden-import",
            "collect-submodules",
            "collect-data",
            "collect-binaries",
            "collect-all",
            "copy-metadata",
            "recursive-copy-metadata",
            "additional-hooks-dir",
            "runtime-hook",
            "exclude-module",
        )
        other = (
            "debug",
            "optimize-level",
            "version-file",
            "manifest",
            "osx-bundle-identifier",
            "codesign-identity",
            "osx-entitlements-file",
        )
        build_options = []
        if "scriptname" in self.target_config:
            build_options.append(self.target_config["scriptname"])
        else:
            build_options.append(f"{self.target_config['project_name']}.py")
        build_options.extend(self.target_config["flags"])
        for option in self.target_config:
            if option in path_options_single:
                if option == "paths":
                    paths = self.target_config[option].split(",")
                    paths = [p for p in map(normalize_relative_path, paths)]
                    build_options.extend(["--paths", ",".join(paths)])
                else:
                    build_options.extend(
                        [
                            f"--{option}",
                            normalize_relative_path(self.target_config[option]),
                        ]
                    )
            elif option in path_options_multi:
                for value in self.target_config[option]:
                    if option in ("add-data", "add-binary"):
                        src, dst = value.split(":")
                        value = f"{normalize_relative_path(src)}:{normalize_relative_path(dst)}"
                        build_options.extend([f"--{option}", value])
                    else:
                        build_options.extend(
                            [
                                f"--{option}",
                                normalize_relative_path(value),
                            ]
                        )
            elif option in other:
                build_options.extend([f"--{option}", self.target_config[option]])
        return build_options


class PyInstallerBuilder(BuilderInterface):
    PLUGIN_NAME = "pyinstaller"

    @classmethod
    def get_config_class(cls) -> BuilderConfig:
        return PyInstallerConfig

    def get_version_api(self) -> dict[str, Callable[..., Any]]:
        return {"app": self.build_app}

    def build_app(self, directory: str, **build_data: Any) -> str:
        project_name = self.normalize_file_name_component(self.metadata.core.raw_name)
        self.target_config["project_name"] = project_name
        pyinstaller.run(self.config.pyinstaller_options())

        dist_dir = Path(directory, project_name)
        extra_files = []

        if self.metadata.core.readme_path:
            extra_files.append(self.metadata.core.readme_path)
        if self.metadata.core.license_files:
            extra_files.extend(self.metadata.core.license_files)
        for f in extra_files:
            shutil.copy2(f, dist_dir)
        return os.fspath(dist_dir)

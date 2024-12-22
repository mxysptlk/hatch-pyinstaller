import os
import shutil
import PyInstaller.__main__ as pyinstaller
from pathlib import Path
from typing import Any, Callable
from hatchling.builders.config import BuilderConfig
from hatchling.builders.plugin.interface import BuilderInterface

class PyInstallerConfig(BuilderConfig):
    def pyinstaller_options(self) -> list[str]:
        """ Extract & format pysintaller options from self.target_config
        """
        option_names = {
            "distpath",
            "workpath",
            "upx-dir",
            "specpath",
            "name",
            "contents-directory",
            "paths",
            "icon",
            "splash",
            "upx-exclude",
            "runtime-tmpdir",
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
            "debug",
            "optimize-level",
            "version-file",
            "manifest",
            "osx-bundle-identifier",
            "codesign-identity",
            "osx-entitlements-file",
        }
        build_options = [""] # first element of the list will contain the scriptname and is filled in later on
        build_options.extend(self.target_config["flags"]) # append options with no argument
        # Append options with arguments
        for option, values in self.target_config.items():
            if option in option_names:
                if not isinstance(values, list):
                    values = [values]

                for value in values:
                    build_options.append(f'--{option}={value}')
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
        pyinstaller_options = self.config.pyinstaller_options()

        if "scriptname" in self.target_config:
            scriptname = self.target_config["scriptname"]
            if isinstance(scriptname, list):
                scriptnames = self.target_config["scriptname"]
            else:
                scriptnames = [scriptname]
        else:
            scriptnames = [f"{self.target_config['project_name']}.py"]

        for scriptname in scriptnames:
            pyinstaller_options[0] = scriptname
            pyinstaller.run(pyinstaller_options)

        dist_dir = Path(directory, project_name)
        extra_files = []

        if self.metadata.core.readme_path:
            extra_files.append(self.metadata.core.readme_path)
        if self.metadata.core.license_files:
            extra_files.extend(self.metadata.core.license_files)
        for f in extra_files:
            shutil.copy2(f, Path(directory, project_name + '_' + f))
        return os.fspath(dist_dir)

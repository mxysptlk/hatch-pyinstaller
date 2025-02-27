import os
import shutil
import zipfile
from pathlib import Path
import tempfile

from typing import Any, Callable
from hatchling.builders.config import BuilderConfig
from hatchling.builders.plugin.interface import BuilderInterface
import PyInstaller.__main__ as pyinstaller

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

    def build_app(self, directory: str, **_build_data: Any) -> str:
        project_name = self.normalize_file_name_component(self.metadata.core.raw_name)

        # extract list of script(s) to build and ensure to have it as a list
        scriptnames = self.target_config.get("scriptname", f"{project_name}.py")
        if not isinstance(scriptnames, list):
            scriptnames = [scriptnames]

        # dist dir can be hatch's dist path or pyinstaller option distpath.
        dist_dir = Path(self.target_config.get("distpath", directory))
        dist_dir.mkdir(parents = True, exist_ok = True)
        dist_dir /= project_name

        # update <distpath> in function of zip option.
        # when zipping, use a temp directory
        create_zip = self.target_config.get("zip", False)
        if create_zip:
            temp_dir = tempfile.TemporaryDirectory()
            self.target_config["distpath"] = temp_dir.name
        else:
            self.target_config["distpath"] = str(dist_dir)

        if len(scriptnames) > 1 and "name" in self.target_config:
            print("WARNING: '--name' is incompatible with bundling multiple scriptnames. It is ignored.")
            self.target_config.pop("name")

        # Construct pyinstaller arguments - to do only once all coherency checks are done
        pyinstaller_options = self.config.pyinstaller_options()

        for scriptname in scriptnames:
            pyinstaller_options[0] = scriptname
            pyinstaller.run(pyinstaller_options)

        extra_files = []
        if self.metadata.core.readme_path:
            extra_files.append(self.metadata.core.readme_path)
        if self.metadata.core.license_files:
            extra_files.extend(self.metadata.core.license_files)

        if not create_zip:
            for f in extra_files:
                shutil.copy2(f, dist_dir.parent / f'{dist_dir.name}_{f}')
        else:
            # zip is located in hatch dist, zip name mimics wheel & sdist naming rules
            dist_dir = dist_dir.parent / f'{dist_dir.name}-{self.metadata.version}.bin.zip'
            with zipfile.ZipFile(dist_dir, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _dirs, files in os.walk(Path(temp_dir.name), topdown = False):
                    for name in files:
                        zipped_file = Path(root, name)
                        zf.write(zipped_file, zipped_file.relative_to(temp_dir.name))

                for f in extra_files:
                    zf.write(f, Path(f).name)

        return os.fspath(dist_dir)

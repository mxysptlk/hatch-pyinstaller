# hatch-pyinstaller

-----

This is a [Hatch](https://hatch.pypa.io/latest/) plugin that provides
a custom builder to support building binaries using [PyInstaller](https://pyinstaller.org). Any licence or readme files will be copied to the `dist` directory.

This is something I found useful for building my own personal use apps, and thought I would share. It is offered without waranty or gaurentee of support. I am not a developer or IT professional of any kind. If you find this usefull, and want to take ownership, let me know. 

## Usage

Add hatch-pyinstaller to your build dependencies, then add PyInstaller options to `[tool.hatch.build.targets.pyinstaller]`. Yor app's main script can be specified with `scriptname = "myscript.py"`. Otherwise the builder will assume as script with the same name as the project in the project's root directory. Also, you will need to add `require-runtime-dependencies = true` to the target config or else PyInstaller won't be able to find your imported modules.

All valid PyInstaller options should be functional. Options that do not take an argument are added to a flags list: `flags = ["--onedir", "--clean"]`. Options that take an argument have their own entry `log-level = "WARN"`. For options that can be used multiple times use a list of strings for the value: `collect-data = ["some_module", "some_other_module" ]`. For a full list of option, see https://pyinstaller.org/en/stable/usage.html#options.

## Example

Project directory:
```
.
├── pyproject.toml
├── LICENSE.txt
├── README.md
├── foo.py
├── foo
│   ├── bar
│   │   └── more-code.py
│   ├── baz
│   │   ├── data.txt
│   │   └── even-more-code.py
│   └── my-code.py
```
`pyproject.toml`
```toml
[project]
name = "foo"
version = "0.1"
dependencies = ["some_module"]

[build-system]
requires = [
    "hatchling",
    "hatch-pyinstaller",
]
build-backend = "hatchling.build"

[tool.hatch.build.targets.pyinstaller]
require-runtime-dependencies = true
flags = ["--clean", "--onedir"]
collect-submodules = ["bar", "baz"]
log-level = "WARN"
```
build command:
```
hatch build --target pyinstaller
```

## Author
William Smith <williams@citisyn.net>

## License
`hatch-pyinstaller` is distributed under the terms of [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
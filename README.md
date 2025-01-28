# hatch-pyinstaller

-----

This is a [Hatch](https://hatch.pypa.io/latest/) plugin that provides
a custom builder to support building binaries using [PyInstaller](https://pyinstaller.org). Any licence or readme files will be copied to the `dist` directory.

This is something I found useful for building my own personal use apps, and thought I would share. It is offered without waranty or gaurentee of support. I am not a developer or IT professional of any kind. If you find this usefull, and want to take ownership, let me know. 

## Usage

Add hatch-pyinstaller to your build dependencies, then add PyInstaller options to `[tool.hatch.build.targets.pyinstaller]`. Yor app's main script(s) can be specified with `scriptname = "myscript.py"` or `scriptname = ["myscript1.py", "myscript2.py"]` if you have multiple script to build. Otherwise the builder will assume as script with the same name as the project in the project's root directory. Also, you will need to add `require-runtime-dependencies = true` to the target config or else PyInstaller won't be able to find your imported modules.

All valid PyInstaller options should be functional. You can only define 1 set of options that are applied on all built scripts (= values of `scriptname`). Options that do not take an argument are added to a flags list: `flags = ["--onedir", "--clean"]`. Options that take an argument have their own entry `log-level = "WARN"`. For options that can be used multiple times use a list of strings for the value: `collect-data = ["some_module", "some_other_module" ]`. For a full list of option, see https://pyinstaller.org/en/stable/usage.html#options.

Zipping:  
If you want built scripts to be bundled in a zip file, add `zip = true` in `[tool.hatch.build.targets.pyinstaller]`.  
Zip file is created in hatch \<dist\> folder, named as per standard naming convention: _{distribution}-{version}.bin.zip_.


Compatibility warnings:  
`--name` option cannot be defined if several scripts are to be built.  
If this occurs, the option is ignored and a warning message is displayed.

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
zip = true
```
build command:
```
hatch build --target pyinstaller
```

## Author
William Smith <williams@citisyn.net>

## License
`hatch-pyinstaller` is distributed under the terms of [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).
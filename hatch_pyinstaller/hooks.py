from hatchling.plugin import hookimpl

from .builder import PyInstallerBuilder


@hookimpl
def hatch_register_builder():
    return PyInstallerBuilder

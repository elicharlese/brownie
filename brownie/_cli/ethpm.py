#!/usr/bin/python3

from docopt import docopt

from brownie._config import CONFIG
from brownie.exceptions import ProjectNotFound
from brownie.network.web3 import _resolve_domain
from brownie.project import check_for_project, ethpm
from brownie.utils import color, notify

__doc__ = """Usage: brownie ethpm <command> [<arguments> ...] [options]

Commands:
  list                             List packages installed in this project
  install <uri> [overwrite=False]  Install a package in this project
  unlink <name>                    Unlink a package in this project
  remove <name>                    Remove an installed package from this project
  show <uri>                       Show detailed information about a package
  all                              List all locally available packages

Options:
  --help -h              Display this message

...TODO...
"""


def main():
    args = docopt(__doc__)
    command = args["<command>"]
    if command not in ("all", "install", "remove", "list", "show", "unlink"):
        print("Invalid command. Try brownie ethpm --help")
        return
    if command == "all":
        return _all()
    project_path = check_for_project(".")
    if project_path is None:
        raise ProjectNotFound
    if command == "list":
        _list(project_path)
    if command == "show":
        _show(project_path, *args["<arguments>"])
    if command == "install":
        _install(project_path, *args["<arguments>"])
    if command == "unlink":
        _unlink(project_path, *args["<arguments>"])
    if command == "remove":
        _remove(project_path, *args["<arguments>"])


def _all():
    for path in sorted(CONFIG["brownie_folder"].glob("data/ethpm/*")):
        package_list = [i.stem for i in sorted(path.glob("*"))]
        if not package_list:
            path.unlink()
            continue
        address = path.stem
        try:
            domain = _resolve_domain(address)
            print(f"{color['bright magenta']}erc1319://{domain}{color}")
        except Exception:
            print(address)
        for name in package_list:
            u = "\u2514" if name == package_list[-1] else "\u251c"
            print(f" {color['bright black']}{u}\u2500{color['bright white']}{name}{color}")


def _list(project_path):
    installed, modified = ethpm.get_installed_packages(project_path)
    package_list = sorted(installed.union(modified))
    if modified:
        notify(
            "WARNING",
            f"One or more files in {len(modified)} packages have been modified since installation.",
        )
        print("Unlink or reinstall them to silence this warning.")
        print(f"Modified packages name are highlighted in {color['bright blue']}blue{color}.\n")
    print(f"Found {color('bright magenta')}{len(package_list)}{color} installed packages:")
    for name in package_list:
        u = "\u2514" if name == package_list[-1] else "\u251c"
        c = color("bright blue") if name in modified else color("bright white")
        print(f" {color('bright black')}{u}\u2500{c}{name}{color}")


def _show(project_path):
    # TODO
    pass


def _install(project_path, uri, replace=False):
    if replace:
        if replace.lower() not in ("true", "false"):
            raise
        replace = eval(replace.capitalize())
    print(f'Attempting to install package at "{color("bright magenta")}{uri}{color}"')
    name = ethpm.install_package(project_path, uri, replace)
    print(f'The "{color("bright magenta")}{name}{color}" package was installed successfully.')


def _unlink(project_path, name):
    ethpm.remove_package(project_path, name, False)
    print(f'The "{color("bright magenta")}{name}{color}" package was successfully unlinked.')


def _remove(project_path, name):
    ethpm.remove_package(project_path, name, True)
    print(f'The "{color("bright magenta")}{name}{color}" package was successfully removed.')

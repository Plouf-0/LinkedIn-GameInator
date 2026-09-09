"""Locate SWI-Prolog at build time and list what the frozen app needs.

Used by `linkedin-gameinator.spec`. `swipl --dump-runtime-variables` is the
portable way to ask an installation where it lives, so the same code works on
Windows, Linux and macOS without hardcoded paths.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

# Parts of the SWI-Prolog home the resolver never touches. Skipping them keeps
# the executable to a sane size (the full home is well over 100 MB).
EXCLUDED_HOME_DIRS = {
    "app",
    "bin",
    "cmake",
    "customize",
    "demo",
    "desktop",
    "doc",
    "include",
    "xpce",
}

# The .rc files are the interactive initialisation scripts. An embedded engine
# does not want them -- they pull in optional libraries we do not ship and print
# an alarming "source_sink does not exist" error on startup.
EXCLUDED_HOME_FILES = {
    "README.md",
    "Uninstall.exe",
    "swipl-win.rc",
    "swipl.ico",
    "swipl.rc",
}

_VARIABLE = re.compile(r'^(?P<name>\w+)="(?P<value>.*)";?$')


class SwiplNotFound(RuntimeError):
    """Raised when no SWI-Prolog installation can be inspected."""


def find_swipl() -> str | None:
    """Locate the `swipl` executable, PATH first then the usual places.

    Not relying on PATH alone matters on Windows, where an installer may not
    have refreshed the environment of the running shell.
    """
    found = shutil.which("swipl")
    if found:
        return found

    candidates: list[Path] = []
    if sys.platform == "win32":
        # Same registry key pyswip reads, so we agree on the installation.
        try:
            import winreg

            with winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"Software\SWI\Prolog") as key:
                home, _ = winreg.QueryValueEx(key, "home")
                candidates.append(Path(home) / "bin" / "swipl.exe")
        except (ImportError, OSError):
            pass
        candidates += [
            Path(r"C:\Program Files\swipl\bin\swipl.exe"),
            Path(r"C:\Program Files (x86)\swipl\bin\swipl.exe"),
        ]
    else:
        candidates += [
            Path("/usr/lib/swi-prolog/bin/swipl"),
            Path("/usr/local/bin/swipl"),
            Path("/opt/homebrew/bin/swipl"),
        ]

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def runtime_variables() -> dict[str, str]:
    """Return the variables reported by `swipl --dump-runtime-variables`."""
    swipl = find_swipl()
    if swipl is None:
        raise SwiplNotFound("`swipl` could not be found; install SWI-Prolog before building.")

    output = subprocess.run(
        [swipl, "--dump-runtime-variables"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    variables: dict[str, str] = {}
    for line in output.splitlines():
        match = _VARIABLE.match(line.strip())
        if match:
            variables[match.group("name")] = match.group("value")
    return variables


def library_dependencies(libswipl: Path) -> list[Path]:
    """Return the sibling shared libraries `libswipl` needs.

    Only libraries shipped next to it are considered: system libraries are
    resolved by the OS, and PyInstaller already handles the ones it can see.
    """
    if sys.platform != "win32":
        # PyInstaller's dependency analysis covers ELF and Mach-O well enough.
        return []

    # These are the non-system DLLs libswipl.dll links against. Listing them by
    # name rather than parsing the PE imports keeps the spec dependency-free.
    names = (
        "libgcc_s_seh-1.dll",
        "libwinpthread-1.dll",
        "libgmp-10.dll",
        "zlib1.dll",
    )
    return [libswipl.parent / name for name in names if (libswipl.parent / name).exists()]


def collect() -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return `(binaries, datas)` entries for the PyInstaller spec.

    Binaries land at the top level of the bundle, where the loader already
    looks; the Prolog home is copied under a `swipl/` subdirectory, which the
    runtime hook then points `SWI_HOME_DIR` at.
    """
    variables = runtime_variables()

    home = Path(variables["PLBASE"])
    libswipl = Path(variables.get("PLLIBSWIPL") or "")
    if not home.is_dir():
        raise SwiplNotFound(f"SWI-Prolog home does not exist: {home}")
    if not libswipl.is_file():
        raise SwiplNotFound(f"libswipl does not exist: {libswipl}")

    binaries = [(str(libswipl), ".")]
    binaries += [(str(path), ".") for path in library_dependencies(libswipl)]

    datas: list[tuple[str, str]] = []
    for entry in home.iterdir():
        if entry.name in EXCLUDED_HOME_DIRS:
            continue
        if entry.is_dir():
            datas.append((str(entry), f"swipl/{entry.name}"))
        elif entry.is_file() and entry.name not in EXCLUDED_HOME_FILES:
            datas.append((str(entry), "swipl"))

    return binaries, datas


if __name__ == "__main__":
    collected_binaries, collected_datas = collect()
    print(f"libswipl and friends ({len(collected_binaries)}):")
    for source, _ in collected_binaries:
        print(f"  {source}")
    print(f"home entries ({len(collected_datas)}):")
    for source, destination in collected_datas:
        print(f"  {source} -> {destination}")

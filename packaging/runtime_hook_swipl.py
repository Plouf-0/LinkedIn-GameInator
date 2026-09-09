"""Point pyswip at the SWI-Prolog bundled inside the frozen application.

PyInstaller runs this before any of the application's own imports, which is
what makes it work: `pyswip.core` locates and loads libswipl at *import* time,
so the environment has to be set up beforehand.

If the bundle carries no SWI-Prolog (an unbundled build, or a platform where
collection failed), nothing is set and pyswip falls back to its own search of
the machine's installation.
"""

import contextlib
import os
import sys


def _setup_bundled_swipl() -> None:
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle is None:
        return  # Running from source, not frozen.

    home = os.path.join(bundle, "swipl")
    if not os.path.isdir(home):
        return  # Nothing was bundled; let pyswip search the system.

    library_name = {
        "win32": "libswipl.dll",
        "darwin": "libswipl.dylib",
    }.get(sys.platform, "libswipl.so")
    library = os.path.join(bundle, library_name)

    if not os.path.exists(library):
        # The name is versioned on some platforms (libswipl.so.9, ...).
        matches = [
            name
            for name in os.listdir(bundle)
            if name.startswith("libswipl.so") or name.startswith("libswipl.")
        ]
        if not matches:
            return
        library = os.path.join(bundle, sorted(matches)[0])

    # pyswip returns these two straight away when both are set, skipping its
    # platform guesswork entirely.
    os.environ.setdefault("SWI_HOME_DIR", home)
    os.environ.setdefault("LIBSWIPL_PATH", library)

    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        # libswipl.dll pulls in libgcc/libgmp/zlib from the same directory.
        with contextlib.suppress(OSError):
            os.add_dll_directory(bundle)


_setup_bundled_swipl()

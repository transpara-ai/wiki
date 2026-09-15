"""Publish complete generated directories; keep runtime writers on the same lock."""
from contextlib import contextmanager
import ctypes
import errno
import fcntl
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import warnings


@contextmanager
def publication_lock(output):
    output = Path(output).absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    with (output.parent / (output.name + "-publish.lock")).open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def exchange_directories(first, second):
    """One namespace operation, including when both directories are nonempty."""
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                           ctypes.c_char_p, ctypes.c_uint]
        args = (-100, os.fsencode(first), -100, os.fsencode(second), 2)
    elif sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        args = (os.fsencode(first), os.fsencode(second), 2)
    else:
        raise OSError(errno.ENOTSUP, "Atomic directory exchange is unavailable; live site unchanged")
    rename.restype = ctypes.c_int
    if rename(*args) != 0:
        code = ctypes.get_errno()
        raise OSError(code, "Atomic site publication failed: " + os.strerror(code))


@contextmanager
def staged_publication(output, preserve=()):
    """Render privately, then publish everything at once or retain the old site."""
    output = Path(output).absolute()
    with publication_lock(output):
        if output.is_symlink() or (output.exists() and not output.is_dir()):
            raise ValueError("Publication output must be a real directory")
        stage = Path(tempfile.mkdtemp(prefix=output.name + "-build-", dir=output.parent))
        try:
            yield stage
            for name in preserve:
                if Path(name).name != name:
                    raise ValueError("Preserved status files must be direct children")
                previous = output / name
                if previous.is_file():
                    shutil.copy2(previous, stage / name)
            stage.chmod(stat.S_IMODE(output.stat().st_mode) if output.exists() else 0o755)
            if output.exists():
                exchange_directories(stage, output)
            else:
                os.replace(stage, output)
        finally:
            # After an exchange this is the previous complete site. Already-open
            # reader file descriptors remain valid when their names are removed.
            if stage.exists():
                try:
                    shutil.rmtree(stage)
                except OSError as exc:
                    warnings.warn("Unable to remove publication staging directory: %s" % exc)


def write_runtime_status(path, text):
    """Do not lose an activity/deploy update during a directory publication."""
    path = Path(path)
    with publication_lock(path.parent):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w") as handle:
                os.fchmod(handle.fileno(), stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644)
                handle.write(text)
            os.replace(name, path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

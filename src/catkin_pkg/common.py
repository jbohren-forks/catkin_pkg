
from __future__ import print_function

import os
import sys
import subprocess
from StringIO import StringIO


def run_command_colorized(cmd, cwd, quiet=False, add_env=None):
    run_command(cmd, cwd, quiet=quiet, colorize=True, add_env=add_env)


def run_command(cmd, cwd, quiet=False, colorize=False, add_env=None):
    capture = (quiet or colorize)
    stdout_pipe = subprocess.PIPE if capture else None
    stderr_pipe = subprocess.STDOUT if capture else None
    env = None
    if add_env:
        env = copy.copy(os.environ)
        env.update(add_env)
    try:
        proc = subprocess.Popen(
            cmd, cwd=cwd, shell=False,
            stdout=stdout_pipe, stderr=stderr_pipe,
            env=env
        )
    except OSError as e:
        raise OSError("Failed command '%s': %s" % (cmd, e))
    out = StringIO() if quiet else sys.stdout
    if capture:
        while True:
            line = proc.stdout.readline()
            try:
                # try decoding in case the output is encoded
                line = line.decode('utf8', 'replace')
            except (AttributeError, UnicodeEncodeError):
                # do nothing for Python 3 when line is already a str
                # or when the string can't be decoded
                pass

            # ensure that it is convertable to the target encoding
            encoding = 'utf8'
            try:
                if out.encoding:
                    encoding = out.encoding
            except AttributeError:
                # do nothing for Python 2
                pass
            line = line.encode(encoding, 'replace')
            line = line.decode(encoding, 'replace')

            if proc.returncode is not None or not line:
                break
            try:
                line = colorize_line(line) if colorize else line
            except Exception as e:
                import traceback
                traceback.print_exc()
                print('<caktin_make> color formatting problem: ' + str(e),
                      file=sys.stderr)
            out.write(line)
    proc.wait()
    if proc.returncode:
        if quiet:
            print(out.getvalue())
        raise subprocess.CalledProcessError(proc.returncode, ' '.join(cmd))
    return out.getvalue() if quiet else ''

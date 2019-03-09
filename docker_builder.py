#!/usr/bin/env python3

import os
import time
import subprocess
import tempfile

import Programmierspiel.settings as settings
from django import setup as django_setup
from django.conf import settings as django_settings

"""
Requirements:
  ODBC Driver: https://www.microsoft.com/en-ca/download/details.aspx?id=36434
  Django Engine: https://pypi.org/project/django-pyodbc-azure/
"""

django_settings.configure(
    **settings.__dict__)
django_setup()

import core.models as m

BUILD_CWD="../gameserver/docker4bots/"
BUILD_SCRIPT="./1_build_spn_cpp_bot.sh"

while True:
    versions2build = m.SnakeVersion.objects.filter(compile_state='not_compiled')

    for s in versions2build:
        codefile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        codefile.write(s.code)
        codefilename = codefile.name
        codefile.close()

        print(f"Code written to {codefilename}")

        cmd = [BUILD_SCRIPT, str(s.id), codefilename]
        print(f"Running: {cmd}")
        proc = subprocess.run(cmd, cwd=BUILD_CWD, capture_output=True)
        print(f"subprocess completed: {proc.returncode}")

        buildlog  = "--------- STDOUT ---------\n"
        buildlog += proc.stdout.decode('utf-8') + "\n\n"
        buildlog += "--------- STDERR ---------\n"
        buildlog += proc.stderr.decode('utf-8') + "\n"

        s.build_log = buildlog

        if proc.returncode == 0:
            s.compile_state = 'successful'
        else:
            s.compile_state = 'failed'

        s.save()

        os.unlink(codefilename)
        print(f"{codefilename} deleted.")

    time.sleep(10)

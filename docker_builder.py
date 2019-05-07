#!/usr/bin/env python3

import re
import os
import time
import subprocess
import tempfile
import datetime

import Programmierspiel.settings as settings
from django import setup as django_setup
from django.conf import settings as django_settings

"""
Requirements:
  ODBC Driver: https://www.microsoft.com/en-ca/download/details.aspx?id=36434
  Django Engine: https://pypi.org/project/django-pyodbc-azure/
"""

def now():
    return datetime.datetime.utcnow().isoformat()

django_settings.configure(
    **settings.__dict__)
django_setup()

import core.models as m

BUILD_CWD="../gameserver/docker4bots/"
BUILD_SCRIPT="./1_build_spn_cpp_bot.sh"

cleanup_re = re.compile(r"([^a-z0-9+_-]+)", re.IGNORECASE)

while True:
    versions2build = m.SnakeVersion.objects.filter(compile_state='not_compiled')

    if not versions2build:
        print("Nothing to do, sleeping for some time...")
        time.sleep(10)
        continue

    for s in versions2build:
        codefile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        codefile.write(s.code)
        codefilename = codefile.name
        codefile.close()

        clean_name = cleanup_re.sub("_", s.user.username)

        print(f"{now()}: Code written to {codefilename}")

        cmd = [BUILD_SCRIPT, str(s.id), clean_name, codefilename]
        print(f"{now()}: Running: {cmd}")
        proc = subprocess.run(cmd, cwd=BUILD_CWD, capture_output=True)
        print(f"{now()}: subprocess completed: {proc.returncode}")

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
        print(f"{now()}: {codefilename} deleted.")

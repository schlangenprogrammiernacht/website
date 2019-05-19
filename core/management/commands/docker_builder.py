import re
import os
import time
import subprocess
import tempfile
import datetime
from django.core.management.base import BaseCommand
from core.models import SnakeVersion

def now():
    return datetime.datetime.utcnow().isoformat()

class Command(BaseCommand):
    help = "compile snake versions"

    def handle(self, *args, **options):
        BUILD_CWD="../gameserver/docker4bots/"
        BUILD_SCRIPT="./1_build_spn_cpp_bot.sh"

        cleanup_re = re.compile(r"([^a-z0-9+_-]+)", re.IGNORECASE)

        while True:
            versions2build = SnakeVersion.objects.filter(compile_state='not_compiled')

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

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

    def __init__(self):
        self.cleanup_re = re.compile(r"([^a-z0-9+_-]+)", re.IGNORECASE)

    def handle(self, *args, **options):
        while True:
            versions2build = SnakeVersion.objects.filter(compile_state='not_compiled')

            if versions2build:
                for s in versions2build:
                    self.build_version(s)
            else:
                print("Nothing to do, taking a nap...")
                time.sleep(5)

    def build_version(self, snake_version):
        return_code, stdout, stderr = self.run_build_script(snake_version)
        snake_version.build_log = self.format_build_log(stdout, stderr)
        snake_version.compile_state = 'successful' if return_code == 0 else 'failed'
        snake_version.save()

    def run_build_script(self, snake_version):
        BUILD_CWD = "../gameserver/docker4bots/"
        BUILD_SCRIPT = "./1_build_spn_cpp_bot.sh"

        code_file = self.write_code_to_temp_file(snake_version)
        print(f"{now()}: Code written to {code_file}")

        try:
            clean_name = self.cleanup_username(snake_version.user.username)
            cmd = [BUILD_SCRIPT, str(snake_version.id), clean_name, code_file]
            print(f"{now()}: Running: {cmd}")
            sp = subprocess.run(cmd, cwd=BUILD_CWD, capture_output=True)
            print(f"{now()}: subprocess completed: {sp.returncode}")

            return sp.returncode, sp.stdout.decode('utf-8'), sp.stderr.decode('utf-8')
        finally:
            os.unlink(code_file)
            print(f"{now()}: {code_file} deleted.")

    @staticmethod
    def write_code_to_temp_file(snake_version):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(snake_version.code)
            return f.name

    def cleanup_username(self, username):
        return self.cleanup_re.sub("_", username)

    @staticmethod
    def format_build_log(stdout, stderr):
        return  "--------- STDOUT ---------\n{0}\n\n--------- STDERR ---------\n{1}\n".format(stdout, stderr)


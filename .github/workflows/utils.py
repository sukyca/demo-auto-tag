import os
import subprocess
import json

command = subprocess.run('gh run list --json databaseId --repo sukyca/snowflake-test-repo', stdout=subprocess.PIPE)

# print(json.loads(command.stdout.decode()))

print(command.returncode)
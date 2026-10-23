import os

import platform


VERSION = 'v1.0.26.7'
PUBLISH_DATE = '2026060731'
password = os.environ.get("GITS_CONFIG_PASSWORD", "public-demo-only")



system = platform.system().lower()
if system == 'darwin':
    OS = 'macos'
else:
    OS = system
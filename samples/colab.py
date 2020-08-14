import os
import json
from datetime import datetime

os.system('pip install --upgrade pip')
os.system('pip install palladium-python')

os.system('apt-get update')
os.system('apt install chromium-chromedriver')

config = {
    'chromedriver': '/usr/lib/chromium-browser/chromedriver',
    'chromebinary': '/usr/lib/chromium-browser/chromium-browser',
    'modified_time': datetime.now().isoformat(),
}

with open('/usr/local/lib/python3.6/dist-packages/palladium/config.json', 'w') as fp:
  json.dump(config, fp)

import os

# You should change WORKING_DIR to your workspace directory path
WORKING_DIR = 'examples'
# Default using the WORKING_DIR/base.html as the base template file
# You may want to specify yourself base template file
BASE_FILE = os.path.join(os.path.dirname(__file__), WORKING_DIR, 'base.html')
# Genereted file suffix name
SUFFIX_NAME = '.gen.html'
# Server hostname
HOSTNAME = 'localhost'
# Server Listen on port
PORT = 5000

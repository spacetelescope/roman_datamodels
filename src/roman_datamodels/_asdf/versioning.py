import os

import rad

# use dev settings only if RAD is dev or RAD_DEV environment variable
# is set to 1 TODO make other "truthy" things work
USE_DEV = bool(int(os.environ.get("RAD_DEV", "dev" in rad.__version__)))

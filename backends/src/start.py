import env
import ray
from api import start_api

# Enable Distributed Compute
# TODO: only works locally, need to setup 'head' and pass address/port
ray.init()

if __name__ == "__main__":
  start_api()

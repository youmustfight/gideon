import env
import ray
from api import start_api
from worker import start_worker

# Enable Distributed Compute
# TODO: only works locally, need to setup 'head' and pass address/port
ray.init()

if __name__ == "__main__":
  # Run a Service
  if (env.env_target_service() == 'api'):
    start_api()
  elif (env.env_target_service() == 'worker'):
    start_worker()

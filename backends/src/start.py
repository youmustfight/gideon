import env
import torch
from api import start_api
from worker import start_worker

# INIT
# Restrict PyTorch Processor Usage: https://github.com/pytorch/pytorch/issues/36191#issuecomment-620956849
torch.set_num_threads(1)

if __name__ == "__main__":
  # V2 (better than multi-process bc eats extra cpu + background processes don't cause container to exit)
  if (env.env_target_service() == 'api'):
    start_api()
  if (env.env_target_service() == 'worker'):
    start_worker()

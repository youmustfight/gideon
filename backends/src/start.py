from multiprocessing import Process
import torch
import env
import logger
from api import start_api
from worker import start_worker

# INIT
# Restrict PyTorch Processor Usage (blocks other processors):
# https://github.com/UKPLab/sentence-transformers/issues/1318
# https://github.com/pytorch/pytorch/issues/36191#issuecomment-620956849
torch.set_num_threads(1)

if __name__ == "__main__":
    # # V2 SERVICES (better than multi-process bc eats extra cpu + background processes don't cause container to exit)
    # if (env.env_target_service() == 'api'):
    #   start_api()
    # if (env.env_target_service() == 'worker'):
    #   start_worker()

    # # v3 POOLS for PARALLEL PROCESSES (doesn't work. port isn't being exposed for some reason?)
    # def exec_iter(func):
    #     func()
    # with Pool() as pool:
    #     pool.starmap_async(exec_iter, [
    #         start_worker,
    #         start_api,
    #     ])

    # v4 PROCESSES (start api + worker, only wait for worker to resolve, that way if it errors, i think the whole container stops?)
    p1 = Process(target=start_api)
    p2 = Process(target=start_worker)
    p1.start()
    p2.start()
    # --- block till return (if worker returns re-start. load balancer health check will check api)
    p2.join()

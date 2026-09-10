import multiprocessing
import asyncio
from random import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import os

def cpu_bound_task(n):
    return sum(i * i for i in range(n))

async def fetch_data(name, delay):
    await asyncio.sleep(delay)
    return f"{name} fetched data after {delay} seconds"

async def fetching_data():
    tasks = [
        fetch_data("Tasks", 1),
        fetch_data("Product", 1),
        fetch_data("User", 1)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        print(result)

async def slow_analytics():
    try:
        print("[Slow Analytics] Starting slow analytics...")
        await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("[Slow Analytics] Slow analytics was cancelled.")
        raise
    finally:
        print("[Slow Analytics] Cleaning up resources...")

async def main():
    try:
        await asyncio.wait_for(slow_analytics(), timeout=3)
    except asyncio.TimeoutError:
        print("[Main] Timeout occurred.")

async def offloading():
    loop = asyncio.get_running_loop()

    result_io = await asyncio.to_thread(time.sleep, 1)
    with ProcessPoolExecutor() as executor:
        result_cpu = await loop.run_in_executor(executor, cpu_bound_task, 10**6)
    print(f"CPU-bound offloading result: {result_cpu}")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    start_time = time.time()
    numbers = [10**7] * 4
    with multiprocessing.Pool() as pool:
        results = pool.map(cpu_bound_task, numbers, chunksize=1)
    end_time = time.time()
    print(f"Results: {results}")
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")

    counter = 0
    lock = threading.Lock()
    def increment():
        global counter
        for _ in range(2000):
            with lock:
                counter += 1

    threads = [threading.Thread(target=increment) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"Final counter value: {counter}")
    print("\n")

    Executor = ProcessPoolExecutor

    with Executor(max_workers=4) as executor:
        futures = [executor.submit(cpu_bound_task, 10**7) for _ in range(4)]
        for future in as_completed(futures):
            print(f"Result: {future.result()}")


    asyncio.run(fetching_data())
    asyncio.run(main())
    asyncio.run(offloading())


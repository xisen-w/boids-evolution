"""Six pure table services plus ordered, lazy dispatch and fault-isolated batches."""
from published.a07_r05 import (
    process as process, process_many as process_many, process_iter as process_iter,
    clean_adapter, revenue_adapter, group_adapter, monthly_adapter,
    lookup_adapter, window_adapter,
)


def process_results(jobs):
    """Process ordered 4-tuples, retaining failures instead of aborting.

    Returns one ``(success, value)`` pair per job. On success value is the
    service output; on failure it is the caught Exception instance. Each job
    is evaluated exactly once and later jobs continue after a failure.
    """
    results = []
    for job in jobs:
        try:
            results.append((True, process(*job)))
        except Exception as exc:
            results.append((False, exc))
    return results

__all__ = ['process', 'process_many', 'process_iter', 'process_results',
           'clean_adapter', 'revenue_adapter', 'group_adapter',
           'monthly_adapter', 'lookup_adapter', 'window_adapter']

from enum import Enum


class AllSitesFilter(Enum):
    """
    Supported arguments for all_sites endpoint
    """
    all = "all"
    visited = "visited"
    unvisited = "unvisited"

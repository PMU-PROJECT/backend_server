from enum import Enum


class AllSitesTypes(Enum):
    """
    Supported arguments for all_sites endpoint
    """
    all = "all"
    visited = "visited"
    unvisited = "unvisited"

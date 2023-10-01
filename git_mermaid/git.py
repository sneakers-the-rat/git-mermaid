"""
Create mermaid objects from a git repo
"""
from typing import Union, List
from pathlib import Path
import git

from git_mermaid.mermaid import (
    Node,
    Commit,
    Branch,
    Merge,
    Checkout,
    Graph
)

def nodes_from_repo(path:Union[Path, str]) -> List[Node]:
    path = Path(path)
    repo = git.Repo(str(path))

    commits = list(repo.iter_commits())

    branches = {}
    for head in repo.heads:
        branches[str(head)] = list()





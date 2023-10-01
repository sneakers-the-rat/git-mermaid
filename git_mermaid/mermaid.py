"""
Models for generating gitGraphs

See https://mermaid.js.org/syntax/gitgraph.html
for documentation of the format
"""
from typing import Optional, Literal, ClassVar, Generic, TypeVar, Dict,List
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

import git

DISPLAY_TYPE = Literal['NORMAL', 'REVERSE', 'HIGHLIGHT']
@dataclass
class Node(ABC):
    """Metaclass for each entry in the gitGraph"""
    @abstractmethod
    def __str__(self) -> str:
        """All nodes should provide a string"""

    @classmethod
    def from_git(cls, src) -> 'Node':
        """Instantiate from the relevant git type"""
        raise NotImplementedError('Needs to be implemented on subclass')
@dataclass
class Commit(Node):
    id: Optional[str] = None
    type: DISPLAY_TYPE = 'NORMAL'
    tag: Optional[str] = None

    @classmethod
    def from_git(cls, src: git.Commit) -> 'Commit':
        tag = src.repo.git.tag('--points-at', src.hexsha)
        if tag == '':
            tag = None

        return Commit(
            id = src.hexsha[0:7],
            tag = tag
        )

    def __str__(self) -> str:
        res = 'commit'
        for key, val in asdict(self).items():
            if val is not None:
                if key == "type":
                    res += f' {key}:{val}'
                else:
                    res += f" {key}:\"{val}\""
        return res


@dataclass
class Branch(Node):
    name: str
    order: Optional[int] = None

    @classmethod
    def from_git(cls, src: git.Head) -> 'Branch':
        return Branch(
            name= str(src)
        )

    def __str__(self) -> str:
        res = f"branch {self.name}"
        if self.order is not None:
            res += f" order: {self.order}"
        return res

@dataclass
class Checkout(Node):
    name: str

    def __str__(self) -> str:
        return f"checkout {self.name}"



@dataclass
class Merge(Node):
    branch: str
    """branch name to merge"""
    id: Optional[str] = None
    tag: Optional[str] = None
    type: DISPLAY_TYPE = 'NORMAL'
    def __str__(self) -> str:
        res =  f"checkout {self.branch}"
        for key, val in asdict(self).items():
            if val is not None:
                if key == "type":
                    res += f' {key}:{val}'
                else:
                    res += f" {key}:\"{val}\""
        return res


@dataclass
class CherryPick(Node):
    id: str

    def __init__(self, **kwargs):
        raise NotImplementedError('No cherypicking support yet!')


# --------------------------------------------------
# Graph
# --------------------------------------------------
@dataclass
class ThemeVariables:
    branch_color: Optional[Dict[str,str]] = None
    """
    custom colors for each branch::
    
        {
          'git0': '#ff0000',
          'git1': '#0000ff',
          ...
        }
    """
    branch_label_color: Optional[Dict[str,str]] = None
    """
    custom colors for branch labels:
    
        {
          'gitBranchLabel0': '#ff0000',
          'gitBranchLabel1': '#00ff00',
          ...
        }
    """
    commit_label_color: Optional[str] = None
    """Hex color for commit label text"""
    commit_background_color: Optional[str] = None
    """Hex color for commit background"""
    commit_label_font_size: Optional[int] = None
    """in pixels"""


    tag_label_color: Optional[str] = None
    """Hex color for tag label text"""
    tag_background_color: Optional[str] = None
    """Hex color for tag label background"""
    tag_border_color: Optional[str] = None
    """Hex color for tag border color"""
    tag_label_font_size: Optional[int] = None
    """in pixels"""


    def dict(self) -> dict:
        res = {}
        if self.branch_color is not None:
            res.update(self.branch_color)
        if self.branch_label_color is not None:
            res.update(self.branch_label_color)
        if self.commit_label_color is not None:
            res.update({'commitLabelColor': self.commit_label_color})
        if self.commit_background_color is not None:
            res.update({'commitLabelBackground': self.commit_background_color})
        if self.commit_label_font_size is not None:
            res.update({'commitLabelFontSize': f"{self.commit_label_font_size}px"})
        if self.tag_label_font_size is not None:
            res.update({'tagLabelFontSize': f"{self.tag_label_font_size}px"})
        if self.tag_label_color is not None:
            res.update({'tagLabelColor': self.tag_label_color})
        if self.tag_background_color is not None:
            res.update({'tagLabelBackground': self.tag_background_color})
        if self.tag_border_color is not None:
            res.update({'tagLabelBorder': self.tag_border_color})

        return res

@dataclass
class Graph:
    nodes: List[Node]
    showBranches: bool = True
    """If set to false, the branches are not shown in the diagram."""
    showCommitLabel: bool = True
    """If set to false, the commit labels are not shown in the diagram."""
    mainBranchName: str = 'main'
    """Name of the default root/branch"""
    mainBranchOrder: int = 0
    """Position of the main branch in the list of branches"""
    rotateCommitLabel:  bool = True
    """
    Mermaid supports two types of commit labels layout. The default layout is rotated, 
    which means the labels are placed below the commit circle, rotated at 45 degrees 
    for better readability. This is particularly useful for commits with long labels.

    The other option is horizontal, which means the labels are placed below the commit 
    circle centred horizontally, and are not rotated. This is particularly useful for 
    commits with short labels.

    You can change the layout of the commit labels by using the rotateCommitLabel 
    keyword in the directive. It defaults to true, which means the commit labels are 
    rotated.
    """
    orientation: Literal['LR', 'TB'] = 'LR'
    """
    Sometimes we may want to change the orientation. Currently, Mermaid supports 
    two orientations: Left to Right(default) and Top to Bottom.

    In order to change the orientation from top to bottom i.e. branches lined 
    horizontally, you need to add TB along with gitGraph.
    """
    theme: Literal['base', 'forest', 'dark', 'default', 'neutral'] = 'base'
    themeVariables: Optional[ThemeVariables] = None



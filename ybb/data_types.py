from dataclasses import dataclass, field
from dataclasses_json import LetterCase, dataclass_json, Undefined
from typing import List, Optional

@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.KEBAB)
@dataclass(frozen=True)
class Frame:
    x: float
    y: float
    w: float
    h: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def center_x(self) -> float:
        return self.x + self.w / 2

    @property
    def center_y(self) -> float:
        return self.y + self.h / 2



@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.KEBAB)
@dataclass
class Window:
    id: int
    pid: int
    app: str
    title: str
    scratchpad: str
    frame: Frame
    role: str
    subrole: str
    root_window: bool
    display: int
    space: int
    level: int
    sub_level: int
    layer: str
    sub_layer: str
    opacity: float
    split_type: Optional[str]
    split_child: Optional[str]
    stack_index: Optional[int]
    can_move: bool
    can_resize: bool
    has_focus: bool
    has_shadow: bool
    has_parent_zoom: bool
    has_fullscreen_zoom: bool
    has_ax_reference: bool
    is_native_fullscreen: bool
    is_visible: bool
    is_minimized: bool
    is_hidden: bool
    is_floating: bool
    is_sticky: bool
    is_grabbed: bool

@dataclass_json(undefined=Undefined.EXCLUDE, letter_case=LetterCase.KEBAB)
@dataclass
class Space:
    id: int
    uuid: str
    index: int
    label: str
    type: str
    display: int
    windows: List[int]
    first_window: int
    last_window: int
    has_focus: bool
    is_visible: bool
    is_native_fullscreen: bool

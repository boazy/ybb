from dataclasses import dataclass
from dataclasses_json import LetterCase, DataClassJsonMixin, Undefined
from typing import List, Optional
from enum import Enum

class SplitType(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    def opposite(self) -> 'SplitType':
        match self:
            case SplitType.VERTICAL:
                return SplitType.HORIZONTAL
            case SplitType.HORIZONTAL:
                return SplitType.VERTICAL

    def start_direction(self) -> 'CardinalDirection':
        match self:
            case SplitType.VERTICAL:
                return CardinalDirection.NORTH
            case SplitType.HORIZONTAL:
                return CardinalDirection.WEST
    
    def end_direction(self) -> 'CardinalDirection':
        match self:
            case SplitType.VERTICAL:
                return CardinalDirection.SOUTH
            case SplitType.HORIZONTAL:
                return CardinalDirection.EAST

class CardinalDirection(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    def opposite(self) -> 'CardinalDirection':
        match self:
            case CardinalDirection.NORTH:
                return CardinalDirection.SOUTH
            case CardinalDirection.SOUTH:
                return CardinalDirection.NORTH
            case CardinalDirection.EAST:
                return CardinalDirection.WEST
            case CardinalDirection.WEST:
                return CardinalDirection.EAST

class AdditionInsertDirections(Enum):
    STACK = "stack"

InsertDirection = CardinalDirection | AdditionInsertDirections

@dataclass(frozen=True)
class Frame(DataClassJsonMixin):
    dataclass_json_config = {
        "undefined": Undefined.EXCLUDE,
        "letter_case": LetterCase.KEBAB
    }
    
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



@dataclass
class Window(DataClassJsonMixin):
    dataclass_json_config = {
        "undefined": Undefined.EXCLUDE,
        "letter_case": LetterCase.KEBAB
    }
    
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

@dataclass
class Space(DataClassJsonMixin):
    dataclass_json_config = {
        "undefined": Undefined.EXCLUDE,
        "letter_case": LetterCase.KEBAB
    }
    
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

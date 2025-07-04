from ybb.tree import Window, Stack, Split, SplitType, Frame

def test_find_window_in_window():
    frame = Frame(x=0, y=0, w=100, h=100)
    window = Window(id=1, app="test", title="test", frame=frame)
    result = window.find_window(1)
    assert result.window == window
    assert result.ancestors == []
    assert result.is_first_child is False

def test_find_window_in_stack():
    frame = Frame(x=0, y=0, w=100, h=100)
    window1 = Window(id=1, app="test1", title="test1", frame=frame)
    window2 = Window(id=2, app="test2", title="test2", frame=frame)
    stack = Stack(windows=[window1, window2], frame=frame)
    result = stack.find_window(2)
    assert result.window == window2
    assert result.ancestors == []
    assert result.is_first_child is False

def test_find_window_in_split():
    frame = Frame(x=0, y=0, w=100, h=100)
    window1 = Window(id=1, app="test1", title="test1", frame=frame)
    window2 = Window(id=2, app="test2", title="test2", frame=frame)
    split = Split(first_child=window1, second_child=window2, split_type=SplitType.VERTICAL, frame=frame)
    
    result = split.find_window(1)
    assert result.window == window1
    assert len(result.ancestors) == 1
    assert result.ancestors[0] == split
    assert result.is_first_child is True

    result = split.find_window(2)
    assert result.window == window2
    assert len(result.ancestors) == 1
    assert result.ancestors[0] == split
    assert result.is_first_child is False

def test_find_window_nested_split():
    frame = Frame(x=0, y=0, w=100, h=100)
    window1 = Window(id=1, app="test1", title="test1", frame=frame)
    window2 = Window(id=2, app="test2", title="test2", frame=frame)
    window3 = Window(id=3, app="test3", title="test3", frame=frame)
    
    inner_split = Split(first_child=window2, second_child=window3, split_type=SplitType.HORIZONTAL, frame=frame)
    outer_split = Split(first_child=window1, second_child=inner_split, split_type=SplitType.VERTICAL, frame=frame)

    result = outer_split.find_window(3)
    assert result.window == window3
    assert len(result.ancestors) == 2
    assert result.ancestors[0] == outer_split
    assert result.ancestors[1] == inner_split
    assert result.is_first_child is False

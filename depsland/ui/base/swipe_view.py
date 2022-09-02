import flet
from typing import Iterable


class SwipeView(flet.Row):
    current_index = 0
    
    def __init__(self, *args, **kwargs):
        from flet.transform import Offset
        super().__init__(
            *args, **kwargs,
            animate_position=200,
            offset=Offset(x=0, y=0),
            animate_offset=500,
        )
    
    def append(self, control: flet.Control) -> int:
        idx = len(self.controls)
        control.width = self.width
        control.height = self.height
        self.controls.append(control)
        return idx
    
    def extend(self, controls: Iterable[flet.Control]) -> None:
        for control in controls:
            self.append(control)
    
    @property
    def current_view(self) -> flet.Container:
        return self.controls[self.current_index]
    
    def switch_to(self, idx: int) -> None:
        if idx != self.current_index:
            distance: int = abs(idx - self.current_index) * self.width
            forward: bool = idx > self.current_index
            if forward:
                self.offset.x -= distance
            else:
                self.offset.x += distance
            print(self.width, self.height, idx, self.offset)
            self.current_index = idx
            # TODO: notify views to animate their scale to perform fade-in and
            #   out.
    
    def switch_prev(self) -> None:
        pass
    
    def switch_next(self) -> None:
        pass

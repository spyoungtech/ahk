from behave.matchers import RegexMatcher
from ahk import AHK
from behave_classy import step_impl_base

Base = step_impl_base()


class AHKSteps(AHK, Base):
    @Base.given(u'the mouse position is ({xpos:d}, {ypos:d})')
    def given_mouse_move(self, xpos, ypos):
        self.mouse_move(x=xpos, y=ypos)

    @Base.when(u'I move the mouse (UP|DOWN|LEFT|RIGHT) (\d+)px', matcher=RegexMatcher)
    def move_direction(self, direction, px):
        px = int(px)
        if direction in ('UP', 'DOWN'):
            axis = 'y'
        else:
            axis = 'x'
        if direction in ('LEFT', 'UP'):
            px = px * -1
        kwargs = {axis: px, 'relative': True}
        self.mouse_move(**kwargs)

    @Base.then(u'I expect the mouse position to be ({xpos:d}, {ypos:d})')
    def check_position(self, xpos, ypos):
        x, y = self.mouse_position
        assert x == xpos
        assert y == ypos


AHKSteps().register()

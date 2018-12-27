import ast

from ahk.script import ScriptEngine


class ScreenMixin(ScriptEngine):
    def image_search(self, image_path, upper_bound=(0, 0), lower_bound=None,
                     coord_mode='Screen', scale_height=None, scale_width=None):
        x1, y1 = upper_bound
        if lower_bound:
            x2, y2 = lower_bound
        else:
            x2, y2 = ('%A_ScreenWidth%', '%A_ScreenHeight%')
        script = self.render_template('screen/image_search.ahk',
                                      x1=x1, x2=x2, y1=y1, y2=y2,
                                      coord_mode=coord_mode,
                                      image_path=image_path)
        resp = self.run_script(script)
        try:
            return ast.literal_eval(resp)
        except SyntaxError:
            return None

    def pixel_get_color(self, x, y, coord_mode='Screen', alt=False, slow=False, rgb=True):
        options = []
        if slow:
            options.append('Slow')
        elif alt:
            options.append('Alt')
        if rgb:
            options.append('RGB')
        script = self.render_template('screen/pixel_get_color.ahk',
                                      x=x, y=y,
                                      coord_mode=coord_mode,
                                      options=options)
        resp = self.run_script(script)
        return resp

    def pixel_search(self, color, variation=0, upper_bound=(0, 0), lower_bound=None, coord_mode='Screen', fast=False, rgb=True):
        options = []
        if fast:
            options.append('Fast')
        if rgb:
            options.append('RGB')
        x1, y1 = upper_bound
        if lower_bound:
            x2, y2 = lower_bound
        else:
            x2, y2 = ('%A_ScreenWidth%', '%A_ScreenHeight%')

        script = self.render_template('screen/pixel_search.ahk',
                                      x1=x1, y1=y1, x2=x2, y2=y2,
                                      coord_mode=coord_mode,
                                      color=color,
                                      variation=variation,
                                      options=options)
        resp = self.run_script(script)
        try:
            return ast.literal_eval(resp)
        except SyntaxError:
            return None

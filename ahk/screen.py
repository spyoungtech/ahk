import ast
from ahk.script import ScriptEngine, AsyncScriptEngine
from typing import Tuple, Union, Optional


class ScreenMixin(ScriptEngine):
    def _image_search(
        self,
        image_path: str,
        upper_bound: Tuple[int, int] = (0, 0),
        lower_bound: Tuple[int, int] = None,
        color_variation: int = None,
        coord_mode: str = 'Screen',
        scale_height: int = None,
        scale_width: int = None,
        transparent: str = None,
        icon: int = None,
    ) -> str:

        if scale_height and not scale_width:
            scale_width = -1
        elif scale_width and not scale_height:
            scale_height = -1

        options = []
        if icon:
            options.append(f'Icon{icon}')
        if color_variation:
            options.append(color_variation)
        if transparent:
            options.append(f'Trans{transparent}')
        if scale_width:
            options.append(f'w{scale_width}')
            options.append(f'h{scale_height}')

        x1, y1 = upper_bound
        if lower_bound:
            x2, y2 = lower_bound
        else:
            x2, y2 = ('A_ScreenWidth', 'A_ScreenHeight')
        script = self.render_template(
            'screen/image_search.ahk',
            x1=x1,
            x2=x2,
            y1=y1,
            y2=y2,
            coord_mode=coord_mode,
            image_path=image_path,
            options=options,
        )
        return script

    def image_search(
        self,
        image_path: str,
        upper_bound: Tuple[int, int] = (0, 0),
        lower_bound: Tuple[int, int] = None,
        color_variation: int = None,
        coord_mode: str = 'Screen',
        scale_height: int = None,
        scale_width: int = None,
        transparent: str = None,
        icon: int = None,
    ) -> Union[Tuple[int, int], None]:
        """
        `AutoHotkey ImageSearch reference`_

        .. _AutoHotkey ImageSearch reference: https://autohotkey.com/docs/commands/ImageSearch.htm


        :param image_path: path to the image file e.g. C:\location\of\cats.png
        :param upper_bound: a two-tuple of X,Y coordinates for the upper-left corner of the search area e.g. (200, 400)
            defaults to (0,0)

        :param lower_bound: like ``upper_bound`` but for the lower-righthand corner of the search area e.g. (400, 800)
            defaults to screen width and height (lower right-hand corner; ``%A_ScreenWidth%``, ``%A_ScreenHeight%``).

        :param color_variation: Shades of variation (up or down) for the intensity of RGB for each pixel. Equivalent of
            ``*n`` option. Defaults to 0.

        :param coord_mode: the Pixel CoordMode to use. Default is 'Screen'
        :param scale_height: Scale height in pixels. Equivalent of ``*hn`` option
        :param scale_width: Scale width in pixels. Equivalent of ``*wn`` option
        :param transparent: Specific color in the image that will be ignored during the search. Pixels with the exact
            color given will match any color. Can be used with color names e.g. (Black, Purple, Yellow) found
            at https://https://www.autohotkey.com/docs/commands/Progress.htm#colors or hexadecimal values e.g.
            (0xFFFFAA, 05FA15, 632511). Equivalent of ``*TransN`` option

        :param icon: Number of the icon group to use. Equivalent of ``*Icon`` option

        :return: coordinates of the upper-left pixel of where the image was found on the screen; ``None`` if the image
            was not found

        :rtype: Union[Tuple[int, int], None]

        Note: when only scale_height or only scale_width are provided, aspect ratio is maintained by default.
        """
        script = self._image_search(
            image_path=image_path,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            color_variation=color_variation,
            coord_mode=coord_mode,
            scale_height=scale_height,
            scale_width=scale_width,
            transparent=transparent,
            icon=icon,
        )
        resp = self.run_script(script)
        try:
            return ast.literal_eval(resp)
        except SyntaxError:
            return None

    def _pixel_get_color(
        self, x: int, y: int, coord_mode: str = 'Screen', alt: bool = False, slow: bool = False, rgb=True
    ):
        options = []
        if slow:
            options.append('Slow')
        elif alt:
            options.append('Alt')
        if rgb:
            options.append('RGB')
        script = self.render_template('screen/pixel_get_color.ahk', x=x, y=y, coord_mode=coord_mode, options=options)
        return script

    def pixel_get_color(self, *args, **kwargs):
        """
        `AutoHotkey PixelGetColor reference`_

        .. _AutoHotkey PixelGetColor reference: https://autohotkey.com/docs/commands/PixelGetColor.htm

        :param x: x coordinate
        :param y: y coordinate
        :param coord_mode:
        :param alt:
        :param slow:
        :param rgb: returns
        :return: the color as an RGB hexidecimal string;
        """
        script = self._pixel_get_color(*args, **kwargs)
        return self.run_script(script)


    def _pixel_search(
        self,
        color: Union[str, int],
        variation: int = 0,
        upper_bound: Tuple[int, int] = (0, 0),
        lower_bound: Tuple[int, int] = None,
        coord_mode: str = 'Screen',
        fast: bool = True,
        rgb: bool = True,
    ) -> str:
        options = []
        if fast:
            options.append('Fast')
        if rgb:
            options.append('RGB')
        x1, y1 = upper_bound
        if lower_bound:
            x2, y2 = lower_bound
        else:
            x2, y2 = ('A_ScreenWidth', 'A_ScreenHeight')

        script = self.render_template(
            'screen/pixel_search.ahk',
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            coord_mode=coord_mode,
            color=color,
            variation=variation,
            options=options,
        )
        return script

    def pixel_search(self, *args, **kwargs):
        """
        `AutoHotkey PixelSearch reference`_

        .. _AutoHotkey PixelSearch reference: https://autohotkey.com/docs/commands/PixelSearch.htm

        :param color:
        :param variation:
        :param upper_bound:
        :param lower_bound:
        :param coord_mode:
        :param fast:
        :param rgb:
        :return: the coordinates of the pixel; None if the pixel is not found
        """
        script = self._pixel_search(*args, **kwargs)
        resp = self.run_script(script)
        try:
            return ast.literal_eval(resp)
        except SyntaxError:
            return None

class AsyncScreenMixin(AsyncScriptEngine, ScreenMixin):
    async def pixel_search(self, *args, **kwargs):
        script = self._pixel_search(*args, **kwargs)
        resp = await self.a_run_script(script)
        try:
            return ast.literal_eval(resp)
        except SyntaxError:
            return None

    async def image_search(self, *args, **kwargs):
        script = self._image_search(*args, **kwargs)
        resp = await self.a_run_script(script)
        try:
            return ast.literal_eval(resp)
        except SyntaxError:
            return None

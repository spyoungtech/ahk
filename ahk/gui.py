from ahk.script import ScriptEngine


class GUIMixin(ScriptEngine):
    def __init__(self, *args, **kwargs):
        self.window_encoding = kwargs.pop('window_encoding', None)
        super().__init__(*args, **kwargs)

    def show_tooltip(self, text: str, ms=1000, x="", y="", id=""):
        """Show ToolTip

        https://www.autohotkey.com/docs/commands/ToolTip.htm

        :param text: Tooltip text
        :type text: str
        :param ms: Wait time (ms), defaults to 1000
        :type ms: int, optional
        :param x: X coordinate relative to active window, defaults to ""
        :type x: str, optional
        :param y: Y coordinate relative to active window, defaults to ""
        :type y: str, optional
        :param id: ID of ToolTip for more ToolTip message, defaults to ""
        :type id: str, optional
        :raises ValueError: ID must be between [1, 20]
        """

        if id and not (1 <= int(id) <= 20):
            raise ValueError("ID value must be between [1, 20]")

        script = self.render_template("gui/tooltip.ahk", text=text, ms=ms, x=x, y=y, id=id)
        self.run_script(script)

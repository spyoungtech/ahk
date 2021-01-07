from ahk.script import ScriptEngine, AsyncScriptEngine


class GUIMixin(ScriptEngine):

    TRAYTIP_INFO = 1
    TRAYTIP_WARNING = 2
    TRAYTIP_ERROR = 3

    def __init__(self, *args, **kwargs):
        self.window_encoding = kwargs.pop('window_encoding', None)
        super().__init__(*args, **kwargs)

    def show_tooltip(self, text: str, second=1.0, x="", y="", id="", blocking=True):
        """Show ToolTip

        https://www.autohotkey.com/docs/commands/ToolTip.htm

        :param text: Tooltip text
        :type text: str
        :param ms: Wait time (s), defaults to 1000
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

        encoded_text = "% " + "".join([f"Chr({hex(ord(char))})" for char in text])
        script = self.render_template("gui/tooltip.ahk", text=encoded_text, second=second, x=x, y=y, id=id)
        return self.run_script(script, blocking=blocking) or None

    def _show_traytip(
        self, title: str, text: str, second=1.0, type_id=1, slient=False, large_icon=False, blocking=True
    ):
        """Show TrayTip (Windows 10 toast notification)

        https://www.autohotkey.com/docs/commands/TrayTip.htm

        :param title: Title of notification
        :type title: str
        :param text: Content of notification
        :type text: str
        :param second: Wait time (s) to be disappeared, defaults to 1.0
        :type second: float, optional
        :param type_id: Notification type `TRAYTIP_<type>`, defaults to 1
        :type type_id: int, optional
        :param slient: Shows toast without sound, defaults to False
        :type slient: bool, optional
        :param large_icon: Shows toast with large icon, defaults to False
        :type large_icon: bool, optional
        """

        encoded_title = "% " + "".join([f"Chr({hex(ord(char))})" for char in title])
        encoded_text = "% " + "".join([f"Chr({hex(ord(char))})" for char in text])
        option = type_id + (16 if slient else 0) + (32 if large_icon else 0)
        script = self.render_template(
            "gui/traytip.ahk", title=encoded_title, text=encoded_text, second=second, option=option
        )
        return self.run_script(script, blocking=blocking) or None

    def show_info_traytip(self, title: str, text: str, second=1.0, slient=False, large_icon=False, blocking=True):
        """Show TrayTip with info icon (Windows 10 toast notification)

        https://www.autohotkey.com/docs/commands/TrayTip.htm

        :param title: Title of notification
        :type title: str
        :param text: Content of notification
        :type text: str
        :param second: Wait time (s) to be disappeared, defaults to 1.0
        :type second: float, optional
        :param slient: Shows toast without sound, defaults to False
        :type slient: bool, optional
        :param large_icon: Shows toast with large icon, defaults to False
        :type large_icon: bool, optional
        :param blocked: Block program, defaults to True
        :type blocked: bool, optional
        """
        return self._show_traytip(title, text, second, self.TRAYTIP_INFO, slient, large_icon, blocking)

    def show_warning_traytip(self, title: str, text: str, second=1.0, slient=False, large_icon=False, blocking=True):
        """Show TrayTip with warning icon (Windows 10 toast notification)

        https://www.autohotkey.com/docs/commands/TrayTip.htm

        :param title: Title of notification
        :type title: str
        :param text: Content of notification
        :type text: str
        :param second: Wait time (s) to be disappeared, defaults to 1.0
        :type second: float, optional
        :param slient: Shows toast without sound, defaults to False
        :type slient: bool, optional
        :param large_icon: Shows toast with large icon, defaults to False
        :type large_icon: bool, optional
        :param blocked: Block program, defaults to True
        :type blocked: bool, optional
        """
        return self._show_traytip(title, text, second, self.TRAYTIP_WARNING, slient, large_icon, blocking)

    def show_error_traytip(self, title: str, text: str, second=1.0, slient=False, large_icon=False, blocking=True):
        """Show TrayTip with error icon (Windows 10 toast notification)

        https://www.autohotkey.com/docs/commands/TrayTip.htm

        :param title: Title of notification
        :type title: str
        :param text: Content of notification
        :type text: str
        :param second: Wait time (s) to be disappeared, defaults to 1.0
        :type second: float, optional
        :param slient: Shows toast without sound, defaults to False
        :type slient: bool, optional
        :param large_icon: Shows toast with large icon, defaults to False
        :type large_icon: bool, optional
        :param blocked: Block program, defaults to True
        :type blocked: bool, optional
        """
        return self._show_traytip(title, text, second, self.TRAYTIP_ERROR, slient, large_icon, blocking)


class AsyncGUIMixin(AsyncScriptEngine, GUIMixin):
    pass

from ahk.script import ScriptEngine
import os


class RegisteryMixin(ScriptEngine):
    def _render_template(self, template_name, *args, **kwargs):
        return self.render_template(os.path.join("registery", template_name))

    def _run_template(self, template_name, *args, **kwargs):
        script = self._render_template(template_name, *args, **kwargs)
        return self.run_script(script)

    def reg_read(self, key_name: str, value_name="") -> str:
        """Read registery

            Reference:
                https://www.autohotkey.com/docs/commands/RegRead.htm

            Arguments:
                key_name {str} -- RegEdit

            Keyword Arguments:
                value_name {str} -- TODO (default: {""})

            Returns:
                str -- Registery value
            """
        self._run_template("reg_read.ahk", key_name=key_name, value_name=value_name)

    def reg_delete(self, key_name: str, value_name="") -> None:
        """Delete registery

            Reference:
                https://www.autohotkey.com/docs/commands/RegDelete.htm

            Arguments:
                key_name {str} -- RegEdit

            Keyword Arguments:
                value_name {str} -- TODO (default: {""})
            """
        self._run_template("reg_delete.ahk", key_name=key_name, value_name=value_name)

    def reg_write(self, value_type: str, key_name: str, value_name="") -> None:
        """Write registery

            Reference:
                https://www.autohotkey.com/docs/commands/RegWrite.htm

            Arguments:
                value_type {str} -- RegEdit value
                key_name {str} -- RegEdit

            Keyword Arguments:
                value_name {str} -- TODO (default: {""})
            """
        self._run_template("reg_write.ahk", value_type=value_type, key_name=key_name, value_name=value_name)

    def reg_set_view(self, reg_view: int) -> None:
        """Set registery view

            Reference:
                https://www.autohotkey.com/docs/commands/SetRegView.htm

            Arguments:
                reg_view {str} -- Registery view
            """

        if reg_view not in [32, 64, "32", "64"]:
            raise ValueError("No valid bit, please use 32 or 64")

        self._run_template("reg_set_view.ahk", reg_view=reg_view)

    def reg_loop(self, reg: str, key_name: str, mode=""):
        """Loop registery

        Reference:
            https://www.autohotkey.com/docs/commands/LoopReg.htm

        Arguments:
            reg {str} -- TODO
            key_name {str} -- TODO

        Keyword Arguments:
                mode {str} -- TODO (default: {""})
        """
        raise NotImplementedError

        self._run_template("reg_loop.ahk", reg=reg, key_name=key_name, mode=mode)

    def read(self, *args, **kwargs):
        import warnings

        warnings.warn(
            'read() has been renamed and will be removed in a future version. use reg_read() instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.reg_read(*args, **kwargs)

    def write(self, *args, **kwargs):
        import warnings

        warnings.warn(
            'write() has been renamed and will be removed in a future version. use reg_write() instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.reg_write(*args, **kwargs)

    def set_view(self, *args, **kwargs):
        import warnings

        warnings.warn(
            'set_view() has been renamed and will be removed in a future version. use reg_set_view() instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.reg_set_view(*args, **kwargs)

    def delete(self, *args, **kwargs):
        import warnings

        warnings.warn(
            'delete() has been renamed and will be removed in a future version. use reg_delete() instead',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.reg_delete(*args, **kwargs)

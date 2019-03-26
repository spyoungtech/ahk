from ahk.script import ScriptEngine

class SoundMixin(ScriptEngine):
    def sound_beep(self, frequency=523, duration=150):
        """
        REF: https://autohotkey.com/docs/commands/SoundBeep.htm

        :param frequency: number between 37 and 32767
        :param duration: how long in milliseconds to play the beep
        :return: None
        """

        script = self.render_template('sound/beep.ahk', frequency=frequency, duration=duration)
        self.run_script(script)

    def sound_play(self, filename, wait=None):
        """
        REF: https://autohotkey.com/docs/commands/SoundPlay.htm

        :param filename:
        :param wait:
        :return:
        """

        script = self.render_template('sound/play.ahk', filename=filename, wait=wait)
        self.run_script(script)


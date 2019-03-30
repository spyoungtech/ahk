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

    def sound_play(self, filename, blocking=True):
        """
        REF: https://autohotkey.com/docs/commands/SoundPlay.htm

        :param filename:
        :param blocking:
        :param wait:
        :return:
        """

        script = self.render_template('sound/play.ahk', filename=filename, wait=1, blocking=blocking)
        self.run_script(script, blocking=blocking)

    def sound_get(self, device_number=1, component_type='MASTER', control_type='VOLUME'):
        """
        REF: https://autohotkey.com/docs/commands/SoundGet.htm


        :param device_number:
        :param component_type:
        :param control_type:
        :return:
        """

        script = self.render_template('sound/sound_get.ahk')
        return self.run_script(script)

    def get_volume(self, device_number=1):
        """
        REF: https://autohotkey.com/docs/commands/SoundGetWaveVolume.htm


        :param device_number:
        :return:
        """
        script = self.render_template('sound/get_volume.ahk', device_number=device_number)
        result = self.run_script(script)
        return result

    def sound_set(self, value, device_number=1, component_type='MASTER', control_type='VOLUME'):
        """
        REF: https://autohotkey.com/docs/commands/SoundSet.htm


        :param value:
        :param device_number:
        :param component_type:
        :param control_type:
        :return:
        """

        script = self.render_template('sound/sound_set.ahk', value=value,
                                      device_number=device_number,
                                      component_type=component_type,
                                      control_type=control_type)
        self.run_script(script)

    def set_volume(self, value, device_number=1):
        """
        REF: https://autohotkey.com/docs/commands/SoundSetWaveVolume.htm

        :param value: percent volume to set volume to
        :param device_number:
        :return:
        """

        script = self.render_template('sound/set_volume.ahk', value=value, device_number=device_number)
        self.run_script(script)

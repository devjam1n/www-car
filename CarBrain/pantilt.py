import pigpio
import threading
import time

class PanTilt:
    """
    Simple pan-tilt servo controller using pigpio, with auto-reset and calibration support.
    set_angles, set_pan, set_tilt, and calibration now use normalized values in the range -1..1.
    min_norm, max_norm, default_norm for both pan and tilt are in -1..1 and mapped to hardware pulsewidths internally.
    """
    def __init__(self, pan_pin, tilt_pin, invert_pan=False, invert_tilt=False,
                 pan_min_norm=-1, pan_max_norm=1, tilt_min_norm=-1, tilt_max_norm=1,
                 pan_default_norm=0, tilt_default_norm=0,
                 pan_hw_min_pulse=500, pan_hw_max_pulse=2500, tilt_hw_min_pulse=500, tilt_hw_max_pulse=2500):
        self.pan_pin = pan_pin
        self.tilt_pin = tilt_pin
        self.invert_pan = invert_pan
        self.invert_tilt = invert_tilt
        # Normalized calibration
        self.pan_min_norm = pan_min_norm
        self.pan_max_norm = pan_max_norm
        self.tilt_min_norm = tilt_min_norm
        self.tilt_max_norm = tilt_max_norm
        self.pan_default_norm = pan_default_norm
        self.tilt_default_norm = tilt_default_norm
        # Hardware pulsewidth limits
        self.pan_hw_min_pulse = pan_hw_min_pulse
        self.pan_hw_max_pulse = pan_hw_max_pulse
        self.tilt_hw_min_pulse = tilt_hw_min_pulse
        self.tilt_hw_max_pulse = tilt_hw_max_pulse
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. Is it running?")
        self.pan_norm = self.pan_default_norm
        self.tilt_norm = self.tilt_default_norm
        self._reset_timer = None
        self.set_angles(self.pan_default_norm, self.tilt_default_norm)

    def _norm_to_pulse(self, value, min_norm, max_norm, hw_min, hw_max):
        """Map value in min_norm..max_norm to hw_min..hw_max pulsewidth."""
        value = max(min_norm, min(max_norm, value))
        if max_norm != min_norm:
            norm = (value - min_norm) / (max_norm - min_norm)
        else:
            norm = 0.5
        return int(hw_min + norm * (hw_max - hw_min))

    def _start_reset_timer(self):
        if self._reset_timer:
            self._reset_timer.cancel()
        self._reset_timer = threading.Timer(0.2, self._reset_to_default)
        self._reset_timer.daemon = True
        self._reset_timer.start()

    def _reset_to_default(self):
        self.set_angles(self.pan_default_norm, self.tilt_default_norm, start_timer=False)

    def set_angles(self, pan, tilt, start_timer=True):
        # Accept -1..1, map to calibrated range
        pan_to_set = -pan if self.invert_pan else pan
        tilt_to_set = -tilt if self.invert_tilt else tilt
        
        pan_pulse = self._norm_to_pulse(pan_to_set, self.pan_min_norm, self.pan_max_norm, self.pan_hw_min_pulse, self.pan_hw_max_pulse)
        tilt_pulse = self._norm_to_pulse(tilt_to_set, self.tilt_min_norm, self.tilt_max_norm, self.tilt_hw_min_pulse, self.tilt_hw_max_pulse)
        
        self.pi.set_servo_pulsewidth(self.pan_pin, pan_pulse)
        self.pi.set_servo_pulsewidth(self.tilt_pin, tilt_pulse)
        
        self.pan_norm = pan
        self.tilt_norm = tilt
        
        if start_timer:
            self._start_reset_timer()

    def set_pan(self, value):
        self.set_angles(value, self.tilt_norm)

    def set_tilt(self, value):
        self.set_angles(self.pan_norm, value)

    def set_calibration(self, pan_min_norm=None, pan_max_norm=None, tilt_min_norm=None, tilt_max_norm=None,
                        pan_default_norm=None, tilt_default_norm=None):
        if pan_min_norm is not None:
            self.pan_min_norm = pan_min_norm
        if pan_max_norm is not None:
            self.pan_max_norm = pan_max_norm
        if tilt_min_norm is not None:
            self.tilt_min_norm = tilt_min_norm
        if tilt_max_norm is not None:
            self.tilt_max_norm = tilt_max_norm
        if pan_default_norm is not None:
            self.pan_default_norm = pan_default_norm
        if tilt_default_norm is not None:
            self.tilt_default_norm = tilt_default_norm

    def cleanup(self):
        if self._reset_timer:
            self._reset_timer.cancel()
        self.pi.set_servo_pulsewidth(self.pan_pin, 0)
        self.pi.set_servo_pulsewidth(self.tilt_pin, 0)
        self.pi.stop()
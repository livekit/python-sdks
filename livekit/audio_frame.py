import ctypes


class AudioFrame():
    def __init__(self, sample_rate: int, num_channels: int, samples_per_channel: int, data=None, ffi_handle=None):
        self._ffi_handle = ffi_handle
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        self.samples_per_channel = samples_per_channel
        if data is None:
            self.data = (ctypes.c_int16 *
                         (num_channels * samples_per_channel))()
        else:
            self.data = data

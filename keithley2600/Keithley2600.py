import time
from pyvisa import Resource


class Keithley2600:
    """
    Keithley 2600 Source Meter class. It contains basic functions to set up the device and make measurements.

    The commands and functions of the TSP language are exposed to Python.
    The interface that this class provides is suitable only for making a single measurement per command.
    For making multiple readings per measurement, this class has to be extended to use buffers.
    """

    def __init__(self, device: Resource, delay=0.1):
        self.smu = device
        self.reset_device()
        self.default_setup()
        self.delay = delay

    def measure_resistance(self):
        """
        Get single resistance measurement
        :return: resistance, Ohm
        """
        response =self.smu.query('print(smua.measure.r())')
        resistance = float(response.strip())
        return resistance

    def measure_iv(self):
        """
        Get a single pair of the current and voltage measurement
        :return: current, A; voltage, V
        """
        self.smu.write("ireading, vreading = smua.measure.iv()")
        time.sleep(self.delay)
        response = self.smu.query("printnumber(ireading,vreading)").split(",")
        i = float(response[0])
        v = float(response[1])
        return i, v

    def measure_power(self):
        """
        Get single power measurement
        :return: power, W
        """
        response = self.smu.query('print(smua.measure.p())')
        power = float(response.strip())
        return power

    def reset_device(self):
        """
        Reset the device to the default state
        :return:
        """
        self.smu.write("smua.reset()")

    def device_id(self):
        """
        Get the device name, model and serial number
        :return: string
        """
        self.smu.write("print(smua.idn())")
        response = self.smu.read()
        return response

    @property
    def output(self):
        """
        Get the current state of the output (On or Off)
        :return True if switched on, False if switch off
        """
        state = self.smu.query('print(smua.source.output)')
        return bool(int(float(state.strip())))

    @output.setter
    def output(self, flag):
        """
        Turn output on or off
        :param switch: True to switch on, False to switch off
        """
        self.smu.write(f'smua.source.output = {int(flag)}')

    def default_setup(self):
        """
        Set the device to default setup:

        - DC voltage source, 0 V
        - autorange current
        - autorange voltage
        - output off
        :return:
        """
        # self.smu.write("smua.source.func = smua.OUTPUT_DCVOLTS")
        # self.smu.write("smua.source.levelv = 0.0")
        # self.smu.write("smua.source.autorangev = smua.AUTORANGE_ON")
        # self.smu.write("smua.measure.autorangei = smua.AUTORANGE_ON")
        # self.smu.write("smua.source.output = smua.OUTPUT_OFF")
        self.source_function = 1
        self.level_v = 0
        self.autorange_i = 1
        self.autorange_v = 1
        self.output = False

    def setup_for_resistance_measurement(self):
        """
        Set up the device for resistance measurement:

        - DC current source, 1 mA
        - autorange voltage
        - NPLC = 5
        - delay = 0.1 s
        - voltage range = 20 V
        - current range = 1 mA
        :return:
        """
        # self.smu.write('*RST')
        # self.smu.write('smua.reset()')
        # self.smu.write('smua.source.func = smua.OUTPUT_DCAMPS')
        # self.smu.write('smua.source.leveli = 1e-3')
        # self.smu.write('smua.measure.autorangev = smua.AUTORANGE_ON')
        # self.smu.write('smua.measure.nplc = 5')
        # self.smu.write('smua.measure.delay = 0.1')
        # self.smu.write('smua.measure.rangev = 20')
        # self.smu.write('smua.measure.rangei = 1e-3')
        self.smu.write('smua.measure.r(smua.nvbuffer1)')
        self.reset_device()
        self.source_function = 0
        self.level_i = 1e-3
        self.autorange_v = 1
        self.nplc = 5
        self.delay = 0.1
        self.range_v = 20
        self.range_i = 1e-3

    def setup_for_IV_measurement(self, iLimit, NPLC):
        """
        Set up the device for IV measurement:

        - DC voltage source, 0 V
        - autorange current
        - autorange voltage

        :param iLimit: current limit, A
        :param NPLC: number of power line cycles
        :return:
        """
        # self.smu.write("*RST")
        # self.smu.write("smua.source.func = smua.OUTPUT_DCVOLTS")
        # self.smu.write("smua.source.levelv = 0.0")
        # self.smu.write("smua.source.autorangev = smua.AUTORANGE_ON")
        # self.smu.write("smua.measure.autorangei = smua.AUTORANGE_ON")
        # self.set_i_limit(iLimit)
        # self.set_NPLC(NPLC)
        self.reset_device()
        self.source_function = 1
        self.level_v = 0
        self.autorange_i = 1
        self.autorange_v = 1
        self.limit_i = iLimit
        self.nplc = NPLC

    @property
    def source_function(self):
        """
        Get the output function of the source. Can be either 1 (voltage output) or 0 (current output)
        :return: string
        """
        response = self.smu.query('print(smua.source.func)')
        return response

    @source_function.setter
    def source_function(self, func):
        """
        Set the output function of the source.
        :param func: 1 for voltage output, 0 for current output
        """
        self.smu.write(f'smua.source.func = {func}')

    @property
    def nplc(self):
        """
        Get the integration aperture for measurements (number of power line cycles to average over)

        This attribute controls the integration aperture for the analog-to-digital converter (ADC).
        The integration aperture is based on the number of power line cycles (NPLC), where 1 PLC for 60 Hz
        is 16.67 ms (1/60) and 1 PLC for 50 Hz is 20 ms (1/50).
        :return: number of power line cycles
        """
        response = self.smu.query('print(smua.measure.nplc)')
        return float(response.strip())

    @nplc.setter
    def nplc(self, NPLC):
        """
        Set the integration aperture for measurements (number of power line cycles to average over)
        :param NPLC: number of power line cycles
        """
        self.smu.write(f'smua.measure.nplc = {NPLC}')

    @property
    def delay(self):
        """
        Get the delay between measurements
        :return: delay, s
        """
        response = self.smu.query('print(smua.measure.delay)')
        return float(response.strip())

    @delay.setter
    def delay(self, delay):
        """
        Set the delay between measurements
        :param delay: delay, s
        """
        self.smu.write(f'smua.measure.delay = {delay}')

    @property
    def range_i(self):
        """
        Get the value of the current measurement range
        :return: range limit, A
        """
        response = self.smu.query('print(smua.measure.rangei)')
        return float(response.strip())

    @range_i.setter
    def range_i(self, i_range):
        """
        Set the current measurement range
        :param i_range: range limit, A
        """
        self.smu.write(f'smua.measure.rangei = {i_range}')

    @property
    def range_v(self):
        """
        Get the value of the voltage measurement range
        :return: range limit, V
        """
        response = self.smu.query('print(smua.measure.rangev)')
        return float(response.strip())

    @range_v.setter
    def range_v(self, v_range):
        """
        Set the voltage measurement range
        :param v_range: range limit, V
        """
        self.smu.write(f'smua.measure.rangev = {v_range}')

    @property
    def autorange_i(self):
        """
        Get the autorange state of the current measurement
        :return: autorange state
        """
        response = self.smu.query('print(smua.measure.autorangei)')
        return bool(int(float(response.strip())))

    @autorange_i.setter
    def autorange_i(self, autorange):
        """
        Set the autorange state of the current measurement

        - 0 for disabling autorange
        - 1 for enabling autorange
        - 2 to set the measure range automatically to the limit
        range
        :param autorange: autorange state
        """
        self.smu.write(f'smua.measure.autorangei = {autorange}')

    @property
    def autorange_v(self):
        """
        Get the autorange state of the voltage measurement
        :return: autorange state
        """
        response = self.smu.query('print(smua.measure.autorangev)')
        return bool(int(float(response.strip())))

    @autorange_v.setter
    def autorange_v(self, autorange):
        """
        Set the autorange state of the voltage measurement

        - 0 for disabling autorange
        - 1 for enabling autorange
        - 2 to set the measure range automatically to the limit
        :param autorange: autorange state
        """
        self.smu.write(f'smua.measure.autorangev = {autorange}')

    @property
    def level_v(self):
        """
        Get the voltage output level
        :return: voltage level, V
        """
        response = self.smu.query('print(smua.source.levelv)')
        return float(response.strip())

    @level_v.setter
    def level_v(self, v_level):
        """
        Set the voltage output level
        :param v_level: voltage level, V
        """
        self.smu.write(f'smua.source.levelv = {v_level}')

    @property
    def level_i(self):
        """
        Get the current output level
        :return: current level, A
        """
        response = self.smu.query('print(smua.source.leveli)')
        return float(response.strip())

    @level_i.setter
    def level_i(self, i_level):
        """
        Set the current output level
        :param i_level: current level, A
        """
        self.smu.write(f'smua.source.leveli = {i_level}')

    @property
    def limit_i(self):
        """
        Get the limit of the current ouput
        :return: current limit, A
        """
        response = self.smu.query('print(smua.source.limiti)')
        return float(response.strip())

    @limit_i.setter
    def limit_i(self, i_limit):
        """
        Set the limit of the current output
        :param i_limit: current limit, A
        """
        self.smu.write(f'smua.source.limiti = {i_limit}')

    @property
    def limit_v(self):
        """
        Get the limit of the voltage output
        :return: voltage limit, V
        """
        response = self.smu.query('print(smua.source.limitv)')
        return float(response.strip())

    @limit_v.setter
    def limit_v(self, v_limit):
        """
        Set the limit of the voltage output
        :param v_limit: voltage limit, V
        """
        self.smu.write(f'smua.source.limitv = {v_limit}')

    def __del__(self):
        self.output = False
        self.reset_device()
        self.smu.close()


if __name__ == '__main__':
    import pyvisa

    rm = pyvisa.ResourceManager()
    devs = rm.list_resources()
    dev = rm.open_resource(devs[0])
    smu = Keithley2600(dev)
    smu.level_i = 1e-3

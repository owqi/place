"""The Polytech vibrometer instrument.

This module allows interfacing with Polytec vibrometer OFV-5000 controller and
OFV-505 sensor head. Functions based on Polytec "RS-232 Interface Commands:
OFV-5000 User Manual"

**NOTE** For each polytec controller, different decoders may be installed.
These values should be stored in the your PLACE config file.  (~/.place.cfg)

Example:
DD-300 is 'DisplDec,0'
DD-900 is 'DisplDec,1'
VD-08 is 'VeloDec,0'
VD-09 is 'VeloDec,1'
"""
from time import sleep
import re
from serial import Serial
import serial
import numpy as np
import matplotlib.pyplot as plt
from place.config import PlaceConfig
from place.plugins.instrument import Instrument

_NUMBER = r'[-+]?\d*\.\d+|\d+'

class Vibrometer(Instrument):
    """The polytec class

    The Polytec module requires the following configuration data (accessible as
    self._config['*key*']):

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    dd_300                    bool           flag indicating use of the DD-300
    dd_300_range              string         the range of DD-300
    dd_900                    bool           flag indicating use of the DD-900
    dd_900_range              string         the range of DD-900
    vd_08                     bool           flag indicating use of the VD-08
    vd_08_range               string         the range of VD-08
    vd_09                     bool           flag indicating use of the VD-09
    vd_09_range               string         the range of VD-09
    autofocus                 string         the type of autofocus span
    autofocus_everytime       bool           flag indicating if autofocus should be
                                             performed at every update
    timeout                   float          number of seconds to wait for autofocus
    plot                      bool           turns live plotting on or off
    ========================= ============== ================================================

    The Polytec module will produce the following experimental metadata:

    ========================= ============== ================================================
    Key                       Type           Meaning
    ========================= ============== ================================================
    vd_08_time_delay          float          the decoder time delay (if used)
    vd_08_maximum_frequency   float          the decoder maximum frequency (if used)
    vd_09_time_delay          float          the decoder time delay (if used)
    vd_09_maximum_frequency   float          the decoder maximum frequency (if used)
    dd_300_calibration        float          the decoder calibration (if used)
    dd_300_calibration_units  string         the decoder units (if used)
    dd_900_calibration        float          the decoder calibration (if used)
    dd_900_calibration_units  string         the decoder units (if used)
    vd_08_calibration         float          the decoder calibration (if used)
    vd_08_calibration_units   string         the decoder units (if used)
    vd_09_calibration         float          the decoder calibration (if used)
    vd_09_calibration_units   string         the decoder units (if used)
    ========================= ============== ================================================

    The Polytec will produce the following experimental data:

    +---------------+-------------------------+---------------------------+
    | Heading       | Type                    | Meaning                   |
    +===============+=========================+===========================+
    | signal        | uint63                  | the signal level recorded |
    |               |                         | from the vibrometer       |
    +---------------+-------------------------+---------------------------+

    .. note::

        PLACE will usually add the instrument class name to the heading. For
        example, ``signal`` will be recorded as ``Polytec-signal`` when using
        the Polytec vibrometer. The reason for this is because NumPy will not
        check for duplicate heading names automatically, so prepending the
        class name greatly reduces the likelihood of duplication.

    """

    def __init__(self, config):
        """Constructor"""
        Instrument.__init__(self, config)
        self._serial = None
        self._last_y = None

    def config(self, metadata, total_updates):
        """Configure the vibrometer.

        :param metadata: scan metadata
        :type metadata: dict

        :param total_updates: number of updates for the scan
        :type total_updates: int
        """
        name = self.__class__.__name__
        self._serial = Serial(
            port=PlaceConfig().get_config_value(name, "port"),
            baudrate=PlaceConfig().get_config_value(name, "baudrate"),
            timeout=10,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

        if self._config['dd_300']:
            self._setup_decoder(metadata, 'dd_300')

        if self._config['dd_900']:
            self._setup_decoder(metadata, 'dd_900')

        if self._config['vd_08']:
            self._setup_decoder(metadata, 'vd_08')

        if self._config['vd_09']:
            self._setup_decoder(metadata, 'vd_09')

        if self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.clf()
            plt.ion()

    def update(self, update_number):
        """Update the vibrometer.

        :param update_number: the count of the current update (0-indexed)
        :type update_number: int

        :returns: an array containing the signal level
        :rtype: numpy.array dtype='uint64'
        """
        if self._config['autofocus'] != 'none':
            if update_number == 0 or self._config['autofocus_everytime'] is True:
                self._autofocus_vibrometer(
                    span=self._config['autofocus'],
                    timeout=self._config['timeout'])
        signal_level = self._get_signal_level()
        field = '{}-signal'.format(self.__class__.__name__)
        data = np.array([(signal_level,)], dtype=[(field, 'uint64')])
        if self._config['plot']:
            plt.figure(self.__class__.__name__)
            self._draw_plot(signal_level, update_number)
        return data

    def cleanup(self, abort=False):
        """Free resources and cleanup.

        Display the final plot, unless aborted or plotting is disabled.

        :param abort: indicates that the scan is being aborted and is unfinished
        :type abort: bool
        """
        if abort is False and self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

        if abort is False:
            self._serial.close()

# PRIVATE METHODS

    def _write(self, message):
        """Send a message

        :param message: message to be sent to the Polytec receiver
        :type message: str
        """
        self._serial.write(message.encode())

    def _write_and_readline(self, message):
        """Send a message and get a response.

        :param message: message to be sent to the Polytec receiver
        :type message: str

        :returns: the decoded response
        :rtype: str
        """
        self._write(message)
        return self._serial.readline().decode('ascii', 'replace')

    def _setup_decoder(self, metadata, name):
        """Set the range for the decoder and obtain metadata

        :param metadata: scan metadata
        :type metadata: dict

        :param name: the name to use for the decoder
        :type name: str
        """
        id_ = PlaceConfig().get_config_value(self.__class__.__name__, name)
        self._set_range(id_, self._config[name + '_range'])
        if name == 'vd_08' or name == 'vd_09':
            metadata[name + '_time_delay'] = self._get_delay(id_)
            metadata[name + '_maximum_frequency'] = self._get_maximum_frequency(id_)
        calibration, calibration_units = self._get_range(name, id_)
        metadata[name + '_calibration'] = calibration
        metadata[name + '_calibration_units'] = calibration_units

    def _autofocus_vibrometer(self, span='Full', timeout=30):
        """Autofocus the vibrometer.

        :param span: the range in which the vibrometer should look for focus
        :type span: str

        :param timeout: the number of seconds to wait for focus before failing
        :type timeout: int

        :raises RuntimeError: if focus is not found before timeout
        """
        self._write('Set,SensorHead,0,AutoFocusSpan,'+span+'\n')
        self._write('Set,SensorHead,0,AutoFocus,Search\n')
        countdown = timeout
        tick = 1
        while countdown > 0:
            sleep(tick)
            countdown -= tick
            if self._write_and_readline('Get,SensorHead,0,AutoFocusResult\n') == 'Found\n':
                break
        else:
            raise RuntimeError('autofocus failed')

    def _get_delay(self, id_):
        """Get time delay.

        :param id_: the identification string for the decoder
        :type id_: str

        :returns: the delay time
        :rtype: float
        """
        delay_string = self._write_and_readline('Get,' + id_ + ',SignalDelay\n')
        return float(re.findall(_NUMBER, delay_string)[0])

    def _get_maximum_frequency(self, id_):
        """Get the maximum frequency.

        :param id_: the identification string for the decoder
        :type id_: str

        :returns: the frequency value of the selected decoder
        :rtype: float

        :raises ValueError: if maximum frequency is not available
        """
        frequency_string = self._write_and_readline('Get,' + id_ + ',MaxFreq\n')
        if frequency_string == 'Not Available':
            raise ValueError('maximum frequency for {} not available'.format(id_))
        return _parse_frequency(frequency_string)

    def _get_range(self, name, id_):
        """Get the current range.

        :param name: the name for the decoder
        :type name: str

        :param id_: the identification string for the decoder
        :type id_: str

        :returns: the range value and units returned from the instrument
        :rtype: float, string

        :raises ValueError: if decoder name is not recognized
        """
        decoder_range = self._write_and_readline('Get,' + id_ + ',Range\n')
        if name == 'dd_300':
            range_num = re.findall(_NUMBER, self._config['dd_300_range'])
        elif name == 'dd_900':
            raw_num = re.findall(_NUMBER, self._config['dd_900_range'])
            range_num = [string.replace('um', 'µm') for string in raw_num]
        elif name == 'vd_08':
            range_num = re.findall(_NUMBER, self._config['vd_08_range'])
        elif name == 'vd_09':
            range_num = re.findall(_NUMBER, self._config['vd_09_range'])
        else:
            raise ValueError('unknown decoder: ' + name)
        del_num_r = len(range_num)+1
        calib = float(range_num[0])
        calib_unit = decoder_range[del_num_r:].lstrip()
        return calib, calib_unit

    def _set_range(self, id_, range_):
        """Set the range.

        :param id_: the identification string for the decoder
        :type id_: str

        :param range_: the desired decoder range
        :type range_: str
        """
        self._write('Set,' + id_ + ',Range,' + range_ + '\n')

    def _get_signal_level(self):
        return int(self._write_and_readline('Get,SignalLevel,0,Value\n'))

    def _draw_plot(self, signal_level, update_number):
        if update_number == 0:
            curr_y = signal_level
            plt.plot(update_number, curr_y, '-o')
            plt.xlabel('trace')
            plt.ylabel('signal level')
            self._last_y = curr_y
        else:
            curr_y = signal_level
            plt.plot([update_number - 1, update_number],
                     [self._last_y, curr_y], '-o')
            self._last_y = curr_y
        plt.pause(0.05)

def _parse_frequency(frequency_string):
    """Calculate a frequency from a string.

    Takes a frequency string and parses it to a float value.

    .. doctest::

        >>> _parse_frequency('20MHz')
        20000000.0
        >>> _parse_frequency('20 MHz')
        20000000.0
        >>> _parse_frequency('5kHz')
        5000.0
        >>> _parse_frequency('16.6mhz')
        16600000.000000002
        >>> _parse_frequency('16.6 mhz')
        16600000.000000002

    :param frequency_string: string to be parsed
    :type frequency_string: str

    :returns: the frequency value
    :rtype: float

    :raises ValueError: if frequency units are not recognized
    """
    re_match = re.match(
        r'([-+]?\d*\.\d+|\d+)\s?([kmg]?Hz)',
        frequency_string,
        flags=re.IGNORECASE # pylint: disable=no-member
        )
    if re_match is None:
        raise ValueError('could not parse frequency string: ' + frequency_string)
    else:
        num_str, unit_str = re_match.groups()
    if unit_str.lower() == 'hz':
        return float(num_str)
    elif unit_str.lower() == 'khz':
        return float(num_str) * 10**3
    elif unit_str.lower() == 'mhz':
        return float(num_str) * 10**6
    elif unit_str.lower() == 'ghz':
        return float(num_str) * 10**9
    else:
        raise ValueError('could not match units of frequency: ' + unit_str)

"""Post-processing plugin to perform IQ demodulation"""
try:
    from obspy.signal.filter import lowpass # pylint: disable=import-error
except ImportError:
    pass
import numpy as np
from numpy.lib import recfunctions as rfn
import matplotlib.pyplot as plt
from place.config import PlaceConfig
from place.plugins.postprocessing import PostProcessing

# the name of the field that will contain the post-processed data
FIELD = 'IQ-demodulation-data'
# the type of the data contained in the post-processed data
TYPE = 'float64'

class IQDemodulation(PostProcessing):
    """Subclass of PLACE PostProcessing.

    This class performs IQ demodulation on trace data from PLACE
    """
    def __init__(self, config):
        PostProcessing.__init__(self, config)
        self.trace_field = None
        self.sampling_rate = None
        self.updates = None
        self.lowpass_cutoff = None

    def config(self, metadata, total_updates):
        """Configuration for IQ demodulation

        IQ demodulation requires the following configuration data (accessible as
        self._config['*key*']):

        ========================= ============== ================================================
        Key                       Type           Meaning
        ========================= ============== ================================================
        field_ending              string         the ending of the field to be post-processed
        plot                      bool           true if the post-processed data should be
                                                 plotted
        remove_trace_data         bool           true if the original trace data should be
                                                 removed (saving space); false if all data
                                                 should be retained
        y_shift                   float          an amount to shift all data points to put
                                                 the zero point at zero (mostly used for
                                                 data that is unsigned)
        ========================= ============== ================================================
        """
        try:
            self.sampling_rate = metadata['sampling_rate']
        except KeyError:
            raise RuntimeError("'sampling_rate' is not available in the metadata - " +
                               "IQ demodulation postprocessing cannot be performed")
        self.updates = total_updates
        name = self.__class__.__name__
        self.lowpass_cutoff = float(PlaceConfig().get_config_value(name,
                                                                   'lowpass_cutoff',
                                                                   '10e6'))
        metadata['demodulation'] = 'IQ'
        if self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.clf()
            plt.ion()

    def update(self, update_number, data):
        if self.trace_field is None:
            for device in data.dtype.names:
                if device.endswith(self._config['field_ending']):
                    field = device
                    break
            else:
                err = ('field ending in {} '.format(self._config['field_ending']) +
                       'not found - cannot perform postprocessing')
                raise RuntimeError(err)
        # copy the data out
        data_to_process = data[field][0].copy()
        # GUI option to either keep original traces or delete them
        if self._config['remove_trace_data']:
            other_data = rfn.drop_fields(data, field, usemask=False)
        else:
            other_data = data
        # perform post-processing
        processed_data, times = self._post_processing(data_to_process)
        # plot data
        if self._config['plot']:
            plot_data = lowpass(processed_data[FIELD],
                                self._config['lowpass_cutoff'],
                                self.sampling_rate,
                                corners=4,
                                zerophase=True)
            plt.figure(self.__class__.__name__)
            # current plot
            plt.subplot(211)
            plt.cla()
            plt.plot(times, plot_data)
            plt.xlabel(r'Time [microseconds]')
            plt.ylabel(r'Velocity[m/s]')
            plt.pause(0.05)
            # wiggle plot
            plt.subplot(212)
            axes = plt.gca()
            data = plot_data / (2*max(plot_data)) + update_number
            axes.plot(data, times, color='black', linewidth=0.5)
            plt.xlim((-1, self.updates))
            plt.xlabel('Update Number')
            plt.ylabel(r'Time [microseconds]')
            plt.pause(0.05)

        # insert and return the new data
        return rfn.merge_arrays([other_data, processed_data], flatten=True, usemask=False)

    def cleanup(self, abort=False):
        if abort is False and self._config['plot']:
            plt.figure(self.__class__.__name__)
            plt.ioff()
            print('...please close the {} plot to continue...'.format(self.__class__.__name__))
            plt.show()

    def _post_processing(self, data_to_process):
        #wavelength = 1550.0e-9
        ## Read the channels from the data
        channel1 = np.array(data_to_process[0]).astype(TYPE)
        channel2 = np.array(data_to_process[1]).astype(TYPE)
        #channel3 = np.array(data_to_process[2]).astypye(float)
        times = np.arange(0, len(channel1[0])) * (1 / self.sampling_rate)

        ##call vfm for processing the data on each record
        y_shift = self._config['y_shift']
        processed = np.array([_vfm(channel1[i] + y_shift,
                                   channel2[i] + y_shift,
                                   times) for i in range(len(channel1))])
        ##average and lowpass the processed data
        processed_avg = lowpass(processed.mean(axis=0),
                                self.lowpass_cutoff,
                                self.sampling_rate,
                                corners=4,
                                zerophase=True)
        # make a numpy array for our data
        new_data = np.array((1,), dtype=[(FIELD, TYPE, len(processed_avg)+1)])
        ## copy the processed data to the numpy array
        new_data[FIELD] = np.append(processed_avg, processed_avg[-1])
        return new_data, times

def _vfm(i_values, q_values, times):
    """Compute the Doppler shift from I and Q values  """
    q_part = q_values[1:] * np.diff(i_values) / np.diff(times)
    i_part = i_values[1:] * np.diff(q_values) / np.diff(times)
    q_squared = q_values[1:]**2
    i_squared = i_values[1:]**2
    return np.array((i_part - q_part) / (i_squared + q_squared)) / (2*np.pi)

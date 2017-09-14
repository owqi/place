"""Stanford Research Systems SR850 DSP Lock-In Amplifier"""
from place.plugins.instrument import Instrument
from place.config import PlaceConfig

class SR850(Instrument):
    """PLACE module for controlling the SRS SR850 lock-in amplifier."""
    def config(self, metadata, total_updates):
        """Configure the amplifier.

        Typically, the amplifier will be configured at the beginning of an
        experiment, so the majority of the activity will happen in this method.

        :param metadata: metadata for the experiment
        :type metadata: dict

        :param total_updates: the number of update steps that will be in this
                              experiment
        :type total_updates: int
        """
        serial_port = PlaceConfig().get_config_value(self.__class__.__name__,
                                                     'serial_port', '/dev/ttys0')
        metadata['sr850_settings'] = {
            'serial_port': serial_port,
            }

    def update(self, update_number):
        """Perform updates to the amplifier during an experiment.

        All settings are set during the config phase, so this method does not
        currently do anything.

        :param update_number: the current update count
        :type update_number: int
        """
        pass

    def cleanup(self, abort=False):
        """Cleanup the amplifier.

        Nothing to cleanup.

        :param abort: indicates the experiment is being aborted rather than
                      having finished normally
        :type abort: bool
        """
        pass

    def get_id(self):
        """Prints and returns SR850's device configuration."""
        return self._query('*IDN?')

    def checkModel(self):
        """check Lock-In model"""
        ID = SR850().getID()
        IDN = ID[0:31]
        if IDN != 'Stanford_Research_Systems,SR850':
            print('SRS SR830 initialisation error, check connections/settings')
            exit()
        print('SRS SR850 intialised')

class GainTime(SR850):
    """ Gain and time constant commands"""

    def setSensitivity(self,i):
        """
        Sets sensitivity
        i    sensitivity
       ---  -------------
        0     2 nV/fA
        1     5 nV/fA
        2     10 nV/fA      
        3     20 nV/fA
        4     50 nV/fA
        5     100 nV/fA
        6     200 nV/fA
        7     500 nV/fA
        8     1 microV/pA
        9     2 microV/pA
        10    5 microV/pA
        11    10 microV/pA
        12    20 microV/pA
        13    50 microV/pA
        14    100 microV/pA
        15    200 microV/pA
        16    500 microV/pA
        17    1 mV/nA
        18    2 mV/nA
        19    5 mV/nA
        20    10 mV/nA
        21    20 mV/nA
        22    50 mV/nA
        23    100 mV/nA
        24    200 mV/nA
        25    500 mV/nA
        26    1 V/microA
        """
        self.amp.write('sens %s \n'%i)
        return

    def getSensitivity(self):
        """
        Queries and returns sensitivity.
           i    sensitivity
       ---  -------------
        0     2 nV/fA
        1     5 nV/fA
        2     10 nV/fA      
        3     20 nV/fA
        4     50 nV/fA
        5     100 nV/fA
        6     200 nV/fA
        7     500 nV/fA
        8     1 microV/pA
        9     2 microV/pA
        10    5 microV/pA
        11    10 microV/pA
        12    20 microV/pA
        13    50 microV/pA
        14    100 microV/pA
        15    200 microV/pA
        16    500 microV/pA
        17    1 mV/nA
        18    2 mV/nA
        19    5 mV/nA
        20    10 mV/nA
        21    20 mV/nA
        22    50 mV/nA
        23    100 mV/nA
        24    200 mV/nA
        25    500 mV/nA
        26    1 V/microA
        """
        self.amp.write('sens?\n')
        return self.amp.readline()

    def setReserveMode(self,i):
        """
        Sets reserve mode.
        i = 0 (Max)
          = 1 (Manual)
          = 2 (Min)
        """
        self.amp.write('rmod %s \n'%i)
        return 

    def getReserveMode(self):
        """
        Queries and returns reserve mode.
        i = 0 (Max)
          = 1 (Manual)
          = 2 (Min)
        """
        self.amp.write('rmod?\n')
        return self.amp.readline()

    def setDynamicReserve(self,i):
        """
        Sets dynamic reserve to i^(th) available reserve (between 0 and 5).  
        Must be in Manual reserve mode (see GainTime().setReserveMode())
        i = 0 (minimum reserve for present sensitivity and time constant
          = 1 (next highest reserve)
          = ...
          = 5 (always sets reserve to max.)
          Reserve increases by 10 dB for each successive value of i.
        """
        self.amp.write('rsrv %s \n'%i)
        return

    def getDynamicReserve(self):
        """
        Queries and returns dynamic reserve.
        i = 0 (minimum reserve for present sensitivity and time constant
          = 1 (next highest reserve)
          = ...
          = 5 (always sets reserve to max.)
          Reserve increases by 10 dB for each successive value of i.
        """    
        self.amp.write('rsrv?\n')
        return self.amp.readline()

    def setTimeConstant(self,timeconst):
        """
        Sets time constant.
        time constant options:  10 us, 30us, 100us, 300us, 1ms, 1s, 3s, 10s, 30s, 100s, 300s, 1ks, 3ks, 10ks, 30ks
        """

        constants = ['10us','30us','100us','300us','1ms','3ms','10ms','30ms','100ms','300ms','1s','3s','10s','30s','100s','300s','1ks','3ks','10ks','30ks']

        i = constants.index(timeconst)
    
        self.amp.write('oflt %s \n'%i)
        return

    def getTimeConstant(self):
        """
        Queries and returns the time constant.
        Time constant > 30 x can't bew set if harmonic x ref. frequency > 200 Hz.  
        Time constants < minimum time constant based on filter slope and dynamic reserve will set time constant to minimum allowed time constant.
        i     time constant   
        0     10 us
        1     30 us
        2     100 us
        3     300 us
        4     1 ms
        5     3 ms
        6     10 ms
        7     30 ms
        8     100 ms
        9     300 ms   
        10    1 s
        11    3 s
        12    10 s
        13    30 s
        14    100 s
        15    300 s
        16    1 ks
        17    3 ks
        18    10 ks
        19    30 ks
        """
        self.amp.write('oflt?\n')
        return self.amp.readline()


    def setLowFilterSlope(self,i):
        """
        Sets low pass filter slope.
        i = 0 (6 dB/oct)
          = 1 (12 dB/oct)
          = 2 (18 dB/oct)
          = 3 (24 dB/oct)
        """
        self.amp.write('ofsl %s \n'%i)
        return

    def getLowFilterSlope(self):
        """
        Queries and returns low pass filter slope.
        i = 0 (6 dB/oct)
          = 1 (12 dB/oct)
          = 2 (18 dB/oct)
          = 3 (24 dB/oct)
        """

        self.amp.write('ofsl?\n')
        return self.amp.readline()

    def setSynchFilter(self,i):
        """
        Sets synchronous filter status.
        Only turned on if detection frequency < 200 Hz.
        i = 0 (off)
          = 1 (synchronous filter below 200 Hz)
        """
        self.amp.write('sync %s \n'%i)
        return

    def getSynchFilter(self):
        """
        Queries and returns synchronous filter status.
        i = 0 (off)
          = 1 (synchronous filter below 200 Hz)
        """

        self.amp.write('synch?\n')
        return self.amp.readline()


class OutputOffset(SR850):
    """Output and Offset Commands"""
    
    def setOutputSource(self,i, j):
        """
        Sets front panel output sources. Select the channel (i) and output quantity (j).
        CH 1 (i = 1)     CH2 (i = 2)
        ---------------  ---------------
        j = 0 (X)        j = 0 (Y)
          = 1 (R)          = 1 (R)
          = 2 (theta)      = 2 (theta)
          = 3 (Trace 1)    = 3 (Trace 1)
          = 4 (Trace 2)    = 4 (Trace 2)
          = 5 (Trace 3)    = 5 (Trace 3)
          = 6 (Trace 4)    = 6 (Trace 4)
        """
        self.amp.write('fout %s %s \n'%(i,j))
        return

    def getOutputSource(self):
        """
        Queries and returns the front panel output sources.
        CH 1 (i = 1)     CH2 (i = 2)
        ---------------  ---------------
        j = 0 (X)        j = 0 (Y)
          = 1 (R)          = 1 (R)
          = 2 (theta)      = 2 (theta)
          = 3 (Trace 1)    = 3 (Trace 1)
          = 4 (Trace 2)    = 4 (Trace 2)
          = 5 (Trace 3)    = 5 (Trace 3)
          = 6 (Trace 4)    = 6 (Trace 4)
        """

        self.amp.write('fout?\n')
        return self.amp.readline()
    
    def setOffsetExpand(self,i,x,j):
        """
        Sets output offsets (i) and expands(j). Offset parameter (x) is in percent (-105.00 <= x <= 105.00).  The range for j: 1 <= j <= 256.
        i = 1 (X)
          = 2 (Y)
          = 3 (R)
        """
        
        self.amp.write('oexp %s %s %s \n'%(i,x,j))
        return

    def getOffsetExpand(self):
        """
        Gets output offsets (i) and expands(j). Offset parameter (x) is in percent (-105.00 <= x <= 105.00).  The range for j: 1 <= j <= 256.  Returns offset and expand seperated by a comma (50.00,10 = Y offset 50.00%, Y expand 10).
        i = 1 (X)
          = 2 (Y)
          = 3 (R)
        """
        self.amp.write('oexp?\n')
        return elf.amp.readline()

    def zeroOffset(self,i):
        """
        Automatically sets X, Y, or R offset to zero.  Equivalent to pressing the Auto softkey in the Offset & Expand menu box.
        i = 1 (X)
          = 2 (Y)
          = 3 (R)
        """
        self.amp.write('aoff %s\n'%i)
        return


class TraceScan(SR850):
    """Trace and Scan Commands"""
    def setTraceDef(self,i,j,k,l,m):
        """Sets or queries the trace definitions.  
        i = trace number (1,2,3,4).
        Trace i is defined quantities (j*k/l)
        m = 1 (store trace)
          = 0 (don't store trace)
        Only l can be > 12.
        j, k, l  quantity  j, k, l  quantity
        -------  --------  -------  --------
        0          1         13        X^2
        1          X         14        Y^2
        2          Y         15        R^2
        3          R         16        theta^2
        4          theta     17        Xn^2
        5          Xn        18        Yn^2
        6          Yn        19        Rn^2
        7          Rn        20        Al1^2
        8          Al1       21        Al2^2
        9          Al2       22        Al3^2
        10         Al3       23        Al4^2
        11         Al4       24        F^2 
        12         F
        Ex: TraceScan().setTraceDef(1,1,2,3,1) = trace 1 as X*Y/R and stores trace 1
        """
        self.amp.write('trcd %s %s %s %s %s\n'%(i,j,k,l,m))
        return

    def getTraceDef(self):
        """Queries and returns trace definitions as a string i,j,k,l,m separated by commas.
        i = trace number (1,2,3,4)
        m = 1 (store trace)
          = 0 (don't store trace)
        j, k, l  quantity  j, k, l  quantity
        -------  --------  -------  --------
        0          1         13        X^2
        1          X         14        Y^2
        2          Y         15        R^2
        3          R         16        theta^2
        4          theta     17        Xn^2
        5          Xn        18        Yn^2
        6          Yn        19        Rn^2
        7          Rn        20        Al1^2
        8          Al1       21        Al2^2
        9          Al2       22        Al3^2
        10         Al3       23        Al4^2
        11         Al4       24        F^2 
        12         F
        """
        self.amp.write('trcd?\n')
        return self.amp.readline()

    def setScanRate(self,i):
        """
        Sets scan sample rate.
        i = 0 (62.5 mHz)
          = 1 (125 mHz)
          = 2 (250 mHz)
          = 3 (500 mHz)
          = 4 (1 Hz)
          = 5 (2 Hz)
          = 6 (4 Hz)
          = 7 (8 Hz)
          = 8 (16 Hz)
          = 9 (32 Hz)
          = 10 (64 Hz)
          = 11 (128 Hz)
          = 12 (256 Hz)
          = 13 (512 Hz)
          = 14 (Trigger)
        """
        self.amp.write('srat %s \n'%i)
        
        return
    
    def getScanRate(self):
        """
        Queries and reutrns scan sample rate.
        i = 0 (62.5 mHz)
          = 1 (125 mHz)
          = 2 (250 mHz)
          = 3 (500 mHz)
          = 4 (1 Hz)
          = 5 (2 Hz)
          = 6 (4 Hz)
          = 7 (8 Hz)
          = 8 (16 Hz)
          = 9 (32 Hz)
          = 10 (64 Hz)
          = 11 (128 Hz)
          = 12 (256 Hz)
          = 13 (512 Hz)
          = 14 (Trigger)
        """
        
        self.amp.write('srat?\n')
        return self.amp.readline()

    def setScanLength(self,x):
        """
        Sets scan length. x is real number of seconds.  
        Set to closest allowed time given sample rate and stored number of traces.  Max is buffer size / sample rate.  Min is 1.0 sec.
        """
        self.amp.write('slen %s \n'%x)
        return

    def getScanLength(self):
        """Queries and returns scan length in real number of seconds"""
        self.amp.write('slen?\n')
        return self.amp.readline()

    def setScanMode(self,i):
        """
        Sets scan mode.
        i = 0 (1 shot)
          = 1 (loop)
        """
        self.amp.write('send %s \n')
        return

    def getScanMode(self):
        """
        Queries and returns scan mode.
        Sets scan mode.
        i = 0 (1 shot)
          = 1 (loop)
        """
        self.amp.write('send?\n')
        return self.amp.readline()

    def trigger(self):
        """
        Software trigger command.  Equivalent to rear panel trigger input.
        """
        self.amp.write('trig\n')
        return

class DisplayScale(SR850):
    """Display and Scale Commands"""
    def autoscale(self):
        """Autoscales the active display (bar and chart displays)"""
        self.amp.write('ascl\n')
        return

    def setDisplay(self,i):
        """
        Selects active display.
        i = 0 (full)
          = 1 (top)
          = 2 (bottom)
        **NOTE: select display must be present otherwise error!
        """
        self.amp.write('adsp %s \n'%i)
        return
    
    def getDisplay(self):
        """
        Queries and returns active display.
        i = 0 (full)
          = 1 (top)
          = 2 (bottom)
        """
        self.amp.write('adsp?\n')
        return self.amp.readline()

    def setScreenFormat(self,i):
        """
        Sets screen format.
        i = 0 (single/full screen display)
          = 1 (up/down dual display
        """
        self.amp.write('smod %s \n'%i)
        return

    def getScreenFormat(self):
        """
        Queries and returns screen format.
        i = 0 (single/full screen display)
          = 1 (up/down dual display
        """
        self.amp.write('smod?\n')
        return self.amp.readline()

    def setMonitorDisplay(self,i):
        """
        Sets monitor display mode.
        i = 0 (settings monitor)
          = 1 (input/output monitor)
        """
        self.amp.write('mntr %s \n'%i)
        return

    def getMonitorDisplay(self):
        """
        Queries and returns monitor display mode.
         i = 0 (settings monitor)
           = 1 (input/output monitor)
        """
        self.amp.write('mntr?\n')
        return self.amp.readline()

    def setDisplayType(self,i,j):
        """
        Sets display type.
        i = display.
          = 0 (full)
          = 1 (top)
          = 2 (bottom)
        j = 0 (polar)
          = 1 (blank)
          = 2 (bar)
          = 3 (chart)
        **NOTE: if trying to set a display type of a display not on the screen, an error will result.
        """
        self.amp.write('dtyp %s %s \n'%(i,j))
        return

    def getDisplayType(self):
        """
        Queries and returns the display type.
        i = display.
          = 0 (full)
          = 1 (top)
          = 2 (bottom)
        j = 0 (polar)
          = 1 (blank)
          = 2 (bar)
          = 3 (chart)
        """
        self.amp.write('dtyp?\n')
        return self.amp.readline()

    def setDisplayRange(self,i,x):
        """
        Set display range. 
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        x = number of units of the displayed trace (10^(-18) to 10^(18)
        **NOTE: if trying to set range of a display not on the screen, an error will result.
        """
        self.amp.write('dscl %s %s \n'%(i,x))
        return
    
    def getDisplayRange(self):
        """
        Queries and returns the display range. 
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        x = number of units of the displayed trace
        """
        self.amp.write('dscl?\n')
        return self.amp.readline()

    def setDisplayCenter(self,i,x):
        """
        Sets display center value or offset of bar and chart display types. 
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        x = center value (real number with units of display trace (10^(-12) to 10^(12).
        **NOTE: if trying to set center value of a display not on the screen, an error will result.
        """
        self.amp.write('doff %s %s \n'%(i,x))
        return

    def getDisplayCenter(self):
        """
        Queries and returns display center value or offset.
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        x = center value (real number with units of display trace (10^(-12) to 10^(12).
        """
        self.amp.write('doff?\n')
        return self.amp.readline()

    def setHorizontalScale(self,i,j):
        """
        Sets display horizontal scale for chart display types.
        Minimum scale is (1/sample rate) per division for a minimum of 10 points on the chart. 
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        j = scale listed below.
        i   time/div    i     time/div
       ---  --------   ---    --------
        0     2 mS      17      200 S
        1     5 mS      18      5 min
        2     10 mS     19      500 S
        3     20 mS     20      10 min
        4     50 mS     21      1 kS
        5     0.1 S     22      20 min
        6     0.2 S     23      2 kS
        7     0.5 S     24      1 hour
        8     1.0 S     25      5 kS
        9     2.0 S     26      2 hour
        10    5.0 S     27      10 kS
        11    10 S      28      3 hour
        12    20 S      29      20 kS
        13    50 S      30      50 kS
        14    1 min     31      100 kS
        15    100 S     32      200 kS
        16    2 min
        """
        self.amp.write('dhzs %s %s \n'%(i,j))
        return

    def getHorizontalScale(self):
        """
        Queries and returns display horizontal scale.
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        j = scale listed below.
        i   time/div    i     time/div
       ---  --------   ---    --------
        0     2 mS      17      200 S
        1     5 mS      18      5 min
        2     10 mS     19      500 S
        3     20 mS     20      10 min
        4     50 mS     21      1 kS
        5     0.1 S     22      20 min
        6     0.2 S     23      2 kS
        7     0.5 S     24      1 hour
        8     1.0 S     25      5 kS
        9     2.0 S     26      2 hour
        10    5.0 S     27      10 kS
        11    10 S      28      3 hour
        12    20 S      29      20 kS
        13    50 S      30      50 kS
        14    1 min     31      100 kS
        15    100 S     32      200 kS
        16    2 min
        """
        self.amp.write('dhzs?\n')
        return self.amp.readline()

    def getBinNumber(self,i):
        """
        Queries and returns the bin number at the right edge of the chart display:
        i = display.
          = 0 (full) 
          = 1 (top)
          = 2 (bottom)
        Chart display must be selected (see DisplayScale().setDisplayType())
        """
        self.amp.write('rbin? %s \n'%i)
        return self.amp.readline()
        
class Cursor(SR850):
    """Cursor commands"""
    def setSeekMode(self,i):
        """
        Sets cursor seek mode of active display
        i = 0 (Max)
          = 1 (Min)
          = 2 (Mean)
        Each display has it's own cursor seek mode. Only chart has a cursor.
        """
        self.amp.write('csek %s\n'%i)
        return
    
    def getSeekMode(self):
        """
        Queries and returns cursor seek mode.
        i = 0 (Max)
          = 1 (Min)
          = 2 (Mean)
        """
        self.amp.write('csek?\n')
        return self.amp.readline()

    def setWidth(self,i):
        """
        Sets cursor width of active display.
        i = 0 (off)
          = 1 (narrow)
          = 2 (wide)
          = 3 (spot)
        Each display has it's own cursor width. Only chart has a cursor.
        """
        self.amp.write('cwid %s \n'%i)
        return

    def getWidth(self):
        """
        Queries and returns cursor width of active display.
        i = 0 (off)
          = 1 (narrow)
          = 2 (wide)
          = 3 (spot)
        """
        self.amp.write('cwid?\n')
        return self.amp.readline()
    
    def setVerticalDiv(self,i):
        """
        Sets vertical divisions of the active display.
        i = 0 (8)
          = 1 (10)
          = 2 (None)
        Each display has it's own vertical division mode. Only affetcs charts.
        """
        self.amp.write('cdiv %s \n'%i)
        return

    def getVerticalDiv(self):
        """
        Queries and returns vertical divisions of the active display.
        i = 0 (8)
          = 1 (10)
          = 2 (None)
        """
        self.amp.write('cdiv?\n')
        return self.amp.readline()

    def setControlMode(self,i):
        """
        Sets control mode of cursor.
        i = 0 (linked)
          = 1 (separate)
        Only charts have cursors.
        """
        self.amp.write('clnk %s \n'%i)
        return

    def getControlMode(self):
        """
        Queries and returns cursor control mode.
        i = 0 (linked)
          = 1 (separate)
        """
        self.amp.write('clnk?\n')
        return self.amp.readline()

    def setReadoutMode(self,i):
        """
        Sets cursor readout mode of the active display.  
        i = 0 (delay)
          = 1 (bin)
          = 2 (fsweep)
          = 3 (time)
        Only charts have cursors.
        """ 
        self.amp.write('cdsp %s \n'%i)
        return

    def getReadoutMode(self):
        """
        Queries and returns cursor readout mode of the active display.  
        i = 0 (delay)
          = 1 (bin)
          = 2 (fsweep)
          = 3 (time)
        """ 
        self.amp.write('cdsp?\n')
        return self.amp.readline()

    def setMinMax(self):
        """
        Like pressing the CURSOR MAX/MIN key.
        Cursor will move to the max or min of the data (set by Cursor(). setSeekMode()).
        Only for chart display.
        """
        self.amp.write('cmax\n')
        return

    def getPosition(self,i):
        """
        Queries and returns cursor position of desired chart display (i).
        i = 0 (full)
          = 1 (top)
          = 2 (bottom)
        Only for chart display.
        Returned as X,Y pair spearated by a comma.
        First number = horizontal position (bin, delay, time, or sweep frequency)
        Second number = vertical position.
        """
        self.amp.write('curs? %s \n'%i)
        return self.amp.readline()

    def setBinPosition(self,i):
        """
        Sets cursor bin position of active chart display.
        Only for chart display.
        Bin at the center of the cursor region, not cursor readout position (which selects min, max, or mean of data within cursor region.)
        Moves the cursor to bin i.
        If bin i is outside the time window of the chart, the chart is panned left or right until it reaches an edge.
        **NOTE: This is the center of the cursor REGION.  Cursor().getPosition() queries the actual cursor position.
        """
        self.amp.write('cbin %s \n'%i)
        return

    def getBinPosition(self):
        """
        Queries and returns the cursor bin position of the active display.
        **NOTE: This is the center of the cursor REGION.  Cursor().getPosition() queries the actual cursor position.
        """
        self.amp.write('cbin?\n')
        return self.amp.readline()
      
class Mark(SR850):  
    """Mark Commands"""
    def mark(self):
        """ 
        Like pressing the MARK key.  A mark is placed in the data buffer at the next sample  Only has an effect when scan is in progress.
        """
        self.amp.write('mark\n')
        return
    
    def nextRightMark(self):
        """
        Moves the cursor to the next mark to the right. If mark is off the right edge, then display is panned right until the next mark is found.
        """
        self.amp.write('cnxt\n')
        return
    
    def nextLeftMark(self):
        """
        Moves the cursor to the next mark to the left. If mark is off the left edge, then display is panned left until the next mark is found.
        """
        self.amp.write('cprv\n')
        return

    def markerDelete(self):
        """
        Like pressing the Marker Delete softkey.  Deletes the nearest marker to the left of the cursor.
        """
        self.amp.write('mdel\n')
        return

    def getMarkNum(self):
        """
        Queries and returns the number of active marks (0-8).   If greater than 0, then number of marks is followed by active mark numbers, separated by commas.
        """
        self.amp.write('mact?\n')
        return
    
    def getMarkBin(self, i):
        """
        Queries and reutrns the bin number of mark i.  All displays use the same marks.  If mark i is not active, an error is reutrned. 
        """
        self.amp.write('mbin? %s \n'%i)
        markBin = self.amp.readline()
        if int(markBin) == -1:
            print('ERROR: mark %s is not active!' %i)
            exit()
        else:
            return markBin
        
    def setMarkLabel(self,i,s):
        """
        Sets label field for mark i.  All displays use the same marks.
        i must be an active mark (0-7).
        Use Mark().getMarkNum() to find active marks.
        if s chosen, sets the mark label to string s (do not use spaces!).
        """
            #!! set options if s not chosen.  convert s to a string!
        self.amp.write('mtxt %s %s \n'%(i,s))
        return
        
    def getMarks(self):
        """
        Returns which marks are active.
        """
        self.amp.write('mtxt?\n')
        return self.amp.readline()

    def getMarkLabel(self,i):
        """
        Queries and returns field label for mark i.  
        Default label is date and time.
        """
        self.amp.write('mtxt? %s \n')
        return self.amp.readline()

            
class AuxIO(SR850):
    """AUX Input and Output Commands"""
    def getInput(self,i):
        """
        Queries Aux input values.  Selects Aux input and returns voltage (V).  Resolutoin is 1/3 mV.
        i = Aux input (1, 2, 3, 4)
        """
        self.amp.write('oaux? %s\n'%i)
        return

    def setOutput(self,i,j):
        """
        Sets Aux output mode.  Aux output i is required.  
        i = Aux output (1,2,3,4)
        j = 0 (fixed)
          = 1 (sweep)
          = 2 (linear sweep)
        """
        self.amp.write('auxm %s %s \n'%(i,j))
        return
    
    def getOutput(self,i):
        """
        Queries and returns Aux output mode for Aux output i.
        i = Aux output (1,2,3,4).
        j = 0 (fixed)
          = 1 (sweep)
          = 2 (linear sweep)
        """
        self.amp.write('auxm? %s \n'%i)
        return self.amp.readline()
    
    def setOutputVoltage(self,i,x):
        """
        Sets Aux output voltage when output is in fixed mode (see AuxIO().setOutput)).
        i = output (1,2,3,4)
        x = output voltage (real number of Volts, set to nearest mV). -10.500 <= x <= 10.500.
        **NOTE: error if selects an output set to sweep.
        """
        self.amp.write('auxv %s %s \n'%(i,x))
        return

    def getOutputVoltage(self,i):
        """
        Queries and returns Aux output voltage (in Volts, to nearest mV) when output is in fixed voltage mode.
        i = Aux output (1,2,3,4)
        **NOTE: error if selects an output set to sweep.
        """
        self.amp.write('auxv? %s \n'%i)
        return self.amp.readline()

    def setOutputSweep(self,i,x,y,z):
        """
        Sets Aux output sweep limits and offsets.
        i = Aux output (1,2,3,4)
        x = sweep start voltage
        y = sweep stop voltage
        z = sweep offset voltage
        x, y, and z in real Volts to nearest mV (0.001<=x,y<=21.00, -10.500<=z<=10.500)
        **NOTE: error if selects an output set to fixed (see AuxIO().setOutput())
        """
        self.amp.write('saux %s %s %s %s \n'%(i,x,y,z))
        return
 
    def getOutputSweep(self,i):
        """
        Queries and returns Aux output sweep limits and offsets.
        i = Aux output (1,2,3,4)
        Returns x,y,z separated by commas.
        x = sweep start voltage
        y = sweep stop voltage
        z = sweep offset voltage
        x, y, and z in real Volts to nearest mV (0.001<=x,y<=21.00, -10.500<=z<=10.500)
        **NOTE: error if selects an output set to fixed (see AuxIO().setOutput())
        """
        self.amp.write('saux? %s \n'%i)
        return self.amp.readline()
    
    def setTriggerStart(self,i):
        """
        Sets trigger start scan mode.
        i = 0 (no)
          = 1 (yes)
        """
        self.amp.write('tstr %s \n'%i)
        return

    def getTriggerStart(self):
        """
        Queries and returns trigger start scan mode.
        i = 0 (no)
          = 1 (yes)
        """
        self.amp.write('tstr?\n')
        return self.amp.readline()

class Math(SR850):
    """Math Commands"""
    def smooth(self,i):
        """
        Smooths the data trace of the active display.
         i    smoothing width
        ---  -----------------
         0        5 points
         1        11 points
         2        17 points
         3        21 points
         4        25 points
        if a scan is in progress, this command will pause the scan.
        """
        #!! use status byte query to detect when smoothing operation is done--test..
        status = '0'
        while status != '1':
            self.amp.write('smth %s \n'%i)
            status = Status().getStatus().rstrip()
        # CHECK FOR ERRORS
        return 

    def setType(self,i): 
       """
       Sets the type of math operation.
        i    operation
       ---  -----------
       0        +
       1        -
       2        j
       3        /
       4        sin
       5        cos
       6        tan
       7        sqrt(x)
       8        x^2
       9        log
       10       10^x
       """
       self.amp.write('copr %s \n'%i)
       return
       
    def getType(self):
        """
        Queries and returns the type of math operation.
         i    operation
        ---  -----------
         0        +
         1        -
         2        j
         3        /
         4        sin
         5        cos
         6        tan
         7        sqrt(x)
         8        x^2
         9        log
         10       10^x
        """
        self.amp.write('copr?\n')
        return self.amp.readline()

    def calc(self):
        """
        Starts the calculation selected by Math().setType(). Make sure that Math().setArgType() and Math(). have been used to set the argument if required by the operation defined in Math().setType().  If a scan is in progress, this command will pause the scan.
        """
        self.amp.write('calc\n')
        #!! use status byte command to detect when done
        return

    def setArgType(self,i):
        """
        Sets argument type.
        i = 0 (Trace)
          = 1 (Constant)
        """
        self.amp.write('cagt %s \n'%i)
        return
        
    def getArgType(self):
        """
        Queries and returns the argument type.
         i = 0 (Trace)
          = 1 (Constant)
        """
        self.amp.write('cagt?\n')
        return self.amp.readline()
        
    def setTraceArgNum(self,i):
        """
        Sets the trace argument number.  Choose trace i = 1,2,3, or 4.
        """
        self.amp.write('ctrc %s \n'%i)
        return

    def getTraceArgNum(self):
        """
        Queries and returns trace argument number (1,2,3 or 4).
        """
        self.amp.write('ctrc?\n')
        return self.amp.readline()

    def setConstArg(self,x):
        """
        Sets the constant argument value, where x is a real number.
        """
        self.amp.write('carg %s \n'%x)
        return

    def getConstArg(self):
        """
        Queries and reutrns the constant argument value (real number).
        """
        self.amp.write('carg?\n')
        return self.amp.readline()

    def setFit(self,i):
        """
        Sets the type of fit.
        i = 0 (line)
          = 1 (exponential)
          = 2 (Gaussian)
        """
        self.amp.write('ftyp %s \n'%i)
        return

    def getFit(self):
        """
        Queries and returns the type of fit.
        i = 0 (line)
          = 1 (exponential)
          = 2 (Gaussian)
        """
        self.amp.write('ftyp?\n')
        return

    def startFit(self,i,j):
        """
        Starts fitting calculations.  Fit occurs within chart region defined as i% and j% (integer percentages) from the left edge. If a scan is in progress, this command will pause the scan.
        """
        if i < j:
            print('ERROR: j must be greater than i')
            exit()
        elif type(j) != int or type(i) != int:
            print('ERROR: i and j must be integers.')
            exit()
        self.amp.write('fitt %s %s \n'%(i,j))
        #!! use status byte query to detect when smoothing operation is done

        return

    def getParameters(self,i):
        """
        Queries and returns the fit parameters a, b, c, and t0 after a curve fit has been performed.  
        i = 0 (a)
          = 1 (b)
          = 2 (c)
          = 3 (t0)
        Line fit: y = a + b*(t- t0)
        Exp. fit: y = a*e^(-(t-t0)/b) + c
        Gauss. fit: y = a*e^(-1/2( t/b)^2) + c where t = t - t0
        
        **NOTE: If no fit has been done or the parameter is unused in the fit, invalid data is returned.
        """
        self.amp.write('pars? %s \n'%i)
        return self.amp.readline()

    def startStats(self,i,j):
        """
        Starts the statistics calculations.  Only data within chart region defined as i% and j% (integer percentages) from the left edge are analyzed.  
        If a scan is in progress, this command will pause the scan.
        """
        if j < i:
            print('ERROR: j must be greater than i')
            exit()
        elif type(j) != int or type(i) != int:
            print('ERROR: i and j must be integers.')
            exit()
        self.amp.write('stat %s %s \n'%(i,j))
        #!! use status byte query to detect when smoothing operation is done        
        return

    def getStats(self,i):
        """
        Queries and returns the results of a stastical calculation.
        i = 0 (mean)
          = 1 (standard deviation)
          = 2 (total data)
          = 3 (delta time)
        **NOTE: If no analysis has been done, invalid data is reutnred.
        """
        self.amp.write('spar? %s \n'%i)
        return self.amp.readline()


class File(SR850):
    """
    Store and Recall File Commands.
    Use File().setFilename() before any other file operation commands.
    """
    def setFilename(self,filename):
        """
        Sets the active filename.  Use this command before any file operations.
        Files will be aed to root directory.  Use 8 characters or less, with an optional extra 3 characters. Example: File().setFilename('mydata.dat').
        """
        self.amp.write('fnam %s \n'%filename)
        return

    def getFilename(self):
        """
        Queries and returns the active filename.
        """
        self.amp.write('fnam?\n')
        return self.amp.readline()

    def saveTrace(self):
        """
        Saves active display's data trace to filename specified by File().setFilename().
        """
        self.amp.write('sdat\n')
        #! check error status byte ERRS?
        print(Status().getErrorByte())
        return

    def saveTraceASCII(self):
        """
        Saves active display's data trace in ascii format to filename specified by File().setFilename().
        """
        self.amp.write('sasc\n')
        #! check error status byte ERRS?
        print(Status().getErrorByte())
        return

    def saveSetup(self):
        """
        Saves instrument setup to the filename specified by File().setFilename().
        """
        self.amp.write('sset\n')
        #! check error status byte ERRS?
        print(Status().getErrorByte())
        return
        
    def getData(self):
        """
        Recall trace data, trace definition, and instrument state from the file specified by File().setFilename() command.  Data is stored in the active display's trace.
        """
        self.amp.write('rdat\n')
        #! check error status byte ERRS?
        print(Status().getErrorByte())
        return
        
    def getSetup(self):
        """
        Recalls instrument setup from the file specified by the File().setFilename command.
        """
        self.amp.write('rset\n')
        #! check error status byte ERRS?
        print(Status().getErrorByte())
        return

class Setup(SR850):
    """Setup Commands"""
    def setInterface(self,i):
        """
        Sets the output interface to:
        i = 0 (RS232)
          = 1 (GPIB)
        **NOTE: The interface must be set before any commands are sent!
        """
        self.amp.write('OUTX %s \n'%i)
        return

    def getInterface(self):
        """
        Queries and returns the output interface:
        i = 0 (RS232)
          = 1 (GPIB)
        """
        self.amp.write('OUTX?\n')
        return self.amp.readline()

    def setOverideRemote(self,i):
        """
        Sets the GPIB Overide Remote Yes/No condition.
        i = 0 (No)
          = 1 (Yes)
        """
        self.amp.write('ovrm %s \n'%i)
        return

    def getOverideRemote(self):
        """
        Queries and returns the GPIB Overide Remote Yes/No condition.
        i = 0 (No)
          = 1 (Yes)
        """
        self.amp.write('ovrm?\n')
        return self.amp.readline()

    def setClick(self,i):
        """
        Sets the key click:
        i = 0 (Off)
          = 1 (On)
        """
        self.amp.write('kclk %s \n'%i)
        return
        
    def getClick(self):
        """
        Queries and returns the key click:
        i = 0 (Off)
          = 1 (On)
        """
        self.amp.write('kclk?\n')
        return self.amp.readline()

    def setAlarm(self,i):
        """
        Sets the alarms state:
        i = 0 (Off)
          = 1 (On)
        """
        self.amp.write('alrm %s \n'%i)
        return

    def getAlarm(self):
        """
        Queries and returns the alarm state:
         i = 0 (Off)
          = 1 (On)
        """
        self.amp.write('alrm\n')
        return self.amp.readline()

    def setClockHrs(self,i):
        """
        Sets the hours setting of the clock (i = 0 to 23).
        """
        if i < 0 or i > 23:
            print('ERROR: hours must be between 0 and 23')
            exit()
        if type(i) != int:
            print('ERROR: must use an integer value for hours setting.')
            exit()

        self.amp.write('thrs %s \n'%i)
        return

    def getClockHrs(self):
        """
        Queries and returns the hours setting of the clock.
        """
        self.amp.write('thrs?\n')
        return self.amp.readline()

    def setClockMin(self,i):
        """
        Sets the minutes setting of the clock (i = 0 to 59).
        """
        if i < 0 or i > 59:
            print('ERROR: minutes must be between 0 and 59')
            exit()
        if type(i) != int:
            print('ERROR: must use an integer value for minute setting.')
            exit()

        self.amp.write('tmin %s \n'%i)
        return

    def getClockMin(self):
        """
        Queries and returns the minutes setting of the clock.
        """
        self.amp.write('tmin?\n')
        return self.amp.readline()

    def setClockSec(self,i):
        """
        Sets the seconss setting of the clock (i = 0 to 59).
        """
        if i < 0 or i > 59:
            print('ERROR: hours must be between 0 and 59')
            exit()
        if type(i) != int:
            print('ERROR: must use an integer value for seconds setting.')
            exit()

        self.amp.write('tsec %s \n'%i)
        return

    def getClockSec(self):
        """
        Queries and returns the seconds setting of the clock.
        """
        self.amp.write('tsec?\n')
        return self.amp.readline()

    def setMonth(self):
        """
        Sets the months setting of the calender (i = 1 to 12):
        """
        if i < 1 or i > 12:
            print('ERROR: months must be between 1 and 12')
            exit()
        if type(i) != int:
            print('ERROR: must use an integer value for months setting.')
            exit()

        self.amp.write('dmth %s \n'%i)
        return
        
    def getMonth(self):
        """
        Queries and reutrns the months setting of the calendar.
        """
        self.amp.write('dmth?\n')
        return self.amp.readline()
        
    def setDay(self):
        """
        Sets the day setting of the calender (i = 1 to 31):
        """
        if i < 1 or i > 31:
            print('ERROR: days must be between 1 and 31')
            exit()
        if type(i) != int:
            print('ERROR: must use an integer value for days setting.')
            exit()

        self.amp.write('dday %s \n'%i)
        return
        
    def getDay(self):
        """
        Queries and reutrns the days setting of the calendar.
        """
        self.amp.write('dday?\n')
        return self.amp.readline()

    def setYear(self):
        """
        Sets the year setting of the calender (i = 0 to 99):
        """
        if i < 0 or i > 99:
            print('ERROR: years must be between 0 and 99')
            exit()
        if type(i) != int:
            print('ERROR: must use an integer value for years setting.')
            exit()

        self.amp.write('dyrs %s \n'%i)
        return
        
    def getYear(self):
        """
        Queries and reutrns the year setting of the calendar.
        """
        self.amp.write('dyrs?\n')
        return self.amp.readline()

    def setPlotMode(self,i):
        """
        Sets the plotter mode.  
        i = 0 (plotting to rs232 interface)
          = 1 (plotting to gpib interface)
        """
        self.amp.write('pltm %s \n'%i)
        return

    def getPlotMode(self):
        """
        Queries and returns the plotter mode.
        i = 0 (plotting to rs232 interface)
          = 1 (plotting to gpib interface)
        """
        self.amp.write('pltm? \n')
        return self.amp.readline()

    def setPlotBaud(self,i):
        """
        Sets the RS232 plotter baud rate.
        i = 0 (300)
          = 1 (1200)
          = 2 (2400)
          = 3 (4800)
          = 4 (9600)
        This should match the baudrate of the plotter in use.
        """
        self.amp.write('pltb %s \n'%i)
        return
        
    def getPlotBaud(self):
        """
        Queries and returns the RS232 plotter baud rate.
        i = 0 (300)
          = 1 (1200)
          = 2 (2400)
          = 3 (4800)
          = 4 (9600)
        """
        self.amp.write('pltb?\n')
        return self.amp.readline()

    def setPlotAddress(self,i):
        """
        Sets the GPIB plotter address.  i = 0 to 30, and should agree with plotter in use.
        """
        if i < 0 or i > 30:
            print('ERROR: plotter address must be between 0 and 30.')
            exit()
        self.amp.write('plta %s \n'%i)
        return

    def getPlotAddress(self):
        """
        Queries and returns the GPIB plotter address.
        """
        self.amp.write('plta?\n')
        return self.amp.readline()
        
    def setPlotSpeed(self,i):
        """
        Sets the plot speed. 
        i = 0 (fast)
          = 1 (slow)
        """
        self.amp.write('plts %s \n'%i)
        return

    def getPlotSpeed(self):
        """
        Queries and returns the plot speed.
        i = 0 (fast)
          = 1 (slow)
        """
        self.amp.write('plts?\n')
        return self.amp.readline()
    
    def setTracePenNum(self,i):
        """
        Sets the trace pen number (i = 1 to 6).
        """
        if i < 0 or i > 6:
            print('ERROR: pen number must be between 0 and 6')
            exit()
        self.amp.write('pntr %s \n'%i)
        return

    def getTracePenNum(self):
        """
        Queries and returns the trace pen number.
        """
        self.amp.write('pntr?\n')
        return self.amp.readline()

    def setGridPenNum(self,i):
        """
        Sets the grid pen number (i = 1 to 6).
        """
        if i < 0 or i > 6:
            print('ERROR: grid number must be between 0 and 6')
            exit()
        self.amp.write('pngd %s \n'%i)
        return

    def getGridPenNum(self):
        """
        Queries and returns the grid pen number.
        """
        self.amp.write('pngd?\n')
        return self.amp.readline()    

    def setAlphaPenNum(self,i):
        """
        Sets the alphanumeric pen number (i = 1 to 6).
        """
        if i < 0 or i > 6:
            print('ERROR: pen number must be between 0 and 6')
            exit()
        self.amp.write('pnal %s \n'%i)
        return

    def getAlphaPenNum(self):
        """
        Queries and returns the alphanumeric pen number.
        """
        self.amp.write('pnal?\n')
        return self.amp.readline()
        
    def setCursorPenNum(self,i):
        """
        Sets the cursor pen number (i = 1 to 6).
        """
        if i < 0 or i > 6:
            print('ERROR: pen number must be between 0 and 6')
            exit()
        self.amp.write('pncr %s \n'%i)
        return

    def getCursorPenNum(self):
        """
        Queries and returns the cursor pen number.
        """
        self.amp.write('pncr?\n')
        return self.amp.readline()
        
    
class PrintPlot(SR850):
    """Print and Plot Commands"""

              
    def setPrinterType(self,i):
        """
        Sets the printer type.
        i = 0 (EPSON)
          = 1 (HP)
          = 2 (File)
        """
        self.amp.write('prnt %s \n'%i)
        return

    def getPrinterType(self):
        """
        Queries and returns the printer type.
        i = 0 (EPSON)
          = 1 (HP)
          = 2 (File)
        """
        self.amp.write('prnt? \n')
        return self.amp.readline()

    def printDisplay(self):
        """
        Prints the screen display to a printer attached to the rear panel parallel printer port, defined by PrintPlot().setPrinterType().
        """
        self.amp.write('prsc\n')
        return

    def plotDataDisplays(self):
        """
        Plot the data displays.  Each feature uses the pen assigned in the Setup() plotter menu.
        """
        self.amp.write('pall\n')
        return

    def plotTraces(self):
        """
        Plot only traces.
        """
        self.amp.write('ptrc\n')
        return

    def plotCursor(self):
        """
        Plot only cursors, if they ar eon.
        """
        self.amp.write('pcur\n')
        return
       
class FrontPanel(SR850):
    """Front Panel Controls"""
    def start(self):
        """Starts or resumes a scan: [START/CONT] key."""
        self.amp.write('strt\n')
        return

    def pause(self):
        """
        Pauses a scan.  All sweeps in progress also pause.  Ignored if scan is already paused, stopped, or done.
        """
        self.amp.write('paus\n')
        return

    def reset(self):
        """
        Resets a scan.  
        **NOTE: this command will erase the data buffer and reset all swept parameters to their start value.
        """
        self.amp.write('rest\n')
        return

    def setDisplay(self,i):
        """
        Selects the active display.
        i = 0 (top)
          = 1 (bottom)
        If the display is full screen, it is always the active display.
        """
        self.amp.write('atrc %s \n'%i)
        return

    def getDisplay(self):
        """
        Queries and returns the active display.
        i = 0 (top)
          = 1 (bottom)
        """
        self.amp.write('atrc?\n')
        return

    def autoScale(self):
        """
        Autoscales the active display (bar/chart displays only): [AUTO SCALE] key.
        """
        self.amp.write('ascl\n')
        return

    def autoGain(self):
        """
        Performs the Auto Gain function: [AUTO GAIN] key.  
        """
        self.amp.write('agan\n')
        #! check serial poll status byte (bit 1) to determine when function is finished!
        return
        
    def autoReserve(self):
        """
        Performs the Auto Reserve function: [AUTO RESERVE] key.
        """
        self.amp.write('arsv\n')
        #! check serial poll status byte (bit 1) to determine when function is finished!
        return

    def autoPhase(self):
        """
        Performs the Auto Phase function: [AUTO PHASE] key.
        The outputs will take many time constants to reach their new values.  Don't send this command again without waiting an adequate amount of time.
        """
        self.amp.write('aphs\n')
        return

    def autoOffset(self,i):
        """
        Automatically offsets dimension X, Y, or R to zero.
        i = 1 (X)
          = 2 (Y)
          = 3 (R)
        Equivalent to "Auto" key in the "Offset & Expand" menu box.
        """
        self.amp.write('aoff %s \n'%i)
        return

    def cursorMax(self):
        """
        Cursor will move to the max or min of the data as set by Cursor().setSeekMode().  Equivalent to [CURSOR MAX/MIN] key.  Only good for charts.
        """
        self.amp.write('cmax\n')
        return

class DataTransfer(SR850):
    """Data Transfer Commands"""
    def readParameter(self,i):#,avgs,waittime):
        """
        Reads the value of X, Y, R, or theta.
        i = 1 (X)
          = 2 (Y)
          = 3 (R)
          = 4 (theta)
        Values are returned as ASCII floating point numbers with units of Volts or degrees.
        """

        self.amp.write('OUTP?%s\n'%i)
    
        str = ""
        while 1:
            ch = self.amp.read()
            if(ch == '\r' or ch == ''):
                break
            str+=ch
        return str

    def readTraceValue(self,i):
        """
        Reads the value of trace i = 1,2,3 or 4.  Returned as ASCII floating point numbers with units of the trace (as displayed on the bar graph).
        """
        self.amp.write('OUTR?%s\n'%i)
        return self.amp.readline()
    
    def readAuxValues(self,i):
        """
        Reads Aux Input i = 1, 2 3, or 4.  Returned as ASCII strings with units of volts.  Resolution is 1/3 mV.
        """
        self.amp.write('OAUX?%s\n'%i)
        return self.amp.readline()

    def readMultiParameters(self,i,j,*args, **kwargs):
        """Records the values of 2-6 parameters at a single instant.  For example, query X and Y or R and theta at the same time.  Requires at least two parameters.
        i,j,k,l,m,n      parameter
            1                X
            2                Y
            3                R
            4                theta
            5                Aux In 1
            6                Aux In 2
            7                Aux In 3
            8                Aux In 4
            9                Reference Frequency
            10               Trace 1
            11               Trace 2
            12               Trace 3
            13               Trace 4
        """
        params= str(i)+','+str(j)
        for ar in args:
            params += (','+ar)
        self.amp.write('snap?%s\n'%params)
        return self.amp.readline()
            
class Interface(SR850):
    """Interface Commands"""
    
    def defaults(self):
        """
        Resets SR850 to default configurations.  Communication setup is not changed.  Allow adequate time to complete.
        """
        self.amp.write('*RST\n')
        return
        
    def setLocalRemote(self,i):
        """
        Sets the local/remote function.
        i = 0 (local)
          = 1 (remote)
          = 2 (local lockout)
        In local state, both command execution and keyboard input are allowed.
        In remote state, command execution is allowed, but keyboard and know are locked out, except fot he [HELP] key which returns the SR850 to the LOCAL state.  
        In local lockout state, all front panel operations are locked out, including the [HELP] key.
        Indicator is at the bottom of the spring.
        """
        self.amp.write('locl %s \n'%i)
        return

    def getLocalRemote(self):
        """
        Queries and returns the local/remote function.
        i = 0 (local)
          = 1 (remote)
          = 2 (local lockout)
        """
        self.amp.write('locl?\n')
        return self.amp.readline()

    def setGPIBOveride(self,i):
        """
        Sets the GPIB overide remote Yes/No condition.
        i = 0 (no)
          = 1 (yes)
        Yes: front panel if not locked out when the unit is in the remote state.  The REM indicator will still be on and the [HELP] key will still return the unit to the Local state.
        """
        self.amp.write('ovrm %s \n'%i)
        return
    
    def getGPIBOveride(self):
        """
        Queries and returns the GPIB overide remote Yes/No condition.
        i = 0 (no)
          = 1 (yes)
        """
        self.amp.write('ovrm?\n')
        return self.amp.readline()

    def trigger(self):
        """
        Software trigger command.  Same effect as a trigger at the rear panel trigger input.
        """
        self.amp.write('trig \n')
        return
        
        
class Status(SR850):
    """Status Reporting Commands"""
    def getStatus(self):
        """
        Queries and returns the value of the standard event status byte.  Returned as decimal from 0 to 255.
        """
        self.amp.write('*ESR?\n')
        return self.amp.readline()

    def getStatusBit(self,i):
        """
        Queries and returns the value (0 or 1) of bit i (0-7).
        """
        self.amp.write('*ESR? %s \n'%i)
        return self.amp.readline()

    
    def getErrorByte(self):
        """
        Queries and returns the value of the error status byte.  Returned as a decimal fro 0 to 255.
        """
        self.amp.write('errs?\n')
        return self.amp.readline()

    def getErrorBit(self,i):
        """
        Queries and returns the value (0 or 1) of bit i (0-7).
        """
        self.amp.write('errs? %s \n'%i)
        return self.amp.readline()
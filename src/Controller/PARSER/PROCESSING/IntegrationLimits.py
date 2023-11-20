import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RangeSlider

def GetLimits(Waveform):
    # As input: Waveform = np.array([time],[Voltage]), recommended to use averaged.
    # Opens a graphical interface to choose the signal area and offset.
    
    # Create an array for the offset.
    offset = np.array(Waveform[1])*0
    
    fig, ax = plt.subplots()
    
    plt.subplots_adjust(left=0.25, bottom=0.25) # Make space for the sliders
    
    # Plot Waveform and offset line
    ax.plot(Waveform[0],Waveform[1])
    line, = ax.plot(Waveform[0],offset)
    
    # Set the starting t limits to fit the full dataset
    tlims = [Waveform[0][0], Waveform[0][-1]]
    ax.set_xlim(*tlims)
    
    # Create a plt.axes object to hold the slider [left,bottom,width,height]
    Trange_ax = plt.axes([0.2, 0.12, 0.65, 0.05])
    offset_ax = plt.axes([0.1, 0.25, 0.04, 0.63])
    
    # Add slider to adjust 
    TRange_Slider = RangeSlider(Trange_ax, "Signal area", valmin = Waveform[0][0], valmax = Waveform[0][-1])
    
    # Add slider to adjust offset
    maxV = max(abs(Waveform[1]))
    offset_Slider = Slider(offset_ax, "Offset", valmin = -0.4*maxV, valmax = 0.4*maxV, valinit=0.0,orientation ="vertical")
    
    # Define functions to run whenever the slider changes its value and change graph accordingly.
    def offsetupdate(val):
        line.set_ydata(val)
        fig.canvas.draw_idle()
    
    def rangeupdate(val):
        tlims = [val[0],val[1]]
        ax.set_xlim(*tlims)
        fig.canvas.draw_idle()
    
    # Register the function update to run when the slider changes value
    TRange_Slider.on_changed(rangeupdate)
    offset_Slider.on_changed(offsetupdate)
    
    plt.show()

    # Return timerange and offset
    return TRange_Slider.val, offset_Slider.val
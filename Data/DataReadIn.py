from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import pandas as pd
import os

#Slightly cleaning the CSV data and testing values. Still needs to be updated such that no manual work needs to be done.
def displayCSVData(file):
    #Read in the CSV file and remove uneccessary columns first.
    motiveDF = pd.read_csv(file)
    motiveDF = motiveDF.loc[:, ~motiveDF.columns.str.contains('^Unnamed')]
    
    return motiveDF


#Create a class of marker objects.
class Marker:
    def __init__ (self, listx, listy, listz):
        self.x = listx 
        self.y = listy 
        self.z = listz 


#Visualization of multiple markers in a 3D setting.
def visualization(df, file):
    #Create a marker dataframe which only includes columns with marker positions (+rotations, error, etc.).
    markerDF = df.drop(['Frame', 'Time'], axis=1)


    #Create a marker list holding multiple marker objects with x, y, and z colums each.
    MarkerList = []
    for x in range(int((markerDF.shape[1])/4)):
        MarkerList.append(Marker(markerDF.iloc[:, (4*x)], markerDF.iloc[:, ((4*x)+1)], markerDF.iloc[:, ((4*x)+2)]))

    print(f"Number of markers is {len(MarkerList)}")


    #Create the figure and axes.
    figure = plt.figure()
    axes = figure.add_subplot(111, projection='3d')

    #Set the figure's limits (find min and max values for each axis).
    #First, find min and max values for the x, y, and z of each marker. THEN, find the min and max between the x, y, and z's of the marker objects.
    #However, currently manually setting the min and max values. Will be changed soon.
    axes.set_xlim(-1, 2)
    axes.set_ylim(-1, 2)
    axes.set_zlim(-1, 2)


    #x, y, and z initial points from each marker, aka an array of n values for each axis from frame 0.
    initializedX = [item.x[0] for item in MarkerList]
    initializedY = [item.y[0] for item in MarkerList]
    initializedZ = [item.z[0] for item in MarkerList]


    #Set point = beginning x, y, and z positions, then create text to display frame and timestamp in the 3D figure.
    point, = axes.plot(initializedX, initializedY, initializedZ, 'bo', markersize=10)
    text = axes.text2D(0, 0.9, '', transform=axes.transAxes, fontsize=12, verticalalignment='top')


    #Initialize the figure with initial values and empty text.
    def init():
        point.set_data(initializedX, initializedY)
        point.set_3d_properties(initializedZ)
        text.set_text('')
        return point,


    #Update the figure with the next row of data from the marker object list.
    def update(frame):
        new_x = [item.x[frame] for item in MarkerList]
        new_y = [item.y[frame] for item in MarkerList]
        new_z = [item.z[frame] for item in MarkerList]
        time = df['Time'][frame]
        frame = df['Frame'][frame]
        
        #Set the new x, y, and z points as well as updating the time and frame.
        point.set_data(new_x, new_y)
        point.set_3d_properties(new_z)
        text.set_text(f'File is: {file}.\nAt time: {time}, and frame: {frame}.\n')
        
        return point, text
        
    #Create the animation with the figure, update and initialization functions, frames = length of the dataframe 
    #(total number of rows), and interval at 2 (speed at which the animation updates).
    animation = FuncAnimation(figure, update, frames = len(df), init_func=init, blit = True, interval = 2)
    plt.show()
    
    
directory = r"CSV Takes"
for path, folders, files in os.walk(directory):
    for file in files:
        print(f"This is file: {file}")
        newFile = r"CSV Takes/" + file
        df = displayCSVData(newFile)
        visualization(df, file)
    break

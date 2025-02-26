from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from io import StringIO
from collections import defaultdict
import numpy as np
import pandas as pd
import os
import re

#Slightly cleaning the CSV data and testing values. Still needs to be updated such that no manual work needs to be done.
def displayCSVData(file):
    #Read in the CSV file as a text file, line by line (aka list of lines).
    with open(file, "r", encoding="utf-8") as textFile:
        lines = textFile.readlines()
    
    
    #Remove the first two lines, being uneccessary data and an empty row.
    lines = lines[2:]
    
    
    #Then, create list of the lines that will form the header (multiple row names are concatenated to form a singular row name),
    #and create a list of lines that contain the actual row data from the take file.
    headerLines = lines[:2] + lines[3:5]
    actualData = lines[5:]
    
    #Joining words together since I'd like to take certain words from the header, aka if I detect something other than "Marker#"
    #in a column number after the "Rigid Body Marker" part of the column name, then I know we're onto a new rigidbody, and I'd join
    #those as a whole group so the rigid body and its respective could be the same color in the graph.
    headerLines[1] = ",".join([re.sub("_", "", word) for word in headerLines[1].split(",")])
    
    
    #Split the headers by the comma separating them and strip them of the commas, join them as a list of columns, and finally create a 
    #new list of headers that are the concatenated column names, separated by '_''s.
    splitHeaders = [x.strip().split(",") for x in headerLines]
    columns = list(zip(*splitHeaders))
    header = ["_".join(filter(None, map(str.strip, column))) for column in columns]


    #Finally, join the data text together, read that into a CSV form, make the headers of this DF the columns we created,
    #and drop any columns containing ':' in their names (typically missing data OR repeated data columns).
    allText = "".join(actualData)
    df = pd.read_csv(StringIO(allText), header=None)
    df.columns = header
    
    
    #This filters for the first column with ':' in its name, and then removes it and every subsequent column from the df.
    for c in df.columns:
        if ":" in c:
            print(c)
            columnIndexToBreak = df.columns.get_loc(c)
            df = df.iloc[:, :columnIndexToBreak]
            break


    print(df.head())
    
    return df


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
    
    
    #Regex's to mimic the pattern of a column header for a limb and a column header for a marker.
    nonMarkerPattern = re.compile(r'^Rigid Body_([\w]+)_')
    markerPattern = re.compile(r'^Rigid Body Marker_(Marker\d+)_')
    
    
    #Baically looks through the column header names, and once it sees a different limb, it (SHOULD) split it. Currently
    #encountering a bug which I've temporarily fixed in the loop just below this.
    markerGrouping = []
    newList = []
    activeLimb = None
    index = 0
    
    columnIndices = defaultdict(list)
    
    for i, c in enumerate(markerDF.columns):
        currentLimb = nonMarkerPattern.search(c)
        currentMarker = markerPattern.search(c)
        
        columnIndices[c].append(i)
        
        if currentLimb and not currentMarker:
            limbName = currentLimb.group(1)
            
            if(activeLimb and limbName != activeLimb):
                markerGrouping.append(newList)
                newList = []
            activeLimb = limbName
            newList.append((c, i))
            
        elif (currentMarker and activeLimb):
            newList.append((c, i))
        index = index + 1
    
    if newList:
        markerGrouping.append(newList)
            
    
    #For some reason it was splitting the correct groupings into three indexes in the list, for now I'm going to
    #simply group them by threes since that works for the example take; however, there may be some bug fixes
    #I need to address soon.
    secondToLastList = []
    for x in range(0, int(len(markerGrouping)/3)):
        correctList = markerGrouping[(3*x)] + markerGrouping[(3*x)+1] + markerGrouping[(3*x)+2]
        secondToLastList.append(correctList)
    
    print(len(secondToLastList))
    
    
    #The problem with the above list is that simply pulling from the dataframe returns duplicates for the markers
    #for each limb, since the markers are basically all named the same. Therefore, we had to index in one of the 
    #functions above and then use those indexes to pull the correct column marker into the groupedMarkers data.
    columnCount = defaultdict(int)
    groupedMarkers = []
    for g in secondToLastList:
        groupData = []
        
        for column, columnIndex in g:
            columnCount[column] += 1
            columnOccurrence = columnCount[column] - 1
            
            if columnOccurrence < len(columnIndices[column]):
                correctIndex = columnIndices[column][columnOccurrence]
                columnData = markerDF.iloc[:, correctIndex]
                groupData.append(columnData)
            
        groupedMarkers.append(groupData)

    print(groupedMarkers[0])
    
    
    
    #Create a marker list holding multiple marker objects with x, y, and z colums each.
    MarkerList = []
    for grouping in groupedMarkers:
        for x in range(int(len(grouping)/4)):
            MarkerList.append(Marker(grouping[(4*x)], grouping[((4*x)+1)], grouping[((4*x)+2)]))
            #print(markerDF.iloc[:, (4*x)], markerDF.iloc[:, ((4*x)+1)], markerDF.iloc[:, ((4*x)+2)])
            #print(markerDF.shape[1])
 
    print(f"Number of markers is {len(MarkerList)}")


    #Create the figure and axes.
    figure = plt.figure()
    axes = figure.add_subplot(111, projection='3d')

    #Set the figure's limits (find min and max values for each axis).
    #First, find min and max values for the x, y, and z of each marker. THEN, find the min and max between the x, y, and z's of the marker objects.
    #However, currently manually setting the min and max values. Will be changed soon.
    axes.set_xlim(-2, 3)
    axes.set_ylim(-2, 3)
    axes.set_zlim(-2, 3)


    #x, y, and z initial points from each marker, aka an array of n values for each axis from frame 0.
    initializedX = [item.x[0] for item in MarkerList]
    initializedY = [item.y[0] for item in MarkerList]
    initializedZ = [item.z[0] for item in MarkerList]


    #Set point = beginning x, y, and z positions, then create text to display frame and timestamp in the 3D figure.
    point, = axes.plot(initializedX, initializedY, initializedZ, 'bo', markersize=10)
    text = axes.text2D(0, 0.9, '', transform=axes.transAxes, fontsize=12, verticalalignment='top')

    #Creating the colors for each point in the 3D graph.
    colors = [plt.cm.gist_rainbow(x) for x in np.linspace(0,1,len(MarkerList))]
    
    #Converting the np.float64 values to float values.
    newColors = []
    for t in colors:
        tupleList = []
        for wrongFloat in t:
            tupleList.append(float(wrongFloat))
        newColors.append(tuple(tupleList))

    print(type(newColors[:1][0]))        

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
        
        #Take the [0] index of newColors since it's technically a tuple within a list.
        #Still not working, however
        #point.set_color(newColors[:frame+1][0])
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

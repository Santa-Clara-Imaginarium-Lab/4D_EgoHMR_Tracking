import pandas as pd

#For now, just wanna look at what data we're receiving from the CSV file.
def displayCSVData():
    #Read in the CSV file and remove uneccessary columns first.
    motiveDF = pd.read_csv("Motive Modified Take File.csv")
    motiveDF = motiveDF.loc[:, ~motiveDF.columns.str.contains('^Unnamed')]
    print(motiveDF)
    
    #Taking one example of the rigid body's X position, comparing to the average of the 4 markers, it should be roughly the same.
    rigidBodyXPosition = 1.152497
    averageMarkerPosition = (1.234662+1.140421+1.134937+1.099968)/4
    
    #Prints if it's within or outside of the error range.
    print(averageMarkerPosition, "while rigidBody is", rigidBodyXPosition)
    if((rigidBodyXPosition-averageMarkerPosition) <=.01):
        print((rigidBodyXPosition-averageMarkerPosition), "is within error range")
    else:
        print((rigidBodyXPosition-averageMarkerPosition), "is outside of error range")
        
    #Getting the maximum and minimum values of each marker's X, Y, Z values (and extra max/mins).
    maxVals = motiveDF.max()
    minVals = motiveDF.min()
    print("Max values are:")
    print(maxVals)
    print("Min values are:")
    print(minVals)

displayCSVData()
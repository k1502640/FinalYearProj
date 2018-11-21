import json
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from gmplot import gmplot
from geopy import Nominatim
import coverage

# begin coverage tracking
cov = coverage.Coverage()
cov.start()

API_KEY = 'AIzaSyDe_N9qkpkCVUGGoP8jRezfu-WxF-aIzLU'
geolocator = Nominatim()

class PlotCluster:

    # identify the root folder
    global dir
    dir= r".\DATA"
    # set up the os.walk in the directory
    global filelist
    filelist = os.walk(dir)
    # used to store the coordinate pairs
    global coords
    coords = []
    # ask user to enter city and save the coordinates for the city
    global userlocation
    userlocation = input('Please enter city: ').title()
    location = geolocator.geocode(userlocation)
    global sessionlongitude
    sessionlongitude= location.longitude
    global sessionlatitude
    sessionlatitude= location.latitude
    # print the coordinates of the chosen city
    print(location.longitude, location.latitude)

    # loop through the folders, sub folders and files
    def openfile(self):

        for subdir, dirs, files in filelist:
            for f in files:
                # if JSON.txt file is found begin to read
                if f.endswith(".txt"):
                    filedir = os.path.join(subdir, f)
                    file = open(filedir, 'r')
                    data = json.load(file)
                    # retrieve necessary data
                    # and find out if all the data is present on one file or split across multiple
                    total = int(data["photos"]["total"])
                    perpage = data["photos"]["perpage"]
                    page = data["photos"]["page"]
                    pages = data["photos"]["pages"]
                    # create boundary points around city
                    pluslat = sessionlatitude + 0.2
                    minuslat = sessionlatitude - 0.2
                    pluslon = sessionlongitude + 0.2
                    minuslon = sessionlongitude - 0.2
                    # if they are all on one page read the lat and lon
                    if total <= perpage:
                        for n in range(0, total):
                            x = data["photos"]["photo"][n]["longitude"]
                            y = data["photos"]["photo"][n]["latitude"]
                            # only read the coordinates within safe range
                            if (float(y) <= (pluslat)) and (float(y) >= (minuslat)):
                                if (float(x) <= (pluslon)) and (float(x) >= (minuslon)):
                                    coords.append([float(x), float(y)])
                    else:
                        # if there are more pages, check those too
                        if page < pages:
                            for n in range(0, perpage):
                                x = data["photos"]["photo"][n]["longitude"]
                                y = data["photos"]["photo"][n]["latitude"]
                                # only read the coordinates within safe range
                                if (float(y) <= (pluslat)) and (float(y) >= (minuslat)):
                                    if (float(x) <= (pluslon)) and (float(x) >= (minuslon)):
                                        coords.append([float(x), float(y)])
                        else:
                            # ensure all pages are visited
                            difference = total - (pages-1)*perpage
                            for n in range(0, difference):
                                x = data["photos"]["photo"][n]["longitude"]
                                y = data["photos"]["photo"][n]["latitude"]
                                # only read the coordinates within safe range
                                if (float(y) <= (pluslat)) and (float(y) >= (minuslat)):
                                    if (float(x) <= (pluslon)) and (float(x) >= (minuslon)):
                                        coords.append([float(x), float(y)])
        # send back a list of coordinate pairs
        return coords

    def getXY(self):
        # this separates the coordinate pairs into x and y for plotting
        coords = self.openfile()
        xcoords = []
        ycoords = []
        for x in coords:
            # take the first element and add it to the x
            xcoords.append(x[0])
        for y in coords:
            # take the second element and add it to the y
            ycoords.append(y[1])
        return xcoords, ycoords

    def plotmap(self):
        xy = self.getXY()
        plt.scatter(xy[0], xy[1], s=1.2, c="black", marker=".")
        plt.show()

    def Cluster(self):
        # read in the coords within the safe range
        coords = self.openfile()
        # set radians for the haversine metric
        kms_per_radian = 6371.0088
        # set epsilon to 50 meters
        epsilon = 0.05 / kms_per_radian
        # set epslion really small so it forms a cluster on each plot
        espsi = 0.0000000000000000001 / kms_per_radian
        # perform the DBSCAN using the ball tree algorithm and haversine metric.
        # form cluster if 10 pics are present within 50 meters
        db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        # form cluster on every single plot
        scat = DBSCAN(eps=espsi, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        cluster_labels = db.labels_
        scatcluster_labels = scat.labels_
        # set number of clusters to the number of labels (one per cluster)
        num_clusters = len(set(cluster_labels))
        if num_clusters < 3:
            print('Not enough clusters were formed')
            PlotCluster()
        scatnum_clusters = len(set(scatcluster_labels))
        print('Number of clusters: {}'.format(scatnum_clusters))
        # convert the coords to a DataFrame with columns of lat and lon
        scat = pd.DataFrame(coords, columns=["latitude", "longitude"])
        df = pd.DataFrame(coords, columns=["latitude", "longitude"])
        # convert to matrix to allow manipulation into series
        scatcoords = scat.as_matrix(columns=["latitude", "longitude"])
        coords = df.as_matrix(columns=["latitude", "longitude"])
        # store clusters in a series data type
        clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters - 1)])
        scatclusters = pd.Series([scatcoords[scatcluster_labels == n] for n in range(scatnum_clusters - 1)])

        # this function was taken from a webpage
        def get_centermost_point(cluster):
            # using the centroid attribute, pull out the centre point of each cluster
            centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
            # save the centermost point in a variable and return as a tuple
            centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
            print(centermost_point)
            return tuple(centermost_point)

        # use series' map attribute to map the centermost point to each cluster
        centermost_points = clusters.map(get_centermost_point)
        # also map every point to the clusters of each point to allow for plotting
        scatplot = scatclusters.map(get_centermost_point)
        # separate the lat and lon points from the tuple
        Alatitude, Alongitude = zip(*scatplot)
        latitude, longitude = zip(*centermost_points)
        # plot the centermost points using matplotlib
        plt.scatter(latitude, longitude, s=2, c="black", marker=".")
        plt.show()

        # use gmap to open the map to the first plot point
        gmap = gmplot.GoogleMapPlotter(longitude[0], latitude[0], zoom=15)
        # plot the centermost points and every other point
        gmap.scatter(longitude, latitude, '#ff0000', size=10, marker=False)
        gmap.scatter(Alongitude, Alatitude, '#0000ff', size=5, marker=False)
        # save map as html file in directory
        gmap.draw(userlocation + 'Map.html')

# call class, plot the initial map, then cluster and plot centermost points
JP = PlotCluster()
JP.plotmap()
JP.Cluster()

# stop monitoring the coverage and save
cov.stop()
cov.save()

# draw up coverage report
cov.html_report()
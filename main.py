from flask import render_template
import csv, geopy.distance, collections, heapq
from flask import Flask, redirect, url_for, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("mainpage.html")

@app.route('/display/<starting>/<ending>')
def display(starting,ending):
    output=''
    Location = collections.namedtuple("Location", "ID CODE NAME LATITUDE LONGITUDE".split())
    data = {}
    with open("stops.csv") as f:
        r = csv.DictReader(f)
        for d in r:
            i, c, n, la, lo = int(d["stop_id"]), d["stop_code"], d["stop_name"], d["stop_lat"], d["stop_lon"]
            data[i] = Location(i, c, n, la, lo)

    def calcH(start, end):
        cod1 = (data[start].LATITUDE, data[start].LONGITUDE)
        cod2 = (data[end].LATITUDE, data[end].LONGITUDE)
        distance = (geopy.distance.vincenty(cod1, cod2)).km
        return distance

    def getneighbors(startLocation, n=10):
        return sorted(data.values(), key=lambda x: calcH(startLocation, x.ID))[1:n + 1]

    def getParent(closedlist, index):
        path = []
        while index is not None:
            path.append(index)
            index = closedlist.get(index, None)
        return [data[i] for i in path[::-1]]

    startIndex = int(starting)
    endIndex = int(ending)  # 1056 839 3313 3418
    print(startIndex, endIndex)

    Node = collections.namedtuple("Node", "ID F G H parentID".split())

    h = calcH(startIndex, endIndex)
    openlist = [(h, Node(startIndex, h, 0, h, None))]
    closedlist = {}

    count = 0
    while len(openlist) >= 1:
        _, currentLocation = heapq.heappop(openlist)
        print(currentLocation)

        if currentLocation.ID in closedlist:
            continue
        closedlist[currentLocation.ID] = currentLocation.parentID

        if currentLocation.ID == endIndex:
            print("complete")
            output+="complete Route is:"+"<br>"
            for p in getParent(closedlist, currentLocation.ID):
                output+=str(p)+"<br>"
                print(output)
                count += 1
            return "%s" % output


        for other in getneighbors(currentLocation.ID):
            g = currentLocation.G + calcH(currentLocation.ID, other.ID)
            h = calcH(other.ID, endIndex)
            f = g + h
            heapq.heappush(openlist, (f, Node(other.ID, f, g, h, currentLocation.ID)))



@app.route("/output",methods = ['POST','GET'])
def output():
    if request.method == 'POST':
        startid = request.form['startid']
        endid = request.form['endid']
        return redirect(url_for('display',starting=startid,ending=endid))

if __name__ == "__main__":
    app.run(debug=True)
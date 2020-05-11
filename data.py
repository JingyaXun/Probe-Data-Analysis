
class ProbePoint:
    def __init__(self, sampleID, dateTime, sourceCode, latitude, longitude, altitude, speed, heading):
        #initial record
        self.sampleID = sampleID
        self.dateTime = dateTime
        self.sourceCode = sourceCode
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.altitude = altitude
        self.speed = speed
        self.heading = heading

        # matched points
        self.linkPVID = ""
        self.direction = ""
        self.distFromRef = ""
        self.distFromLink = ""


        self.linkNode = ""
        self.distFromRefLat = ""
        self.distFromRefLong = ""
        self.distFromLinkLat = ""
        self.distFromLinkLong = ""

class LinkData:
    def __init__(self, linkPVID, refNodeID, nrefNodeID, length, functionalClass, directionOfTravel, speedCategory, fromRefSpeedLimit, toRefSpeedLimit, fromRefNumLanes, toRefNumLanes, multiDigitized, urban, timeZone, shapeInfo, curvatureInfo, slopeInfo):

        #initial record
        self.linkPVID = linkPVID
        self.refNodeID = refNodeID
        self.nrefNodeID = nrefNodeID
        self.length = length
        self.functionalClass = functionalClass
        self.directionOfTravel = directionOfTravel
        self.speedCategory = speedCategory
        self.fromRefSpeedLimit = fromRefSpeedLimit
        self.toRefSpeedLimit = toRefSpeedLimit
        self.fromRefNumLanes = fromRefNumLanes
        self.toRefNumLanes = toRefNumLanes
        self.multiDigitized = multiDigitized
        self.urban = urban
        self.timeZone = timeZone
        self.shapeInfo = self.process(shapeInfo)
        self.curvatureInfo = curvatureInfo
        self.slopeInfo = slopeInfo
        self.minLat = min(self.shapeInfo, key=lambda l: l.latitude).latitude
        self.maxLat = max(self.shapeInfo, key=lambda l: l.latitude).latitude
        self.minLong = min(self.shapeInfo, key=lambda l: l.longitude).longitude
        self.maxLong = max(self.shapeInfo, key=lambda l: l.longitude).longitude
        # self.slope = self.process_slope()

    def process(self,shapeInfo):
        temp = []
        points = shapeInfo.split("|")
        for i in points:
            data = i.split("/")
            # print(data)
            if(len(data)==3 and data[2]!=''):
                # print(data[2])
                temp.append(LinkPoint(data[0], data[1],data[2]))
            else:
                temp.append(LinkPoint(data[0], data[1]))

        return temp

    def process_slope(self):
        if(self.slopeInfo is None):
            return
        temp=[]
        slopes = self.slopeInfo.split("|")
        for i in slopes:
            data = i.split("/")
            temp.append([data[0],data[1]])
        return temp


class LinkPoint:
    def __init__(self, latitude, longitude, altitude = None):
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        if(altitude is not None):
            self.altitude = float(altitude)
            # print(self.altitude)
        else:
            self.altitude = None

class MatchedData:
    def __init__(self, sampleID, dateTime, sourceCode, latitude, longitude, altitude, speed, heading, linkPVID, linkRefNode, direction, distFromNode, distFromLinkLine):
        self.sampleID = sampleID
        self.dateTime = dateTime
        self.sourceCode = sourceCode
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.speed = speed
        self.heading = heading
        self.linkPVID = linkPVID
        self.linkRefNode = linkRefNode
        self.direction = direction
        self.distFromNode = distFromNode
        self.distFromLinkLine = distFromLinkLine
        self.slope = None

    def __str__(self):
        shapeInfo = "["
        for point in self.shapeInfo[:-1]:
            shapeInfo += str(point) + "\n"
        shapeInfo += "\t\t\t" + str(self.shapeInfo[-1]) + "]"
        return "Link PVID: " + str(self.linkPVID) + "\n" + "\tLength: " + str(self.length) + "\n" + "\tShapeInfo: " + shapeInfo

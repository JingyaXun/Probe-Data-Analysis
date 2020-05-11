import csv
import pandas as pd
import math
import sys
import random
import numpy as np
from data import ProbePoint,LinkData,LinkPoint,MatchedData

R = 6373.0

def process_data(probedata_path, linkdata_path):
    probe_data = {}
    link_data = []
    with open(probedata_path) as f1:
        temp = csv.reader(f1)
        for i in temp:
            if (str(i[0]) not in probe_data):
                probe_data[str(i[0])] = [[]]
            batch_size = 10
            if (len(probe_data[str(i[0])][-1]) < batch_size):
                probe_data[str(i[0])][-1].append(ProbePoint(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
            else:
                probe_data[str(i[0])].append([ProbePoint(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])])
    with open(linkdata_path) as f2:
        temp = csv.reader(f2)
        for i in temp:
            link_data.append(LinkData(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15], i[16]))
    link_data.sort(key=lambda x: x.shapeInfo[0].latitude, reverse=True)
    return probe_data, link_data

def map_match(probe_data, link_data):
    probe_index = 0
    total_probe_ids = len(probe_data)

    with open('Partition6467MatchedPoints.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        temp = 1
        writer.writerow(["sampleID", "dateTime", "sourceCode", "Latitude", "Longitude", "Altitude", "Speed", "Heading", "linkPVID",  "direction", "distFromNode", "distFromLinkLine"])
        for probe_id in probe_data:
            temp +=1
            if(temp>4):
                break
            probe_index+=1
            sys.stdout.write('\r')
            sys.stdout.write('[ ' + str(probe_index) + "/" + str(total_probe_ids) + ' ]')
            batches = probe_data[probe_id]
            for batch in batches:
                links = {}
                link_counts = {}
                for probe in batch:
                    closestLink = None
                    closestLinkPointDistance = math.inf
                    for link in link_data:
                        if (probe.latitude < link.minLat or probe.latitude > link.maxLat or probe.longitude < link.minLong or probe.longitude > link.maxLong):
                            continue
                        for linkPoint in link.shapeInfo:
                            distance = calc_dist(linkPoint.longitude,linkPoint.latitude,probe.longitude,probe.latitude)
                            if (distance < closestLinkPointDistance):
                                closestLinkPointDistance = distance
                                closestLinkPoint = linkPoint
                                closestLink = link
                    if (closestLink == None): closestLink = link_data[random.randint(0, len(link_data)-1)]
                    if (closestLink.linkPVID not in link_counts):
                        link_counts[closestLink.linkPVID] = 0
                    link_counts[closestLink.linkPVID] += 1
                    if (closestLink.linkPVID not in links):
                        links[closestLink.linkPVID] = closestLink

                best_link = ""
                best_count = 0
                for linkPVID in link_counts:
                    if (link_counts[linkPVID] > best_count):
                        best_count = link_counts[linkPVID]
                        best_link = linkPVID
                for p in batch:
                    p.linkPVID = best_link
                    p.direction = links[best_link].directionOfTravel
                    refNode = None
                    nonRefNode = None
                    if (len(links[best_link].shapeInfo) > 0):
                        refNode = links[best_link].shapeInfo[0]
                        p.linkNode = str(refNode.latitude) + ", " + str(refNode.longitude)
                        nonRefNode = links[best_link].shapeInfo[-1]
                    p.distFromRef = -1
                    if (refNode != None):
                        p.distFromRef= calc_dist(refNode.latitude,refNode.longitude,p.latitude,p.longitude)
                    p.distFromLink = "N/A"
                    if (refNode != None and nonRefNode != None):
                        if(nonRefNode.altitude is not None):
                            p.distFromLink = -(float(p.altitude) - nonRefNode.altitude)

                    writer.writerow([p.sampleID, p.dateTime, p.sourceCode, str(p.latitude), str(p.longitude), p.altitude, p.speed, p.heading, p.linkPVID, p.direction, str(p.distFromRef), str(p.distFromLink)])

    print("map matching finished")
    return 'Partition6467MatchedPoints.csv'

def calc_dist(latitude1,longitude1,latitude2,longitude2):
    R = 6371.0* 1000
    lat1 = math.radians(latitude1)
    lon1 = math.radians(longitude1)
    lat2 = math.radians(latitude2)
    lon2 = math.radians(longitude2)
    temp1 = lon2 - lon1
    temp2 = lat2 - lat1
    a = (math.sin(temp2 / 2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(temp1 / 2))**2
    c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
    dist = R * c
    return dist

def slope_evaluation(link_data_file, matched_data_file, evaluation_file):
    print("Evaluating Slope: ")
    evaluation_file = open(evaluation_file, 'a')
    evaluation_file.write('linkPVID, groundTruth, calculatedSlope, error' + "\n")

    s_probe_list = []
    s_groundtruth_list = []
    prev_probe = None

    with open(matched_data_file) as matched_data:
        reader = csv.reader(matched_data)
        for i, row in enumerate(reader):
            match = MatchedData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
            if not prev_probe or match.sampleID != prev_probe.sampleID:
                match.slope = ''
            else:
                try:
                    start, end = list(map(float, [match.longitude, match.latitude])), list(map(float, [prev_probe.longitude, prev_probe.latitude]))
                    long1, latt1, long2, latt2 = list(map(math.radians, [start[0], start[1], end[0], end[1]]))
                    a = math.sin((latt2 - latt1) / 2) ** 2 + math.cos(latt1) * math.cos(latt2) * math.sin(
                        (long2 - long1) / 2) ** 2
                    hyp = R * 2 * math.asin(math.sqrt(a))
                    opp = float(match.altitude) - float(prev_probe.altitude)
                    match.slope = (2 * math.pi * math.atan(opp / hyp)) / 360
                except ZeroDivisionError:
                    match.slope = 0.0
            s_probe_list.append(match)
            prev_probe = match

    link_data = []
    with open(link_data_file) as link_csvfile:
        reader = csv.reader(link_csvfile)
        for row in reader:
            link_data.append(LinkData(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16]))
    link_data.sort(key=lambda x: x.shapeInfo[0].latitude, reverse=True)

    print("s_probe_list: ", len(s_probe_list))
    print("s_groundtruth_list: ", len(s_groundtruth_list))

    prev_id = None
    sum_calculated_slope, non_zero_probe_count = 0.0, 0
    for i, item in enumerate(s_probe_list):
        link_id = item.linkPVID
        if item.slope == "": continue
        if prev_id == None: prev_id = link_id
        if link_id == prev_id:
            if item.direction == "T":
                item.slope = -1 * item.slope
            if item.slope != '' and item.slope != 0:
                sum_calculated_slope += item.slope
                non_zero_probe_count += 1
        else:
            # get probe data slope
            calculated_slope = sum_calculated_slope / non_zero_probe_count if non_zero_probe_count != 0 else 0
            # get surveyed slope
            s_groundtruth = -1
            for link_obj in link_data:
                if link_id == link_obj.linkPVID and link_obj.slopeInfo != "":
                    slope_info = link_obj.slopeInfo.split("|")
                    sum_slope = 0
                    for s in slope_info:
                        sum_slope += float(s.strip().split('/')[1])
                    s_groundtruth = sum_slope / len(slope_info)
                    break
            if s_groundtruth != -1:
                error = abs(calculated_slope - s_groundtruth) / abs(s_groundtruth)
                print(calculated_slope, s_groundtruth)
                evaluation_file.write(link_id+','+str(s_groundtruth)+','+str(calculated_slope)+','+str(error)+'\n')    

            sum_calculated_slope, non_zero_probe_count = 0.0, 0
        prev_id = link_id
### SAVING AND LOADING PROBE AND LINK DATA (NOTE: NOT THAT MUCH FASTER THAN JUST CREATING THE DATA SETS AGAIN)###
# def save_data(probe_data, link_data):
#     probe_filehandler = open('./saved_probe_data.txt', 'wb')
#     link_filehandler = open('./saved_link_data.txt', 'wb')
#     pickle.dump(probe_data, probe_filehandler)
#     pickle.dump(link_data, link_filehandler)
#
# def load_data():
#     probe_filehandler = open('./saved_probe_data.txt', 'rb')
#     link_filehandler = open('./saved_link_data.txt', 'rb')
#     return pickle.load(probe_filehandler), pickle.load(link_filehandler)


if __name__ == '__main__':

    if sys.argv[1] == "map_match":
        probe_path = "Partition6467ProbePoints.csv"
        link_path = "Partition6467LinkData.csv"
        print("start data processing ... ")
        (probe_data, link_data) = process_data(probe_path, link_path)
        print("data processing finished")
        print("start map matching ...")
        output_file = map_match(probe_data, link_data)

    # slope eval
    if sys.argv[1] == "slope_eval":
        link_path = "Partition6467LinkData.csv"
        matched_data_path = "Partition6467MatchedPoints.csv"
        output_data_path = "eval.csv"
        slope_evaluation(link_path, matched_data_path, output_data_path)

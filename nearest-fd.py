from osgeo import ogr,osr
from geopy.distance import geodesic
import csv
import sys

fixupFD: dict[str, str] = {
	'06361': '01277', # the ncone map is wrong, burke has no fire district with this id, it should be 01277
}

class FireDistrict:
	def __init__(self, id: str, name: str):
		self.FDID = id
		self.name = name
		self.stations = []
		self.parcels = 0
		self.parcelsWithCloserFS = 0
		self.propertyVal = 0.0
		self.propertyValWithCloserFS = 0.0

class FireStation:
	def __init__(self, id, name, fdid, station_num, pt):
		self.FSID = id
		self.name = name
		self.FDID = fdid
		self.station_num = station_num
		self.pt = pt

class ParcelPoint:
	__slots__ = ['NPARNO', 'PARVAL', 'FDID', 'pt', 'FSID_Nearest', 'FSID_NearestInDistrict', 'Dist_Nearest', 'Dist_NearestInDistrict']
	def __init__(self, l):
		self.NPARNO = l['NPARNO']
		self.PARVAL = float(l['PARVAL']) if l['PARVAL'] and (l['PARVAL'] != 'None') else 0.0
		self.FDID = l['FDID']
		self.pt = (float(l['X']), float(l['Y']))
		self.FSID_Nearest = None
		self.FSID_NearestInDistrict = None
		self.Dist_Nearest = float('inf')
		self.Dist_NearestInDistrict = float('inf')

fd: dict[str, FireDistrict] = {}
fs: dict[str, FireStation] = {}
parcels: dict[str, ParcelPoint] = {}

target_srs = osr.SpatialReference()
target_srs.ImportFromEPSG(4326)

with open('../data/burkefd.tsv', 'r') as file:
	reader = csv.DictReader(file, delimiter="\t")
	for row in reader:
		fdid = row['FDID']
		if fdid in fixupFD: fdid = fixupFD[fdid]
		fd[fdid] = FireDistrict(fdid, row['FDNAME'])

stations = ogr.Open('/vsizip/../data/NC_Fire_Stations_7200722316549403871.zip/Fire_Stations.shp')
stationLayer = stations.GetLayer()
xstation = osr.CoordinateTransformation(stationLayer.GetSpatialRef(), target_srs)

for station in stationLayer:
	id = station.GetFID()
	name = station.GetField('DEPT_NAME')
	fd_id = station.GetField('FD_ID')
	station_num = station.GetField('STATION_NU')

	if not fd_id in fd: continue

	stationGeo = station.GetGeometryRef()
	if not stationGeo or not stationGeo.IsValid():
		print(f"Warning: Station geometry is missing. Skipping this feature.")
		continue

	stationGeo.Transform(xstation)

	X = stationGeo.GetX()
	Y = stationGeo.GetY()
	PT = (X,Y)

	fs[id] = FireStation(id, name, fd_id, station_num, PT)
	fd[fd_id].stations.append(fs[id])

print(f"Loaded {len(fs)} fire stations from {len(fd)} fire departments.")

# sys.exit()

with open('../data/parcel2fd.tsv', 'r') as file:
	reader = csv.DictReader(file, delimiter="\t")
	for row in reader:
		fdid = row['FDID']
		if fdid in fixupFD:
			fdid = fixupFD[fdid]
			row['FDID'] = fdid
		parcels[row['NPARNO']] = ParcelPoint(row)

parcelsWithCloserFS = 0
parcelCount = 0

for parcel in parcels.values():
	parcelCount += 1
	if parcelCount % 1000 == 0: print("." , end="", flush=True)

	ppt = parcel.pt
	parcelFD = fd[parcel.FDID] if parcel.FDID in fd else None

	for stationid,station in fs.items():
		d = geodesic(ppt, station.pt).miles
		if d < parcel.Dist_Nearest:
			parcel.Dist_Nearest = d
			parcel.FSID_Nearest = stationid

		if ((station.FDID == parcel.FDID) and d < parcel.Dist_NearestInDistrict) or (parcel.FDID is None):
			parcel.Dist_NearestInDistrict = d
			parcel.FSID_NearestInDistrict = stationid

	if parcelFD:
		parcelFD.parcels += 1
		parcelFD.propertyVal += parcel.PARVAL
		if parcel.Dist_Nearest < parcel.Dist_NearestInDistrict:
			parcelsWithCloserFS += 1
			parcelFD.parcelsWithCloserFS += 1
			parcelFD.propertyValWithCloserFS += parcel.PARVAL

print(f"\nProcessed {parcelCount} parcels. Found {parcelsWithCloserFS} parcels with closer fire stations than their own district.")
with open("../data/burkefd2.tsv", "w") as out:
	print(f"FDID\tFDNAME\tSTATIONS\tPARCELS\tPROPERTYVAL\tPARCELS_WITH_CLOSER_FS\tPROPERTYVAL_WITH_CLOSER_FS",file=out)
	for fdistrict in fd.values():
		print(f"{fdistrict.FDID}\t{fdistrict.name}\t{len(fdistrict.stations)}\t{fdistrict.parcels}\t{fdistrict.propertyVal:.2f}\t{fdistrict.parcelsWithCloserFS}\t{fdistrict.propertyValWithCloserFS:.2f}",file=out)

with open("../data/burkefirestations.tsv", "w") as out:
	print(f"STATIONID\tFDID\tNAME\tNUM\tX\tY",file=out)
	for stationid, station in fs.items():
		print(f"{stationid}\t{station.FDID}\t{station.name}\t{station.station_num}\t{station.pt[0]:.6f}\t{station.pt[1]:.6f}",file=out)

with open("../data/nearestfd.tsv", "w") as out:
	print(f"NPARNO\tPARVAL\tFDID\tFSID_nearestindistrict\tD_nearestInDistrict\tFSID_nearest\tD_nearest\tDiff\tX\tY",file=out)
	for parcel in parcels.values():
		diff = parcel.Dist_Nearest - parcel.Dist_NearestInDistrict
		print(f"{parcel.NPARNO}\t{parcel.PARVAL}\t{parcel.FDID}\t{parcel.FSID_NearestInDistrict}\t{parcel.Dist_NearestInDistrict}\t{parcel.FSID_Nearest}\t{parcel.Dist_Nearest}\t{diff}\t{parcel.pt[0]:.6f}\t{parcel.pt[1]:.6f}",file=out)

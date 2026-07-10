from osgeo import ogr,osr
from geopy.distance import geodesic
import csv, os, sys
import lib.config as config
from lib.fdtypes import FireDistrict, FireStation, ParcelPoint

fd: dict[str, FireDistrict] = {}
fs: dict[str, FireStation] = {}
parcels: dict[str, ParcelPoint] = {}

target_srs = osr.SpatialReference()
target_srs.ImportFromEPSG(4326)

with open(f"{config.src_datafolder}/burkefd.csv", 'r') as file:
	reader = csv.DictReader(file)
	for row in reader:
		fdid = row['FDID']
		fd[fdid] = FireDistrict(fdid, row['FDNAME'])

stations = ogr.Open(f"/vsizip/{config.src_datafolder}/NC_Fire_Stations_7200722316549403871.zip/Fire_Stations.shp")
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

with open(config.src_datafolder+'/parcel2fd.csv', 'r') as file:
	reader = csv.DictReader(file)
	for row in reader:
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
with open(f"{config.src_datafolder}/burkefd2.csv", "w", newline='') as out:
	writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["FDID", "FDNAME", "STATIONS", "PARCELS", "PROPERTYVAL", "PARCELS_WITH_CLOSER_FS", "PROPERTYVAL_WITH_CLOSER_FS"])
	for fdistrict in fd.values():
		writer.writerow([fdistrict.FDID, fdistrict.name, len(fdistrict.stations), fdistrict.parcels, f"{fdistrict.propertyVal:.2f}", fdistrict.parcelsWithCloserFS, f"{fdistrict.propertyValWithCloserFS:.2f}"])

with open(f"{config.src_datafolder}/burkefirestations.csv", "w", newline='') as out:
	writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["STATIONID", "FDID", "NAME", "NUM", "lat", "lng"])
	for stationid, station in fs.items():
		writer.writerow([stationid, station.FDID, station.name, station.station_num, f"{station.pt[0]:.6f}", f"{station.pt[1]:.6f}"])

with open(f"{config.src_datafolder}/nearestfd.csv", "w", newline='') as out:
	writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["NPARNO", "PARVAL", "FDID", "FSID_nearestindistrict", "D_nearestInDistrict", "FSID_nearest", "D_nearest", "Diff", "lat", "lng"])
	for parcel in parcels.values():
		diff = parcel.Dist_Nearest - parcel.Dist_NearestInDistrict
		writer.writerow([parcel.NPARNO, parcel.PARVAL, parcel.FDID, parcel.FSID_NearestInDistrict, parcel.Dist_NearestInDistrict, parcel.FSID_Nearest, parcel.Dist_Nearest, diff, f"{parcel.pt[0]:.6f}", f"{parcel.pt[1]:.6f}"])

import csv, json, os, sys
from lib.fdtypes import FireDistrict, FireStation
from datetime import datetime
import lib.config as config
import lib.util as util

fd: dict[str, FireDistrict] = {}

with open(config.src_datafolder + "/burkefd2.csv", "r") as file:
	reader = csv.DictReader(file)
	for row in reader:
		fd1 = FireDistrict(row['FDID'], row['FDNAME'])
		fd1.initFromCSV(row)
		fd[fd1.name] = fd1

fd = dict(sorted(fd.items()))

fdate = datetime.fromtimestamp(os.path.getmtime(config.src_firedistricts_shapefile))
fdVersion = fdate.strftime("%Y%m%d")
pmtileSrc = f"assets/map/burkefd{fdVersion}.pmtiles"

fdenv = {'version':fdVersion,'pmtile':pmtileSrc}
# write the env date into a file that can be accessed by the Jeckyll docs
with open(config.web_datafolder+"/fdenv.json", "w") as out:
	json.dump(fdenv,out)

# create a readable summary CSV of the fire districts and corresponding parcel counts and value,
# plus the number of parcels who have a closer fire station outside of the district
with open(config.web_datafolder+"/burkefd.csv", "w", newline='') as out:
	writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["Name", "Stations", "Parcels", "Value", "Closer Station Parcels", "CSP Value"])
	for fdistrict in fd.values():
		writer.writerow([fdistrict.name, fdistrict.stations, util.human_format(fdistrict.parcels), f"${util.human_format(fdistrict.propertyVal)}", util.human_format(fdistrict.parcelsWithCloserFS), f"${util.human_format(fdistrict.propertyValWithCloserFS)}"])

# create a pmtiles that can be used to visualize the fire district data on a map
os.system(
	f"tippecanoe -f -Z8 -z12 -o docs/{pmtileSrc} -y NPARNO -y PARVAL -y FDID -y FSID_nearestindistrict -y FSID_nearest -y firedepart " +
	f"--named-layer='burke:{config.src_datafolder}/burke-boundary.geojson' " +
	f"--named-layer='firedistricts:{config.src_datafolder}/fd-burke.geojson.gz' " +
	f"--named-layer='firestations:{config.src_datafolder}/burkefirestations.csv' " +
	f"--named-layer='parcels:{config.src_datafolder}/nearestfd.csv'"
)

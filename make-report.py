import csv, os, sys
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
fdVersion = fdate.strftime("%Y-%m-%d")

with open("./docs/index.md", "w") as out:
	out.write(f"# Fire Districts (vintage {fdVersion})\n\n")
	out.write(f"## Summary\n\n")
	out.write(f"| Name | Stations | Parcels | Prop Value | Parcels with Closer Station | Prop Value |\n")
	out.write(f"| --- | --- | --- | --- | --- | --- |\n")
	for fdistrict in fd.values():
		out.write(f"| {fdistrict.name} | {fdistrict.stations} | {util.human_format(fdistrict.parcels)} | ${util.human_format(fdistrict.propertyVal)} | {util.human_format(fdistrict.parcelsWithCloserFS)} | ${util.human_format(fdistrict.propertyValWithCloserFS)} |\n")

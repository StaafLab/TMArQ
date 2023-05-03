

#file handling support functions

import os

def set_headers(file, headers):
	with open(file, "a") as f:
		f.write(headers)

def path_to_dir(ptd):
	if os.path.isdir(ptd):
		return ptd
	else:
		raise NotADirectoryError(ptd)

def check_outdir(outdir, message=True):
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	if message==True:
		print(f'created output directory {outdir}')

def list_files(input_dir):
	files = [f for f in os.listdir(input_dir) if os.path.isfile(input_dir+"/"+f) and not f.startswith(".")]
	return files

def create_coord_dict(coordinates_file):
	
	coordinate_dict = {}

	for line in coordinates_file:
		if not line.startswith("#"):
			line = line.rstrip()
			values = line.split("\t")
			coordinate_dict[values[0]] = values[1:4]

	return coordinate_dict


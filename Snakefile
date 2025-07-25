#input filenames should not contain white spaces

configfile: "config/config_example.yaml"

import json

SEGMENTS = config["segment"]
SEGMENTS = json.loads(json.dumps(SEGMENTS))

rule all:
	input:
		expand('results/01_coordinates/{block}/{marker}.txt', block=config['block'], marker=config['marker']),
		expand('results/02_segment/per_core/{block}/{marker}/{cells}', block=config['block'], marker=config['marker'],
					cells=config['segment']['cells'])

rule detectROI:
	input:
		"data/{block}/{marker}"
	output:
		coordinates = "results/01_coordinates/{block}/{marker}.txt",
		meta = "results/02_segment/meta/{block}/{marker}/" + config['excluded']
	shell:
		"bin/01_detectROI.py -i {input} -o {output.coordinates} -e {output.meta}"

rule segment:
	input:
		tma = "data/{block}/{marker}/",
		coordinates = "results/01_coordinates/{block}/{marker}.txt"
	params:
		flag = "--save-per-cell" if config["save_per_cell"] else ""
	output:
		counts = "results/02_segment/per_core/{block}/{marker}/" + config['segment']['cells'],
		meta = "results/02_segment/meta/{block}/{marker}/" + config['segment']['meta']
	shell:
		"bin/02_deconvolve.py -i {input.tma} -c {input.coordinates} -out {output.counts} -m {output.meta} {params.flag}"

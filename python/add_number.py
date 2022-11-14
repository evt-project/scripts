import argparse
import lxml.etree as ET

# parse arguments
parser = argparse.ArgumentParser(description="Add progressive numeric attribute to a XML tag", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--initial", type=int, help="initial value of the attribute", default=1)
parser.add_argument("-a", "--attribute", type=ascii, help="name of the counter attribute", default="n")
parser.add_argument("-r", "--rectoverso", action="store_true", help="only for pb tag, add recto/verso to number, starting with recto")
parser.add_argument("-v", "--versorecto", action="store_true", help="only for pb tag, add recto/verso to number, starting with verso")
parser.add_argument("-t", "--root", type=ascii, help="root tag, default TEI")
parser.add_argument("src", type=open, help="Source file")
parser.add_argument("tag", help="XML tag to which add number")
parser.add_argument("dest", help="Destination file")
args = parser.parse_args()
config = vars(args)

# read input file
ns = {
		'tei': 'http://www.tei-c.org/ns/1.0',
		'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
	}
for prefix, uri in ns.items():
	ET.register_namespace(prefix, uri)
tree = ET.parse(config["src"])
root = tree.getroot()

# insert attribute
prefix = "{http://www.tei-c.org/ns/1.0}"
c_tag = config["tag"]
TAG = prefix+c_tag
count = config["initial"]
counter_tag = config["attribute"][1:-1]
rectoverso = config["rectoverso"] | config["versorecto"]
r_tag = config["root"]

# check root tag
if r_tag is not None:
	try:
		root = next(root.iter(prefix+r_tag[1:-1]))
	except StopIteration:
		print("Error: root tag '" + r_tag[1:-1] + "' not found")
		exit(1)
	
	
# check errors
if rectoverso & (c_tag!="pb"):
	print("Error: for recto/verso option the value of 'tag' must be pb")
	exit(1)

if (c_tag == "pb") & rectoverso: # recto/verso to pages
	# set values
	rv = "r" if config["rectoverso"] else "v"
	l_count = str(count)+rv
	for item in root.iter(TAG):
		item.set(counter_tag, l_count)
		if (rv == "v"):
			count += 1
			rv = "r"
		else:
			rv = "v"
		l_count = str(count)+rv
elif (c_tag == "lb"): # count restart at each pb
	# add temp attibute
	temp_att = "xyzMyTag"
	for tag in ["lb", "pb"]:
		for item in root.iter(prefix+tag):
			item.set(temp_att, "n")
	# add n attibute and delete temp attibute
	count = 1
	for item in root.findall('.//*[@'+temp_att+']'):
		if(item.tag == prefix+"pb"):
			count = 1
		elif(item.tag == prefix+"lb"):
			item.set(counter_tag, str(count))
			count += 1
		# delete temp attibute
		del item.attrib[temp_att]
else: # common case
	for item in root.iter(TAG):
		item.set(counter_tag, str(count))
		count += 1
		
# write output file
with open(config["dest"], 'wb') as f:
    tree.write(f)

exit(0)

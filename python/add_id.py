import argparse
import lxml.etree as ET

# parse arguments
parser = argparse.ArgumentParser(description="Add progressive id attribute to a XML tag. The id has the form <prefix>_<tag>_<progressive number>; for lb tag the id has the form <prefix>_<tag>_<page number>_<progressive number>", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--initial", type=int, help="initial value of the attribute", default=1)
parser.add_argument("-a", "--attribute", type=ascii, help="name of the id attribute, xml:id if not inserted")
parser.add_argument("-r", "--rectoverso", action="store_true", help="only for pb and lb tags, add recto/verso to number, starting with recto")
parser.add_argument("-v", "--versorecto", action="store_true", help="only for pb and lb tags, add recto/verso to number, starting with verso")
parser.add_argument("-s", "--restart", type=ascii, help="restart numbering after this tag")
parser.add_argument("-t", "--root", type=ascii, help="root tag, default TEI")
parser.add_argument("src", type=open, help="Source file")
parser.add_argument("tag", help="XML tag to which add id")
parser.add_argument("prefix", help="Prefix to be inserted in the id")
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
id_tag = '{http://www.w3.org/XML/1998/namespace}id' if config["attribute"] is None else config["attribute"][1:-1]
id_pre = config["prefix"]
rectoverso = config["rectoverso"] | config["versorecto"]
r_tag = config["root"]
l_tag = config["restart"]

# check root tag
if r_tag is not None:
	try:
		root = next(root.iter(prefix+r_tag[1:-1]))
	except StopIteration:
		print("Error: root tag '" + r_tag[1:-1] + "' not found")
		exit(1)

# check errors
if rectoverso & (c_tag!="pb") & (c_tag!="lb"):
	print("Error: for recto/verso option the value of 'tag' must be pb or lb")
	exit(1)

if (c_tag == "pb") & rectoverso: # recto/verso to pages
	# set values
	rv = "r" if config["rectoverso"] else "v"
	local_prefix = id_pre+"_"+c_tag+"_"
	l_count = str(count)+rv
	for item in root.iter(TAG):
		item.set(id_tag, local_prefix+l_count)
		if (rv == "v"):
			count += 1
			rv = "r"
		else:
			rv = "v"
		l_count = str(count)+rv
elif (c_tag == "lb"): # count restart at each pb
	# add temp attibute
	temp_att = "xyzMyTag"
	for l_tag in ["lb", "pb"]:
		for item in root.iter(prefix+l_tag):
			item.set(temp_att, "n")
	# add n attibute and delete temp attibute
	count_pb = count
	# page before the first found in the document
	rv = "" if not rectoverso else "v" if config["rectoverso"] else "r"
	if (rv == "v"):
		count_pb -= 1
	l_count_pb = str(count_pb)+rv
	count = 1
	local_prefix = id_pre+"_"+c_tag+"_"
	for item in root.findall('.//*[@'+temp_att+']'):
		if(item.tag == prefix+"pb"):
			if (rv == ""):
				count_pb += 1
			elif (rv == "v"):
				count_pb += 1
				rv = "r"
			else:
				rv = "v"
			l_count_pb = str(count_pb)+rv
			count = 1
		elif(item.tag == prefix+"lb"):
			item.set(id_tag, local_prefix+str(l_count_pb)+"_"+str(count))
			count += 1
		# delete temp attibute
		del item.attrib[temp_att]
elif (l_tag is not None): # count restart at each l_tag
	local_prefix = id_pre+"_"+c_tag+"_"
	# add temp attibute
	temp_att = "xyzMyTag"
	for tag in [c_tag, l_tag]:
		for item in root.iter(prefix+tag):
			item.set(temp_att, "n")
	# add n attibute and delete temp attibute
	count = 1
	for item in root.findall('.//*[@'+temp_att+']'):
		if(item.tag == prefix+l_tag):
			count = 1
		elif(item.tag == prefix+c_tag):
			item.set(id_tag, local_prefix+str(count))
			count += 1
		# delete temp attibute
		del item.attrib[temp_att]
else: # common case
	local_prefix = id_pre+"_"+c_tag+"_"
	for item in root.iter(TAG):
		item.set(id_tag, local_prefix+str(count))
		count += 1
		
# write output file
with open(config["dest"], 'wb') as f:
    tree.write(f, pretty_print = True, xml_declaration=True, encoding="utf-8")

exit(0)

from pprint import pprint
from app.api import Templates

base = Templates()
t = Templates(type=["metadata", "dataflow", "colorspace"])
data = {"metadata": t.metadata.format()}

dataflow = t.dataflow.format(data)

pprint(dataflow.nuke.nodes.ModifyMetaData.metadata.set)
pprint(t.colorspace)

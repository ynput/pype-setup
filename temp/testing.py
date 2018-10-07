from pype import (
    nuke
)
import pype.templ
data = {}
format = Templates.pype_format
anatomy = templates.anatomy.data
file = format(anatomy.workfiles.file, data)
path = format(anatomy.workfiles.path, data)

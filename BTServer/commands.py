from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

def execute_commands(cmd):
    # import pdb; pdb.Pdb().set_trace()
    type = cmd['type']
    if type == 'setExtent':
        app = QgsApplication.instance()
        # Load the QGIS interface and plugins
        app.initQgis()

        # Get a reference to the current QGIS project
        project = QgsProject.instance()

        # Get a reference to the map canvas
        # canvas = QgsMapCanvas()
        canvas = iface.mapCanvas()

        # Set the map canvas to use the current project
        # canvas.setExtent(project.extent())
        # canvas.setLayers(project.mapLayers().values())

        # Set the extent of the map canvas to the desired values
        xmin = cmd['xmin']
        ymin = cmd['ymin']
        xmax = cmd['xmax']
        ymax = cmd['ymax']
        extent = QgsRectangle(xmin, ymin, xmax, ymax)
        canvas.setExtent(extent)

        # Refresh the map canvas to display the new extent
        canvas.refresh()
        return True
    if type == 'createLineFromWkt':
        IMPORTGROUP = "FromUXOLab"

        root = QgsProject.instance().layerTreeRoot()
        agroup = root.findGroup(IMPORTGROUP)

        if not agroup:
            agroup = root.insertGroup(0, IMPORTGROUP)

        crs = iface.mapCanvas().mapSettings().destinationCrs().authid()
        print(crs)
        wkt_str = 'LineString(532133.205341 5051929.565745,532133.213951 5051929.570419,532133.227171 5051929.570503)'
        vstr = f'LineString?crs={crs}&field=id:integer&index=yes'
        print(vstr)

        linea = iface.addVectorLayer(vstr,"Linea","memory")
        linea.startEditing()
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(wkt_str))
        feature.setAttributes([1])
        linea.addFeature(feature)
        linea.commitChanges()
        iface.zoomToActiveLayer()

    else:
        return False
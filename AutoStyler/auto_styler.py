from qgis.core import QgsProject, QgsMapLayer
import glob, os

class AutoStyler:
    def __init__(self, iface):
        self.iface = iface
        # Connect the layerAdded signal from the beginning
        QgsProject.instance().layersAdded.connect(self.apply_style_based_on_name)

    def initGui(self):
        pass

    def unload(self):
        # Disconnect the signal when the plugin is unloaded
        QgsProject.instance().layersAdded.disconnect(self.apply_style_based_on_name)

    def get_style_directory(self):
        project = QgsProject.instance()
        project_home = project.homePath()
        if not project_home:
            project_file = project.fileName()
            project_home = os.path.dirname(project_file) if project_file else ''
        return os.path.join(project_home, 'styles')  # Adjust this path as necessary

    def apply_style_based_on_name(self, layers):
        style_directory = self.get_style_directory()
        
        for layer in layers:
            layer_name = layer.name()
            # Determine the layer type (vector or raster) and apply styles accordingly
            if layer.type() == QgsMapLayer.VectorLayer:
                # List all QML files in the style directory for vectors
                qml_files = glob.glob(os.path.join(style_directory, '*.qml'))
                for qml_file in qml_files:
                    qml_basename = os.path.splitext(os.path.basename(qml_file))[0]
                    if qml_basename in layer_name:
                        layer.loadNamedStyle(qml_file)
                        layer.triggerRepaint()
                        print(f"Style applied to vector layer {layer_name} from {qml_file}")
                        break  # Stop after applying the first matching style
            elif layer.type() == QgsMapLayer.RasterLayer:
                qml_files = glob.glob(os.path.join(style_directory, 'raster_style_*.qml'))
                for qml_file in qml_files:
                    # Extract the meaningful part of the QML filename
                    qml_basename = os.path.splitext(os.path.basename(qml_file))[0]
                    style_identifier = qml_basename.replace('raster_style_', '')
                    
                    # Check if the style identifier is in the layer name
                    if style_identifier in layer_name:
                        layer.loadNamedStyle(qml_file)
                        layer.triggerRepaint()
                        print(f"Style based on {style_identifier} applied to raster layer {layer_name}")
                        
                        # Set the 'Additional no data value' to 0.0 for all bands
                        provider = layer.dataProvider()
                        for band in range(1, layer.bandCount() + 1):
                            provider.setNoDataValue(band, 0.0)
                        print(f"No data value set to 0.0 for {layer_name}")
                        break  # Stop after applying the first matching style


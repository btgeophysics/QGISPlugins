# QGISPlugins


## Setup Matlab

``` matlab
apath = 'C:\Users\admin\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins';
 
P = py.sys.path;
if count(P,apath) == 0
    insert(P,int32(0),apath);
end
 
py.importlib.import_module('BTClient')
``` 
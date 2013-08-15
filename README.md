![QGIS meshing plugins](./extras/readme_data/meshing_icon_M_withQGIS_100x.png "QGIS meshing plugins") QGIS meshing plugins
=========================================================

QGIS plugins for meshing geophysical domains.

Test engine status
------------------

[![Build Status](https://travis-ci.org/adamcandy/qgis-plugins-meshing.png?branch=master)](https://travis-ci.org/adamcandy/qgis-plugins-meshing)

Outline
-------

![UK meshed](./extras/readme_data/uk.gif "UK meshed")

This project contains four plugins for the generation of surface meshes in QGIS:

#### ![Mesh surface plugin](./extras/readme_data/meshing_icon_M2_64x.png "Mesh surface plugin") Mesh surface plugin,
#### ![Boundary identification plugin](./extras/readme_data/id_x64.png?raw=true "Boundary identification plugin") Boundary identification plugin,
#### ![Rasterise Polygons plugin](./extras/readme_data/ras_x64.png "Rasterise Polygons plugin") Rasterise Polygons plugin, and 
#### ![Raster Calculator plugin](./extras/readme_data/rastercalc.png "Raster Calculator plugin") Raster Calculator plugin.

Outline web page: [http://adamcandy.github.io/qgis-plugins-meshing/](http://adamcandy.github.io/qgis-plugins-meshing)

Installation
------------

### Ubuntu package

For anyone who would like to experiment with the plugins, please download the qgis-plugins-meshing Ubuntu package which is available in the following PPA:

    ppa:meshing/release

(which depends on packages in ppa:ubuntugis/ppa)

Commands required:

    sudo add-apt-repository ppa:ubuntugis/ppa
    sudo add-apt-repository ppa:meshing/release
    sudo apt-get update
    sudo apt-get install qgis-plugins-meshing

If the final command fails, please download the package manually from

    http://amcg.ese.ic.ac.uk/~asc/public/qgis-plugins-meshing_1.9_all.deb

and install with

    sudo dpkg -i qgis-plugins-meshing_1.9_all.deb

(there is a fix for Precise, which is currently being processed by Launchpad)

### Development manual install

Clone the GitHub repository and use the following:

    make install

This will install the plugins for all users (and requires superpowers).
For a single-user install, use the following:

    make installlocal

Manual
------

Further information on the dependencies can be found in the manual at:
[http://amcg.ese.ic.ac.uk/~asc/public/meshing_manual.pdf](http://amcg.ese.ic.ac.uk/~asc/public/meshing_manual.pdf)

Resources for developers
------------------------

The plugins are written in Python, each being a [Python package](http://docs.python.org/2/tutorial/modules.html#packages).
A guide to developing Python plugins for QGIS is available [here](http://www.qgis.org/pyqgis-cookbook/plugins.html#plugins).
The [PyQGIS Developer Cookbook](http://www.qgis.org/pyqgis-cookbook/) is also a useful resource.

Contact
-------

The plugin developers can be contacted via [Adam Candy](http://www3.imperial.ac.uk/people/adam.candy).


Current development
-------------------

Current development focus is on a test engine to ensure the plugins are robust.



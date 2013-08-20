
##########################################################################
#  
#  QGIS-meshing plugins.
#  
#  Copyright (C) 2012-2013 Imperial College London and others.
#  
#  Please see the AUTHORS file in the main source directory for a
#  full list of copyright holders.
#  
#  Dr Adam S. Candy, adam.candy@imperial.ac.uk
#  Applied Modelling and Computation Group
#  Department of Earth Science and Engineering
#  Imperial College London
#  
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation,
#  version 2.1 of the License.
#  
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#  
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
#  USA
#  
##########################################################################

"""
This script writes the geo file. This script works with multiple domains and the surface id for that domain
is same as the id for the shape file in the shapefile. This script also respects the physical line id which 
is defined using define_id script.

This script has an option to allow the user to choose if BSpline or Line has to be used. Another option is
to enable compound lines.

"""

#import for message box to display error
#from PyQt4.QtGui import QMessageBox
import numpy as np

class geometry_writer( object ):
  """Class storing all methods associated with writing geofiles
  
  Note : Map refered to in documentation is not pythons map()
  but a list containing indices which provide a set of slices
  to another list

  """




  def GeoWriter( self ):
    """Calls geofile writing methods

    Passed data from define_ids and writes
    mapping between geofile objects and
    their components. Uses these mappings
    to write the geofile

    """

    print "Writing geo file"
    points = self.domainData.pointsList                    # : list of point ordered on shapes and parts
    lines = np.array(self.Lines)                           # : ids to lines, will be repeated
    boundIdMap = np.array(self.IdMap)                      # : this maps lines to there respective Boundry segments
    lloopMap = np.array(self.domainData.LLoopMap)          # : this maps lines to there respective line loops
    boundIds = np.array(self.BoundryIds)                   # : this is the boundry Ids mapped via boundIdMap
    shapeMap = np.array(self.domainData.ShapeMap)          # : this maps lines to there respective shapes
    regionIds = np.array(self.domainData.RegionId)         # : this is the region Ids Mapped via ShapeMap
  
    self.pointIds = self.__generatePoints(points)

    # generating mappings from objects to their components
    if self.Compound: self.IntersectMap = self.__findIntersections(lines,shapeMap)

    if self.Compound: self.CompoundMap = self.__generateCompound(boundIdMap,lloopMap,self.IntersectMap,lines.size)

    if self.Compound: self.LineLoopMap = self.__map_between_objects(self.CompoundMap,lloopMap)
    else: self.LineLoopMap = lloopMap #may work    

    if self.Compound: self.PhysicalLineMap = self.__map_between_objects(self.CompoundMap,boundIdMap)
    else: self.PhysicalLineMap = boundIdMap

    self.PlaneSurfaceMap = np.array([0] + list(self.__map_between_objects(lloopMap,shapeMap)))

    # writing to the geofile
    self.__write_method(points,lines,lloopMap,boundIds,regionIds)
  
  def __define_mapping_from_intersection(self,mapping1,mapping2):
    """Finds sections of two arrays which are equal"""
    mp1_outr = np.outer(mapping1,np.ones_like(mapping2))
    mp2_outr = np.outer(np.ones_like(mapping1),mapping2)
    mp_result_outr = np.where(mp1_outr == mp2_outr, mp2_outr, 0)
    return np.sum(mp_result_outr,axis=1)
      
      
  def __generatePoints(self,points):
    """Identifies each point with an Id based on coordinates"""
    pointIds = []
    Idno = 1
    Idmap = {}
    for i in range(len(points)):
      if not (points[i] in points[:i]):
        pointIds += [Idno]
        Idmap[tuple(points[i])] = Idno
        Idno += 1
      else:
        pointIds += [Idmap[tuple(points[i])]]
    return pointIds    
          
  def __findIntersections(self,lines,shapeMap):
    """Determines which lines are shared by multiple shapes"""
    IntersectMap = []
    for s1_Id in range(len(shapeMap)-1):
      for s2_Id in range(len(shapeMap)-1):
        if s1_Id == s2_Id:
          continue
          IntersectMap += [self._define_mapping_from_intersection(lines[shapeMap[s1_Id]:shapeMap[s1_Id+1]],lines[shapeMap[s2_Id]:shapeMap[s2_Id+1]])]
    IntersectMap = np.array(IntersectMap + [len(lines)])
    return np.array([0] + list(IntersectMap[np.nonzero(IntersectMap)]))
      
  def __generateCompound(self,boundIdMap,lloopMap,IntersectMap,line_size):
    """Generates Mapping between compounds and lines

    Splits list of lines into the minimum
    number of segments such that no section
    is split by one of the intersect Maps     

    """
    CompoundMap = []
    end = False
    Id = 1
    LLnum = 0
    IntersectNum = 0
    BoundIdNum = 0
    while not end:
      n = np.min([boundIdMap[BoundIdNum],lloopMap[LLnum],IntersectMap[IntersectNum]])
      if IntersectMap[IntersectNum] in CompoundMap: continue

      if n == IntersectMap[IntersectNum]: IntersectNum += 1
      if n == lloopMap[LLnum]: LLnum += 1
      if n == boundIdMap[BoundIdNum]: BoundIdNum += 1
      if (n == line_size): end = True

      CompoundMap += [n]
    return np.array(CompoundMap) 
      
  def __map_between_objects(self,ComponentObjects,LineMap):
    """Generates a Mapping between Maps
    
    Generates a new Map which slices 
    ComponentObjects such that each slice
    corrisponds to the subsets of one
    member of LineMap
    
    """
    ObjectMap = []
    for line_Id in LineMap:
      ObjectMap += [np.sum(np.where(ComponentObjects == line_Id,1,0)*np.arange(ComponentObjects.size))]
    return np.array(ObjectMap)
    

  def __write_method(self,points,lines,lloopMap,boundIds,regionIds):

    """calls the methods which write to the geofile"""
  
    #start writing to file
    self.geofile_inst = open(self.geofilepath,'w')

    #write points
    prev_pointId = 0
    for i in range(len(points)):
      if prev_pointId >= self.pointIds[i]:
        continue
      self.geofile_inst.write("Point(%i) = {%s,0};\n"%(self.pointIds[i], str(points[i])[1:-1]))
      prev_pointId += 1

    #write lines  
    repeatList = []
    Allocated = 0
    LoopNo = 1
    for i in range(len(lines)):
      if i == lloopMap[LoopNo]:
        LoopNo += 1
      if lines[i] <= Allocated:
        continue
      if self.pointIds[i + LoopNo - 1] == self.pointIds[i + LoopNo]:
        repeatList += [lines[i]]
        continue
      self.geofile_inst.write("Line(%i) = {%s};\n" %( lines[i],str([self.pointIds[i + LoopNo - 1],self.pointIds[i + LoopNo]])[1:-1]))
      Allocated += 1
    print 'lines written'


    #print repeatList

    #write compounds
    cLineNo = Allocated + 1 + len(repeatList)
    if self.Compound:
      cLineNo, llrepeatList = self.__write_line_objects(cLineNo,self.CompoundMap,"Compound Line(%i) = {%s};\n",lines,0,repeatList)
      print 'compound lines written'    

    #write line loops
    if self.Compound: Components = np.arange(self.CompoundMap.size);ComponentIdStart = lines.size + 1;
    else: Components = lines;ComponentIdStart = 0;llrepeatList = repeatList
    
    cLineNo, planrepeatList = self.__write_line_objects(cLineNo,self.LineLoopMap,"Line Loop(%i) = {%s};\n",Components,ComponentIdStart,llrepeatList)
    print 'line loops written'      
  
    #write physical lines
    if self.Compound: Components = np.arange(self.CompoundMap.size);ComponentIdStart = lines.size + 1
    else: 
      Components = lines;ComponentIdStart = 0
      mask = np.ones_like(Components)
      for iD in repeatList:
        mask = np.where(Components==iD,0,mask)
      mask = mask*np.arange(mask.size)
      mask = np.array([0]+list(mask[np.nonzero(mask)]))
      Components = lines[mask]
    self.__write_physical_objects(boundIds,self.PhysicalLineMap,"Physical Line(%i) = {%s};\n",Components,ComponentIdStart)
    print 'physical lines written'    

    #write plane surfaces
    cLineNo = 1
    if self.Compound: ComponentIdStart = lines.size + self.CompoundMap.size
    else: ComponentIdStart = lines.size + 1
    self.__write_line_objects(cLineNo,self.PlaneSurfaceMap,"Plane Surface(%i) = {%s};\n",np.arange(lloopMap.size),ComponentIdStart,planrepeatList)
    print 'plane surfaces written'  

    #write physical surfaces
    self.__write_physical_objects(regionIds,self.PlaneSurfaceMap,"Physical Surface(%i) = {%s};\n",np.arange(1),1)
    print 'physical surfaces written'

    self.geofile_inst.write('\nMesh.RemeshAlgorithm=1;')

    self.geofile_inst.close()
    print "geo file written : " + self.geofilepath

  def __write_line_objects(self,cLineNo,ObjectMap,ObjectString,Components,ComponentIdStart,repeatList):
    """writes the gmsh objects which are not physical"""
    ObjectrepeatList = []

    for i in range(len(ObjectMap)-1):
      basear = Components[ObjectMap[i]:ObjectMap[i+1]]

      mask = np.ones_like(basear)
      for iD in repeatList:
        mask = np.where(basear==(iD-ComponentIdStart),0,mask)
      validindex = mask*np.arange(mask.size)
      
      validindex = validindex[np.nonzero(validindex)]
      
      if mask[0] == 1:
        validindex = np.array([0]+list(validindex))
      
      try:
        basear[validindex][0]
      except:
        ObjectrepeatList += [cLineNo]
        cLineNo += 1
        continue      
      self.geofile_inst.write(ObjectString % (cLineNo,str(list(basear[validindex]  + ComponentIdStart))[1:-1]))
      cLineNo += 1
    return cLineNo, ObjectrepeatList


  def __write_physical_objects(self,IdValues,ObjectMap,ObjectString,Components,ComponentIdStart):
    """writes the gmsh objects which are physical"""
    IdsAllocated = []
    cId = IdValues[0]

    while True:

      WithId = []
      for i in range(ObjectMap.size-1):
        if IdValues[i] != cId:
          continue
        WithId += list(Components[ObjectMap[i]:ObjectMap[i+1]]+ComponentIdStart)
      self.geofile_inst.write(ObjectString  % (cId,str(WithId)[1:-1]))
      IdsAllocated += [cId]

      for i in range(ObjectMap.size-1):
        if not (IdValues[i] in IdsAllocated):
          cId = IdValues[i]
          break

      if cId in IdsAllocated:
        break

 
"""
This method uses a text file generated by the data given from the define id script.
"""
def test_with_txt_file():
  filepath = "shapefile_data_simplified.txt"
  data = open(filepath,"r")
  lines = data.readlines()
  data = [lines[1],lines[4],lines[7],lines[10]]
  data = map(eval,data)
  write_geo_file("antartica_multiple_domain.geo",data)

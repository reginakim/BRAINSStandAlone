import os
import sys
import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function
import ConfigurationParser

from nipype import config
config.enable_debug_mode()

workflow = pe.Workflow( name = 'balancedTraning' )
workflow.base_dir = '.'

initialConfigurationFilename = "/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/tempTest.config"

#-------------------------------- argument parser
import argparse
argParser = argparse.ArgumentParser( description ='10-cross validation command line argument parser')

argParser.add_argument( '--configurationFilename',    help="""configurationFilename
                                                           Configuration file name with FULL PATH""", 
                        dest='configurationFilename', required=True )
args = argParser.parse_args()

#
# TODO: Add Config File Generator basedon on Exp Dir
#
configurationMap = ConfigurationParser.ConfigurationSectionMap( args.configurationFilename) 
ROIDict = configurationMap[ 'ROI' ]
roiList = ROIDict[ 'roiList'.lower() ]
#
#--------------------------------  start from generate probability
#
probabilityMapGeneratorND = pe.Node( name = "probabilityMapGeneratorND",
                                     interface = Function( 
                                         input_names = ['configurationFilename',
                                                        'probabilityMapList'],
                                         output_names = [ 'probabilityMapList' ],
                                         function     = ConfigurationParser.BRAINSCutGenerateProbabilityMap )
                                   )
probabilityMapGeneratorND.inputs.configurationFilename = args.configurationFilename 
probabilityMapGeneratorND.inputs.probabilityMapList = roiList.values()

workflow.add_nodes( [probabilityMapGeneratorND] )

#
#--------------------------------  create vectors for each ROI
#
configFileND = pe.Node( name = "configFileND",
                        interface = Function(
                            input_names = ['originalFilename',
                                           'editedFilenamePrefix' ],
                            output_names = ['editiedFilenames'],
                            function     = ConfigurationParser.ConfigurationFileEditor ) 
                      )

configFileND.inputs.originalFilename = args.configurationFilename  
configFileND.inputs.editedFilenamePrefix = 'ROI'
workflow.add_nodes( [ configFileND ] )

vectorCreatorND = pe.MapNode( name = "vectorCreatorND", 
                              interface = Function(
                                  input_names = ['configurationFilename',
                                                 'probabilityMapList'],
                                  output_names = ['outputVectorFilename',
                                                  'outputVectorHdrFilename'],
                                  function     = ConfigurationParser.BRAINSCutCreateVector ),
                              iterfield = [ 'configurationFilename']
                            )
#
#--------------------------------  workflow connections
#
workflow.connect( configFileND, 'editiedFilenames',
                  vectorCreatorND, 'configurationFilename' )
workflow.connect( probabilityMapGeneratorND, 'probabilityMapList',
                  vectorCreatorND, 'probabilityMapList' )

#
#--------------------------------  balance and combine each ROI vectors
#
balaceND = pe.Node( name = "balanceND",
                    interface = Function(
                        input_names = ['inputVectorFilenames'],
                        output_names = ['outputVectorFilenames'],
                        function = ConfigurationParser.BalanceInputVectors )
                  )
workflow.connect( vectorCreatorND, 'outputVectorFilename',
                  balaceND, 'inputVectorFilenames' )

combineND = pe.Node( name = "combineND",
                     interface = Function(
                        input_names = ['inputVectorFilenames',
                                       'outputVectorFilename'],
                        output_names = ['outputVectorFilename',
                                        'outputVectorHdrFilename'],
                        function = ConfigurationParser.CombineInputVectors )
                   )
workflow.connect( balaceND, 'outputVectorFilenames',
                  combineND, 'inputVectorFilenames')

combineND.inputs.outputVectorFilename = 'allCombinedVector.txtANN'
#
#
##workflow.run(updatehash=True)
workflow.run()

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
OptionsDict      = configurationMap[ 'Options' ]
roiDict          = OptionsDict[ 'roiBooleanCreator'.lower() ]
#
#--------------------------------  start from generate probability
#
probabilityMapGeneratorND = pe.Node( name = "probabilityMapGeneratorND",
                                     interface = Function( 
                                         input_names = ['configurationFilename',
                                                        'probabilityMapDict',
                                                        'outputXmlFilename'],
                                         output_names = [ 'probabilityMapDict'],
                                         function     = ConfigurationParser.BRAINSCutGenerateProbabilityMap )
                                   )
myProbDict = {}
for roi in roiDict.iterkeys():
    myProbDict[ roi ] = roi + '_probabilityMap.nii.gz'

probabilityMapGeneratorND.inputs.outputXmlFilename = 'netConfiguration.xml'
probabilityMapGeneratorND.inputs.configurationFilename = args.configurationFilename 
probabilityMapGeneratorND.inputs.probabilityMapDict = myProbDict

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
                                                 'probabilityMapDict',
                                                 'outputXmlFilename',
                                                 'outputVectorFilename'],
                                  output_names = ['outputVectorFilename',
                                                  'outputVectorHdrFilename'],
                                  function     = ConfigurationParser.BRAINSCutCreateVector ),
                              iterfield = [ 'configurationFilename']
                            )
vectorCreatorND.inputs.outputVectorFilename = 'oneROIVectorFile.txt'
vectorCreatorND.inputs.outputXmlFilename = 'oneROICreateVectorNetConfiguration.txt'
#
#--------------------------------  workflow connections
#
workflow.connect( configFileND, 'editiedFilenames',
                  vectorCreatorND, 'configurationFilename' )
workflow.connect( probabilityMapGeneratorND, 'probabilityMapDict',
                  vectorCreatorND, 'probabilityMapDict' )

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
#--------------------------------  train
#
trainND = pe.Node( name = "trainND", 
                   interface = Function( 
                       input_names = ['configurationFilename',
                                      'inputVectorFilename',
                                      'outputModelFilenamePrefix',
                                      'outputXmlFilename',
                                      'methodParameter'],
                       output_names = ['outputTrainedModelFilename'],
                       function = ConfigurationParser.BRAINSCutTrainModel )
                 )
methodParameter = { '--method': 'RandomForest',
                    '--numberOfTrees': 60,
                    '--randomTreeDepth ': 60 }
trainND.inputs.methodParameter = methodParameter
trainND.inputs.outputXmlFilename = 'trianNetConfiguration.xml'
trainND.inputs.configurationFilename = args.configurationFilename
trainND.inputs.outputModelFilenamePrefix = 'trainModelFile.txt'

workflow.connect( combineND, 'outputVectorFilename',
                  trainND, 'inputVectorFilename')


#
#
##workflow.run(updatehash=True)
workflow.run()

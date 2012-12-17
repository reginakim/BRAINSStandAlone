def getProbabilityMapFilename( roiList):
    probabilityMapFilename = {}
    for roi in roiList:
        probabilityMapFilename[roi] = roi + "_probabilityMap.nii.gz" 
    return probabilityMapFilename


def unitWorkUp ( configurationFilename, 
                 doApply = False,
                 baseDir = "."):
    import os
    import sys
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function
    import ConfigurationParser
    import crossValidationUnit as this
    
    from nipype import config
    config.enable_debug_mode()
    
    workflow = pe.Workflow( name = 'balancedTraning' )
    workflow.base_dir = baseDir
    
    #
    # TODO: Add Config File Generator basedon on Exp Dir
    #
    configurationMap = ConfigurationParser.ConfigurationSectionMap( configurationFilename) 
    Options          = configurationMap[ 'Options' ]
    roiDict          = Options[ 'roiBooleanCreator'.lower() ]

    filenameGeneratorND = pe.Node( name      = "filenameGeneratorND",
                                   interface = Function( 
                                      input_names  = ['roiList'],
                                      output_names = ['probabilityMapFilename'],
                                      function     = this.getProbabilityMapFilename )
                                 )
    filenameGeneratorND.inputs.roiList = roiDict.keys()

    #
    #--------------------------------  start from generate probability
    #
    probabilityMapGeneratorND = pe.Node( name = "probabilityMapGeneratorND",
                                         interface = Function( 
                                             input_names = ['configurationFilename',
                                                            'probabilityMapDict',
                                                            'outputXmlFilename'],
                                             output_names = [ 'probabilityMapDict',
                                                              'outputXmlFilename'],
                                             function     = ConfigurationParser.BRAINSCutGenerateProbabilityMap )
                                       )
    
    probabilityMapGeneratorND.inputs.outputXmlFilename = 'netConfiguration.xml'
    probabilityMapGeneratorND.inputs.configurationFilename = configurationFilename 
    
    workflow.connect( filenameGeneratorND, 'probabilityMapFilename',
                      probabilityMapGeneratorND, 'probabilityMapDict' )
    
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
    
    configFileND.inputs.originalFilename = configurationFilename  
    configFileND.inputs.editedFilenamePrefix = 'ROI'
    workflow.add_nodes( [ configFileND ] )
    
    vectorCreatorND = pe.MapNode( name = "vectorCreatorND", 
                                  interface = Function(
                                      input_names = ['configurationFilename',
                                                     'probabilityMapDict',
                                                     'outputXmlFilename',
                                                     'outputVectorFilename'],
                                      output_names = ['outputVectorFilename',
                                                      'outputVectorHdrFilename',
                                                      'outputXmlFilename'],
                                      function     = ConfigurationParser.BRAINSCutCreateVector ),
                                  iterfield = [ 'configurationFilename']
                                )
    vectorCreatorND.inputs.outputVectorFilename = 'oneROIVectorFile.txt'
    vectorCreatorND.inputs.outputXmlFilename = 'oneROICreateVectorNetConfiguration.xml'
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
                            output_names = ['outputVectorFilenames',
                                            'outputVectorHdrFilenames'],
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
    trainND.inputs.configurationFilename = configurationFilename
    trainND.inputs.outputModelFilenamePrefix = 'trainModelFile.txt'
    
    workflow.connect( combineND, 'outputVectorFilename',
                      trainND, 'inputVectorFilename')
    
    #
    #--------------------------------  apply
    #
    # make output dir for each subject as a 
    if doApply:
        from XMLConfigurationGenerator import combineCSVs
        listFiles = configurationMap[ 'ListFiles' ]
        print( listFiles )
        print( listFiles )
        print( listFiles )
        print( listFiles )
        print( listFiles )
        applyDict = combineCSVs( listFiles['applySubjectListFilename'.lower()], 
                                 listFiles['applyFeatureListFileDictionary'.lower()] )
        outputDirDict = {}
        for sessionID in applyDict.iterkeys():
            outputDirDict[ sessionID ] = 'apply_'+sessionID
              
        print ( outputDirDict )
        print ( outputDirDict )
        print ( outputDirDict )
        print ( outputDirDict )
        print ( outputDirDict )
        
        applyND = pe.Node( name = "applyND", 
                           interface = Function( 
                               input_names = ['configurationFilename',
                                              'probabilityMapDict',
                                              'inputModelFilename',
                                              'outputXmlFilename',
                                              'outputDirDict',
                                              'methodParameter'],
                               output_names = ['outputLabelDict'],
                               function = ConfigurationParser.BRAINSCutApplyModel )
                         )
        methodParameter = { '--method': 'RandomForest',
                            '--numberOfTrees': 60,
                            '--randomTreeDepth ': 60 }
        applyND.inputs.methodParameter = methodParameter
        applyND.inputs.outputXmlFilename = 'applyConfiguration.xml'
        applyND.inputs.configurationFilename = configurationFilename
        applyND.inputs.outputDirDict = outputDirDict
        
        workflow.connect( probabilityMapGeneratorND, 'probabilityMapDict',
                          applyND, 'probabilityMapDict' )
        workflow.connect( trainND, 'outputTrainedModelFilename',
                          applyND, 'inputModelFilename' )
    
    #
    #
    ##workflow.run(updatehash=True)
    workflow.run()
    
def main(argv=None):
    #-------------------------------- argument parser
    import argparse
    argParser = argparse.ArgumentParser( description ='10-cross validation command line argument parser')
    
    argParser.add_argument( '--configurationFilename',    help="""configurationFilename
                                                               Configuration file name with FULL PATH""", 
                            dest='configurationFilename', required=True )
    argParser.add_argument( '--doApply',    help="""doApply
                                                    """, 
                            dest='doApply', required=False, default=False )
    argParser.add_argument( '--baseDir',    help="""baseDir
                                                    """, 
                            dest='baseDir', required=False, default="." )
    args = argParser.parse_args()
    
    unitWorkUp( args.configurationFilename,
                args.doApply,
                args.baseDir)

if __name__ == "__main__":
    import sys
    sys.exit(main())

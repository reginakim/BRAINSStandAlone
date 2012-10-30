

## start {
def WFPerSubjectDef ( inputListOfSubjectVolumes, 
                      inputTemplateDir,
                      outputCacheDir,
                      outputResultsDir):

  #
  # workflow definition
  #
  import nipype.pipeline.engine as pe
  
  WFPerSubject = pe.Workflow(name="subject")
  WFPerSubject.base_dir = outputCacheDir
  
  import nipype.interfaces.io as nio
  datasink = pe.Node( nio.DataSink(), name = 'sinker' )
  datasink.inputs.base_directory = ( outputResultsDir ) 
  
  datasink.inputs.regexp_substitutions = [ ('_inputVolume.*BABC..', '') ,
                                           ('_Cache',''),
                                           ('.nii.gz/', ''),
                                           ('_inputMethod_',''),
                                           ('/Normalized','_Normalized'),
                                           ('_inputROI_',''),]
  
  # --------------------------------------------------------------------------------------- #
  # 1. Deform atlas to subject with really gross transform
  #
  from BRAINSFit import BRAINSFit
  
  inputTemplateT1 = inputTemplateDir + "/template_t1.nii.gz"
  
  BFitAtlasToSubject_Node = pe.Node( interface=BRAINSFit(),
                                name="01_AtlasToSubjectRegistration")
  
  BFitAtlasToSubject_Node.inputs.fixedVolume           = inputListOfSubjectVolumes['t1']
  BFitAtlasToSubject_Node.inputs.movingVolume          = inputTemplateT1
  BFitAtlasToSubject_Node.inputs.outputVolume          = "atlas_to_subject_warped.nii.gz"  
  BFitAtlasToSubject_Node.inputs.initialTransform      = inputListOfSubjectVolumes['transform']
  BFitAtlasToSubject_Node.inputs.outputTransform       = "atlas_to_subject.h5"  
  
  ## fixed parameter specification
  BFitAtlasToSubject_Node.inputs.costMetric = "MMI"
  BFitAtlasToSubject_Node.inputs.maskProcessingMode = "ROIAUTO"
  BFitAtlasToSubject_Node.inputs.numberOfSamples = 100000
  BFitAtlasToSubject_Node.inputs.numberOfIterations = [1500,1500,1500,1500]
  BFitAtlasToSubject_Node.inputs.numberOfHistogramBins = 50
  BFitAtlasToSubject_Node.inputs.maximumStepLength = 0.2
  BFitAtlasToSubject_Node.inputs.minimumStepLength = [0.005,0.005,0.005,0.005]
  BFitAtlasToSubject_Node.inputs.transformType = "ScaleVersor3D,ScaleSkewVersor3D,Affine,BSpline" 
  BFitAtlasToSubject_Node.inputs.relaxationFactor = 0.5  
  BFitAtlasToSubject_Node.inputs.translationScale = 1000
  BFitAtlasToSubject_Node.inputs.reproportionScale = 1  
  BFitAtlasToSubject_Node.inputs.skewScale = 1
  BFitAtlasToSubject_Node.inputs.useExplicitPDFDerivativesMode = "AUTO"  
  BFitAtlasToSubject_Node.inputs.useCachingOfBSplineWeightsMode = "ON"  
  BFitAtlasToSubject_Node.inputs.maxBSplineDisplacement = 7 
  BFitAtlasToSubject_Node.inputs.projectedGradientTolerance = 1e-05 
  BFitAtlasToSubject_Node.inputs.costFunctionConvergenceFactor = 1e+09 
  BFitAtlasToSubject_Node.inputs.backgroundFillValue = 0 
  BFitAtlasToSubject_Node.inputs.maskInferiorCutOffFromCenter = 65  
  BFitAtlasToSubject_Node.inputs.splineGridSize = [56,40,48] 
  
  ## add to workflow
  WFPerSubject.add_nodes( [BFitAtlasToSubject_Node])
  
  WFPerSubject.connect( BFitAtlasToSubject_Node, 'outputTransform',
                        datasink, '01_BFitAtlasToSubject')
  
  
  # --------------------------------------------------------------------------------------- #
  # 2. Warp Probability Maps
  #
  
  rois     = [ "l_accumben" , "l_caudate" ,"l_putamen" ,"l_globus" ,"l_thalamus" ,"l_hippocampus",
               "r_accumben" , "r_caudate" ,"r_putamen" ,"r_globus" ,"r_thalamus" ,"r_hippocampus" ]
  
  import MyUtilities  
  from nipype.interfaces.utility import Function
  GetProbabilityMapFilename_Node = pe.Node( name = "utilGetProbabilityMapFilename", 
                         interface = Function( input_names = ["inputROI", "inputDir"],
                                               output_names = ["outputFilename"],
                                               function = MyUtilities.GetProbabilityFilename ),
                         iterfield = ["inputROI"]
                        )
  GetProbabilityMapFilename_Node.iterables = ( "inputROI", rois )                        
  GetProbabilityMapFilename_Node.inputs.inputDir  = inputTemplateDir
  
  from BRAINSResample import BRAINSResample 
  WarpProbabilityMap = pe.Node( interface=BRAINSResample(), 
                                name = "02_WarpProabilityMap",
                              )
  
  WarpProbabilityMap.inputs.outputVolume    = "outputTemplateWarpedToSubject.nii.gz"
  WarpProbabilityMap.inputs.referenceVolume = inputListOfSubjectVolumes['t1']
  
  ## add to the workflow and connect
  WFPerSubject.add_nodes([ WarpProbabilityMap])
  WFPerSubject.connect( GetProbabilityMapFilename_Node , 'outputFilename',
                        WarpProbabilityMap,'inputVolume' )
  WFPerSubject.connect( BFitAtlasToSubject_Node, 'outputTransform',
                        WarpProbabilityMap,'warpTransform' )
  WFPerSubject.connect( WarpProbabilityMap, 'outputVolume',
                        datasink, '02_WarpedProbability' )

  # --------------------------------------------------------------------------------------- #
  # Smoothing 
  #
  SmoothingProbMap_Node = pe.Node( name = "SmoothProbabilityMap",
                              interface = Function( input_names = ["inputVolume",
                                                                   "sigma",
                                                                   "outputVolume"],
                                                    output_names = ["outputSmoothProbabilityMap"],
                                                    function = MyUtilities.SmoothProbabilityMap ),
                              iterfield = ["sigma"]
                            )
  SmoothingProbMap_Node.iterables = ("sigma",[0,0.5,1,1.5,2,2.5,3])
  SmoothingProbMap_Node.inputs.outputVolume = "outputSmoothProbabilityMap.nii.gz"

  WFPerSubject.connect( WarpProbabilityMap, 'outputVolume' ,
                        SmoothingProbMap_Node, 'inputVolume')


  # --------------------------------------------------------------------------------------- #
  # 3. Create Mask by Threshold
  #
  CreateMask_Node = pe.Node( name = "03_CreateMask_Node",
                        interface = Function( input_names = ["inputVolume",
                                                             "lowerThreshold",
                                                             "upperThreshold",
                                                             "outputFilename"],
                                              output_names = ["outputMask"],
                                              function =  MyUtilities.ThresholdProbabilityMap )
                        )
  
  CreateMask_Node.inputs.lowerThreshold = 0.05
  CreateMask_Node.inputs.upperThreshold = 0.95
  CreateMask_Node.inputs.outputFilename = "roiMask.nii.gz"
  
  WFPerSubject.add_nodes( [CreateMask_Node ] )
  WFPerSubject.connect( SmoothingProbMap_Node, 'outputSmoothProbabilityMap',
                        CreateMask_Node, 'inputVolume')
  
  WFPerSubject.connect( CreateMask_Node, 'outputMask',
                        datasink, '03_ROI' )
  
  # --------------------------------------------------------------------------------------- #
  # 4. Compute Statistice 
  #
  LabelStatistics_Node = pe.Node( name = "04_LabelStatistics",
                             interface = Function( input_names = ["inputLabel",
                                                                  "inputVolume",
                                                                  "outputCSVFilename"],
                                                   output_names = ["outputCSVFilename",
                                                                   "outputDictionarySet"],
                                                   function = MyUtilities.LabelStatistics ),
                             iterfield = ["inputVolume"]
                            )
  LabelStatistics_Node.iterables  = ("inputVolume", [ inputListOfSubjectVolumes['t1'], 
                                                 inputListOfSubjectVolumes['t2']]
                               )
  LabelStatistics_Node.inputs.outputCSVFilename = "labelStatistics.csv"
  
  WFPerSubject.add_nodes( [LabelStatistics_Node] )
  
  WFPerSubject.connect( CreateMask_Node, "outputMask",
                        LabelStatistics_Node, "inputLabel" )
  
  WFPerSubject.connect( LabelStatistics_Node, 'outputCSVFilename',
                        datasink, 'labelStatistics')

   
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  print LabelStatistics_Node.outputs.outputCSVFilename
  #return LabelStatistics_Node.outputs.outputCSVFilename

  # --------------------------------------------------------------------------------------- #
  # 5. Linear Transform based on local statistics  and get statistics 
  #
  # Statistics has to be computed only for the ROI that applies 

  NormalizationMethods = ['zScore', 
                          'MAD',
                          'DoubleSigmoid',
                          'Sigmoid',
                          'QEstimator',
                          'Linear']

  NormalizeAndGetStatofROI_Node  = pe.Node( name = "05_NormalizeStats",
                                            interface = Function( input_names = ['inputSet_LabelStat',
                                                                                 'inputMethod',
                                                                                 'outputVolume',
                                                                                 'outputCSVFilename' ],
                                                                  output_names = ['outputCSV',
                                                                                  'outputVolume'],
                                                        function = MyUtilities.NormalizeAndComputeStatOfROI ),
                                            iterfield = ['inputMethod']
                                          )
  # inputs
  NormalizeAndGetStatofROI_Node.iterables = ('inputMethod', NormalizationMethods )
  NormalizeAndGetStatofROI_Node.inputs.outputVolume = "NormalizedVolume.nii.gz"
  NormalizeAndGetStatofROI_Node.inputs.outputCSVFilename = "NormalizedVolumeStats.csv"
  # connect to the work flow
  WFPerSubject.add_nodes( [NormalizeAndGetStatofROI_Node] )
  WFPerSubject.connect( LabelStatistics_Node, 'outputDictionarySet',
                        NormalizeAndGetStatofROI_Node, 'inputSet_LabelStat')
  
  # datasink
  WFPerSubject.connect( NormalizeAndGetStatofROI_Node, 'outputCSV',
                        datasink, 'labelStatistics.@Stat')

  WFPerSubject.connect( NormalizeAndGetStatofROI_Node, 'outputVolume',
                        datasink, 'labelStatistics.@Volume')


  WFPerSubject.run()
  WFPerSubject.write_graph(graph2use='orig')
  ## end }





## main
#
# command line argument specification
#
#import argparse
#
#robustStatArgParser = argparse.ArgumentParser( description = "robust stat. argument")
#
#robustStatArgParser.add_argument('--inputSubjectT1', help='input subject average t1', 
#                                 required=True)
#robustStatArgParser.add_argument('--inputSubjectT2', help='input subject average t2', 
#                                 required=True)
#robustStatArgParser.add_argument('--inputInitialTransform', help='input initial trasnform from atlas to subject', 
#                                 required=True)
#robustStatArgParser.add_argument('--inputTemplateDir', help='input template directory', 
#                                 required=True)
#robustStatArgParser.add_argument('--outputDir',      help="output directory for the workflow", 
#                                 required=True)
#
#cmdArgs = robustStatArgParser.parse_args()
#
#WFPerSubject( cmdArgs.inputSubjectT1, 
#              cmdArgs.inputSubjectT2,
#              cmdArgs.inputInitialTransform,
#              cmdArgs.inputTemplateDir,
#              cmdArgs.outputDir )


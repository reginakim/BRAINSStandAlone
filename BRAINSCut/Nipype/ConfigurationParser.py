
#########################################################################################
def ConfigurationSectionMap( configurationFilename ):
    print( """Executing 
           ConfigurationSectionMap ::: {fn}
           """.format( fn=configurationFilename) )
    import sys
    import os
    import ConfigParser
    import ast
    
    if os.path.exists( configurationFilename ):
        pass 
    else:
        print("""ERROR in ConfigurationSectionMap
              file "{fn}" does not exist!
              """.format( fn = configurationFilename ) )
        sys.exit()
              
    dictionaryListSet = set( ["roilist", 
                              "roibooleancreator",
                              "featurelistfiledictionary",
                              "applyFeatureListFileDictionary".lower(),
                              'numberOfElementInSubset'.lower() ]
                              )

    m_configuration = ConfigParser.ConfigParser()
    print( """READ
           {fn}.""".format( fn = configurationFilename ))
    m_configuration.read ( configurationFilename );

    returnDict= {}

    for section in m_configuration.sections():
        print( """
               porcessing section : {sc}""".format( sc= section ))
        sectionDict = {}
        for option in m_configuration.options( section ):
            try:
                if option in dictionaryListSet:
                    sectionDict[ option ] = ast.literal_eval( m_configuration.get( section, option ) )
                else:
                    sectionDict[ option ] = m_configuration.get( section, option ) 
                print( "{option} ==>  {value}".format( option=option, 
                                                       value= sectionDict[ option ]  ))
            except:
                print("""exception on 
                      %s""" % option )
                print "Unexpected error:", sys.exc_info()[0]
                sectionDict[option]=None
        returnDict[ section ] = sectionDict;
    return returnDict 

#########################################################################################
def BRAINSCutCMDFromConfigFile( configurationFilename,
                                xmlFilename, 
                                probabilityMapDict, 
                                vectorFilename,
                                modelFilename, 
                                generateProbabilityMap,
                                createVectors,
                                trainModel, 
                                applyModel,
                                applyModelOutputDirDict,
                                methodParameter):
    from ConfigurationParser import ConfigurationSectionMap
    configurationMap = ConfigurationSectionMap( configurationFilename )
    
    ## parse dictionary and list
    atlasDict = configurationMap[ 'AtlasDescription' ]
    m_templateDict = { 't1':atlasDict['t1'] }
    m_spatialDescriptionDict = { 'rho':   atlasDict['rho'],
                                 'phi':   atlasDict['phi'], 
                                 'theta': atlasDict['theta'] }
    ##
    ## note on *lower()*
    ## all the options are converted to lower case with ConfigParser xOptions
    listFiles = configurationMap[ 'ListFiles' ]
    if applyModel:
        subjectListFilename = listFiles[ 'applySubjectListFilename'.lower()]
        featureListFileDict = listFiles['applyFeatureListFileDictionary'.lower()]
    else:
        subjectListFilename = listFiles[ 'subjectListFilename'.lower() ]
        featureListFileDict = listFiles['featureListFileDictionary'.lower()]
        print ( """featureListFileDict:::
                {fn}
                """.format( fn=featureListFileDict))


    optionsDict = configurationMap[ 'Options' ]
    #ROIDict = configurationMap[ 'ROI' ] 

    #for key in outputXmlFilenameiterkeys():
    #    print ("{key} ==> {value}".format( key=key, value=m_fileDescriptions[key] ) )
    
    from XMLConfigurationGenerator import xmlGenerator

    import os
    p_probMapDict = {}
    for roi in probabilityMapDict.iterkeys():
        p_probMapDict[ roi ] = os.path.abspath( probabilityMapDict[ roi ] )
    
    p_vectorFilename = os.path.abspath( vectorFilename )
    p_modelFilename = os.path.abspath( modelFilename )
    p_xmlFilename = os.path.abspath( xmlFilename )
    p_applyModelOutputDirDict = {}
    for sessionID in applyModelOutputDirDict.iterkeys():
        p_applyModelOutputDirDict[ sessionID ] = os.path.abspath( applyModelOutputDirDict[ sessionID ] )

    returnList= xmlGenerator( m_templateDict,
                              m_spatialDescriptionDict,
                              p_vectorFilename, 
                              optionsDict[ 'roiBooleanCreator'.lower() ] ,
                              p_modelFilename, 
                              p_probMapDict,
                              optionsDict[ 'imageTypeToUse'.lower() ],
                              subjectListFilename,
                              p_xmlFilename,
                              optionsDict[ 'normalization' ] ,
                              optionsDict[ 'gaussianSigma'.lower() ],
                              featureListFileDict,
                              applyModel,
                              p_applyModelOutputDirDict)
    optionStr = ""
    for option in methodParameter.iterkeys():
        optionStr = optionStr + " {option} {value} ".format(option=option, value=methodParameter[ option ] )

    import subprocess
    if generateProbabilityMap:
        print ("generateProbabilityMap")
        print ("generateProbabilityMap")
        print ("generateProbabilityMap")
        BRAINSCutCommand=["BRAINSCut" + " --generateProbability" +
                          " --netConfiguration " + p_xmlFilename 
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
    if createVectors:
        BRAINSCutCommand=["BRAINSCut" + " --createVectors" +
                          " --netConfiguration " + p_xmlFilename 
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
    if trainModel:
        BRAINSCutCommand=["BRAINSCut" + " --trainModel" +
                          " --netConfiguration " + p_xmlFilename +
                          optionStr
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
    if applyModel:
        BRAINSCutCommand=["BRAINSCut" + " --applyModel" +
                          " --netConfiguration " + p_xmlFilename +
                          optionStr +
                          " --modelFilename " + p_modelFilename
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
        
    return returnList
    
#########################################################################################
def BRAINSCutGenerateProbabilityMap( configurationFilename,
                                     probabilityMapDict,
                                     outputXmlFilename):
    generateProbabilityMap = True
    createVectors = False
    trainModel = False
    applyModel = False
    dummyMethodParameter= {}

    print( """generate probability map
           {str}
           """.format( str=probabilityMapDict) )

    import os
    for roi in probabilityMapDict.iterkeys():
        print( os.path.abspath( probabilityMapDict[ roi ] ) )
        probDir = os.path.dirname( os.path.abspath( probabilityMapDict[ roi ] ) )
        if not os.path.exists( probDir ):
            os.mkdirs( probDir )
    dummyFilename = "na"
    dummyDict = {}
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                outputXmlFilename,
                                probabilityMapDict,
                                dummyFilename,
                                dummyFilename,
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                dummyDict,
                                dummyMethodParameter)
    returnProbMapList = returnList[ 'probabilityMap' ]
    import sys
    if returnProbMapList.keys() != probabilityMapDict.keys():
        print("""ERROR
              returnProbMapList has to match probabilityMapDict
              in BRAINSCutGenerateProbabilityMap
              """)
        sys.exit()
          
    outputXmlFilename = os.path.abspath( outputXmlFilename   )
    return returnProbMapList, outputXmlFilename 
                                
#########################################################################################
def BRAINSCutCreateVector( configurationFilename, 
                           probabilityMapDict,
                           outputXmlFilename,
                           outputVectorFilename):
    print( BRAINSCutCreateVector )
    print( BRAINSCutCreateVector )
    print( BRAINSCutCreateVector )
    print( BRAINSCutCreateVector )
    print( BRAINSCutCreateVector )
    print( BRAINSCutCreateVector )
    import os.path
    import sys
    for roi in probabilityMapDict.iterkeys():
        if not os.path.exists( probabilityMapDict[ roi ]  ):
            print( """ ERROR   
                   {fn}  does not exist.
                   """.format( fn=probabilityMapDict[roi]) )
            sys.exit()

    generateProbabilityMap = False
    createVectors = True
    trainModel = False
    applyModel = False
    dummyMethodParameter = {}
    dummyOutputDirDict = {}
    dummyModelFilename = "na"
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                outputXmlFilename, 
                                probabilityMapDict,
                                outputVectorFilename,
                                dummyModelFilename, 
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                dummyOutputDirDict, 
                                dummyMethodParameter)
    outputVectorFilename = returnList[ 'inputVectorFilename' ]    
    outputVectorHdrFilename = outputVectorFilename + ".hdr"
    outputXmlFilename = os.path.abspath( outputXmlFilename )
    return outputVectorFilename, outputVectorHdrFilename, outputXmlFilename

#########################################################################################
def BRAINSCutTrainModel( configurationFilename, 
                         inputVectorFilename, 
                         outputModelFilenamePrefix, 
                         outputXmlFilename,
                         methodParameter
                       ):
    import os.path
    import sys

    generateProbabilityMap = False
    createVectors = False
    trainModel = True
    applyModel = False
    dummyProbMapDict = {}

    p_inputVectorFilename = os.path.abspath( inputVectorFilename )
    p_inputVectorFilename = p_inputVectorFilename[:-3] # truncate ANN
    print( p_inputVectorFilename )
    print( p_inputVectorFilename )
    print( p_inputVectorFilename )
    print( p_inputVectorFilename )
    print( p_inputVectorFilename )
    print( p_inputVectorFilename )
    print( p_inputVectorFilename )

    p_outputModelFilenamePrefix = os.path.abspath( outputModelFilenamePrefix )
    dummyOutputDirDict = {}
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                outputXmlFilename,
                                dummyProbMapDict,
                                p_inputVectorFilename, 
                                p_outputModelFilenamePrefix, 
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                dummyOutputDirDict,
                                methodParameter )

    outputModelFileSearchStr=p_outputModelFilenamePrefix + "*" + str(methodParameter['--numberOfTrees']) + "*" + "*gz"
    import glob
    trainedModelFile = glob.glob( outputModelFileSearchStr ) 
    return trainedModelFile[0]

#########################################################################################
def BRAINSCutApplyModel( configurationFilename, 
                         probabilityMapDict,
                         inputModelFilename,
                         outputXmlFilename, 
                         outputDirDict,
                         methodParameter):
    import os.path
    import sys
    p_probMapDict = {}
    for roi in probabilityMapDict.iterkeys():
        if not os.path.exists( probabilityMapDict[ roi ] ):
            print( """ ERROR   
                   probabilityMapDict[ roi ]  does not exist.
                   """ )
            sys.exit()
        p_probMapDict[ roi ] = os.path.abspath( probabilityMapDict[ roi ] )

    generateProbabilityMap = False
    createVectors = False
    trainModel = False
    applyModel = True
    dummyInputVectorFilename =""
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                outputXmlFilename, 
                                p_probMapDict,
                                dummyInputVectorFilename, 
                                inputModelFilename,
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                outputDirDict,
                                methodParameter)
    outputLabelDict = returnList[ 'outputLabelDict' ] 

    return outputLabelDict 
     
#########################################################################################
def updating(originalFilename, 
             editedFilename, 
             whatToChangeDict):
    import ConfigParser

    inConfigParser = ConfigParser.ConfigParser()
    inConfigParser.read( originalFilename );

    outConfigParser = ConfigParser.RawConfigParser()

    for section in inConfigParser.sections():
        outConfigParser.add_section( section )
        for option in inConfigParser.options( section ):
            if option in whatToChangeDict:
                print("""
                      change option {op} to {value}
                      """.format( op = option, value = whatToChangeDict[ option ] ) )
                outConfigParser.set( section, option, whatToChangeDict[ option ] )
            else:
                outConfigParser.set( section, option, inConfigParser.get( section ,option) )

    with open( editedFilename, 'wb' ) as outConfigFile:
        outConfigParser.write( outConfigFile )
    import os
    return os.path.abspath( editedFilename )
    
#########################################################################################
def ConfigurationFileEditor( originalFilename, 
                             editedFilenamePrefix ):
    print( ConfigurationFileEditor )
    print( ConfigurationFileEditor )
    print( ConfigurationFileEditor )
    print( ConfigurationFileEditor )
    varToChange= [ 'roiBooleanCreator'.lower()]

    from ConfigurationParser import ConfigurationSectionMap
    from ConfigurationParser import updating 
    Options = ConfigurationSectionMap( originalFilename )['Options']
    roiDict = Options[ 'roiBooleanCreator'.lower() ]

    new_ROIDictTemplate = roiDict.copy()
    for key in new_ROIDictTemplate:
        new_ROIDictTemplate[ key ] = 'false'

    editedFilenames = {}
    for roi in roiDict.iterkeys():
        new_ROIDict = new_ROIDictTemplate.copy() 
        new_ROIDict[ roi ] = 'true'
        #print( "{roi} set to {boolean}".format( roi=roi, boolean=new_ROIDict[roi]))
        #print( new_ROIDict )
        new_ConfigFilename = editedFilenamePrefix + "_" + roi + ".config"
        
        newValues = [ new_ROIDict ]
        whatToChange = dict( zip( varToChange, newValues ))
        editedFilenames[ roi ] = updating( originalFilename, 
                                           new_ConfigFilename, 
                                           whatToChange )

    return editedFilenames.values()

#########################################################################################
def getTVCs ( inputVectorFilenames ):
    import csv
    TVC={}
    for file in inputVectorFilenames:
        filename = file + ".hdr"
        currFile = open( filename, "rb")
        currReader = csv.reader( currFile, delimiter=" ")
        for row in currReader:
            for col in row:
                if col == "TVC":
                    TVC[ file ] = int( row[ row.index(col)+1 ] )
                    #print( "{file} = {tvc}".format( file=file, tvc=TVC[file]))
    return TVC

#########################################################################################
def BalanceInputVectors( inputVectorFilenames ):
    ## read header file
    from ConfigurationParser import getTVCs 
    TVC = getTVCs( inputVectorFilenames )
    print( TVC )
    print( TVC )
    print( TVC )
    print( TVC )
    print( TVC )
    import operator
    maxFile = max(TVC.iteritems(), key=operator.itemgetter(1))[0]
    #maxFile = max(TVC)
    print ( maxFile )
    print ( maxFile )
    print ( maxFile )
    print ( maxFile )

    maxTVC = TVC[ maxFile ]
    #print( "{file} = {tvc}".format( file=maxFile, tvc=TVC[maxFile])) 

    outputVectorFilenames = {}
    outputVectorHdrFilenames = {}
    for inFile in inputVectorFilenames:
        outputVectorFilenames[ inFile ]  = inFile + "_upsampled.txtANN"
        outputVectorHdrFilenames[ inFile ]  = inFile + "_upsampled.txtANN.hdr"
    ## upsample all other files
    import subprocess
    import os
    for inputVectorFile in inputVectorFilenames:
        upsampleCMD = ["ShuffleVectorsModule " + 
                       " --outputVectorFileBaseName " + 
                       outputVectorFilenames[ inputVectorFile ] +
                       " --inputVectorFileBaseName " + inputVectorFile  +
                       " --resampleProportion " + str( float(maxTVC) /float( TVC[ inputVectorFile ]))  ]
        print("HACK:  UPSAMPPLING: {0}".format(upsampleCMD))
        subprocess.call( upsampleCMD, shell = True)
        outputVectorFilenames[ inFile ]  = os.path.abspath( outputVectorFilenames[ inFile ] )
    
    ## return list of upsampled file names
    return outputVectorFilenames.values(), outputVectorHdrFilenames.values()

#########################################################################################
def CombineInputVectors( inputVectorFilenames,
                         outputVectorFilename):
    outFile = open( outputVectorFilename, "w")
    for inFilename in inputVectorFilenames:
        inFile = open( inFilename, "r")
        outFile.write( inFile.read() )
    outFile.close()

    from ConfigurationParser import getTVCs 
    TVC = getTVCs( inputVectorFilenames )
    newTVC = sum( TVC.values() )

    inHdrFile = open ( inputVectorFilenames[1] + ".hdr", "r")
    import os
    outHdrFilename = os.path.abspath( outputVectorFilename ) + ".hdr"
    outHdrFile = open ( outHdrFilename, "w")
     
    outHdrFile.write( inHdrFile.readline() )
    outHdrFile.write( inHdrFile.readline() )
    outHdrFile.write( "TVC {value}".format( value=newTVC))
    outHdrFile.close()

    return os.path.abspath( outputVectorFilename ), outHdrFilename 

configFileTestStr="""[AtlasDescription]
t1 =       /ipldev/scratch/eunyokim/src/BRAINSStandAlone/build_LongitudinalSegmentationPipelineTrial/ReferenceAtlas-build/Atlas/Atlas_20121120/template_t1.nii.gz
rho =      /ipldev/scratch/eunyokim/src/BRAINSStandAlone/build_LongitudinalSegmentationPipelineTrial/ReferenceAtlas-build/Atlas/Atlas_20121120/spatialImages/rho.nii.gz
phi =      /ipldev/scratch/eunyokim/src/BRAINSStandAlone/build_LongitudinalSegmentationPipelineTrial/ReferenceAtlas-build/Atlas/Atlas_20121120/spatialImages/phi.nii.gz
theta =    /ipldev/scratch/eunyokim/src/BRAINSStandAlone/build_LongitudinalSegmentationPipelineTrial/ReferenceAtlas-build/Atlas/Atlas_20121120/spatialImages/theta.nii.gz

[ROI]
roiList=  {'l_accumben'   : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/l_accumben_probaiblityMap.nii.gz',
           'l_caudate'    : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/l_caudate_probaiblityMap.nii.gz',
           'l_putamen'    : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/l_putamen_probaiblityMap.nii.gz',
           'l_globus'     : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/l_globus_probaiblityMap.nii.gz',
           'l_thalamus'   : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/l_thalamus_probaiblityMap.nii.gz',
           'l_hippocampus': '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/l_hippocampus_probaiblityMap.nii.gz',
           'r_accumben'   : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/r_accumben_probaiblityMap.nii.gz',
           'r_caudate'    : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/r_caudate_probaiblityMap.nii.gz',
           'r_putamen'    : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/r_putamen_probaiblityMap.nii.gz',
           'r_globus'     : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/r_globus_probaiblityMap.nii.gz',
           'r_thalamus'   : '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/r_thalamus_probaiblityMap.nii.gz',
           'r_hippocampus': '/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/probabilityMaps/r_hippocampus_probaiblityMap.nii.gz'}


[FileDescriptions]
xmlFilename    = /ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/output.xml
vectorFilename = /ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/vectorfile.txt
modelFilename  = /ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/modelfile.txt

[ListFiles]
subjectListFilename  = /ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/test.csv
featureListFileDictionary = {'gadSG':'/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/BRAINSCut/Nipype/testGadFeatureList.csv'}

[Options]
imageTypeToUse = t1
normalization  = Linear
roiBooleanCreator = {'l_accumben':'true',    'r_accumben':'true',
                     'l_caudate':'true',     'r_caudate':'true',
                     'l_putamen':'true',     'r_putamen':'true',
                     'l_globus':'true',      'r_globus':'true',
                     'l_thalamus':'true',    'r_thalamus':'true',
                     'l_hippocampus':'true', 'r_hippocampus':'true'
                    }

"""

#########################################################################################
def main():
    testConfigFilename='./tempTest.config'
#    with open( testConfigFilename, 'w') as f:
#        f.write( configFileTestStr )
#    f.close()
    ## Unit tests
    ConfigurationSectionMap( testConfigFilename )
#    BRAINSCutCMDFromConfigFile( testConfigFilename,
#                                False, False, False, False )

    #BRAINSCutGenerateProbabilityMap( testConfigFilename )
    #ConfigurationFileEditor( testConfigFilename,
    #                         testConfigFilename + "EDITIED")


#########################################################################################
#{#######################################################################################
# TEST

if __name__ == "__main__":
      main()
#combineCSVs("trainingBAW20120801List.csv", "gadSGFeatureList.csv")
#---------------------------------------------------------------------------------------}

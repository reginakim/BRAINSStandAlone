
#########################################################################################
def ConfigurationSectionMap( configurationFilename ):
    print( """"Executing 
           ConfigurationSectionMap""")
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
                              "featurelistfiledictionary"] )

    m_configuration = ConfigParser.ConfigParser()
    m_configuration.read ( configurationFilename );

    print( """ * read
           {fn}""".format( fn=configurationFilename ))

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
                                generateProbabilityMap,
                                createVectors,
                                trainModel, 
                                applyModel,
                                rfTreeNumber,
                                rfTreeDepth):
    from ConfigurationParser import ConfigurationSectionMap
    configurationMap = ConfigurationSectionMap( configurationFilename )
    
    ## parse dictionary and list
    atlasDict = configurationMap[ 'AtlasDescription' ]
    m_templateDict = { 't1':atlasDict['t1'],
                       't2':'na' }
    m_spatialDescriptionDict = { 'rho':   atlasDict['rho'],
                                 'phi':   atlasDict['phi'], 
                                 'theta': atlasDict['theta'] }
    ##
    ## note on *lower()*
    ## all the options are converted to lower case with ConfigParser xOptions
    listFiles = configurationMap[ 'ListFiles' ]
    optionsDict = configurationMap[ 'Options' ]
    ROIDict = configurationMap[ 'ROI' ] 
    m_fileDescriptions = configurationMap[ 'FileDescriptions' ]

    #for key in m_fileDescriptions.iterkeys():
    #    print ("{key} ==> {value}".format( key=key, value=m_fileDescriptions[key] ) )
    
    from XMLConfigurationGenerator import xmlGenerator
    
    returnList= xmlGenerator( m_templateDict,
                  m_spatialDescriptionDict,
                  m_fileDescriptions[ 'vectorFilename'.lower() ],
                  optionsDict[ 'roiBooleanCreator'.lower() ] ,
                  m_fileDescriptions[ 'modelFilename'.lower() ],
                  ROIDict[ 'roiList'.lower() ],
                  optionsDict[ 'imageTypeToUse'.lower() ],
                  listFiles[ 'subjectListFilename'.lower() ],
                  m_fileDescriptions[ 'xmlFilename'.lower() ],
                  optionsDict[ 'normalization' ] ,
                  listFiles['featureListFileDictionary'.lower()])

    import subprocess
    if generateProbabilityMap:
        print ("generateProbabilityMap")
        print ("generateProbabilityMap")
        print ("generateProbabilityMap")
        BRAINSCutCommand=["BRAINSCut" + " --generateProbability" +
                          " --netConfiguration " + m_fileDescriptions[ 'xmlFilename'.lower() ] 
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
    if createVectors:
        BRAINSCutCommand=["BRAINSCut" + " --createVectors" +
                          " --netConfiguration " + m_fileDescriptions[ 'xmlFilename'.lower() ] 
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
    if trainModel:
        BRAINSCutCommand=["BRAINSCut" + " --trainModel" +
                          " --netConfiguration " + m_fileDescriptions[ 'xmlFilename'.lower()] +
                          " --method RandomForest " +
                          " --numberOfTrees " + rfTreeNumber + 
                          " --randomTreeDepth " + rfTreeDepth  
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
    if applyModel:
        BRAINSCutCommand=["BRAINSCut" + " --applyModel" +
                          " --netConfiguration " + m_fileDescriptions[ 'xmlFilename'.lower()] +
                          " --method RandomForest " +
                          " --numberOfTrees " + rfTreeNumber + 
                          " --randomTreeDepth " + rfTreeDepth 
                         ]
        print("HACK:  BRAINCUT COMMAND: {0}".format(BRAINSCutCommand))
        subprocess.call(BRAINSCutCommand, shell=True)
        
    return returnList
    
#########################################################################################
def BRAINSCutGenerateProbabilityMap( configurationFilename,
                                     probabilityMapList):
    generateProbabilityMap = True
    createVectors = False
    trainModel = False
    applyModel = False
    rfTreeNumber = 0
    rfTreeDepth = 0

    print( """generate probability map
           {str}
           """.format( str=probabilityMapList) )

    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                rfTreeNumber,
                                rfTreeDepth)
    returnProbMapList = returnList[ 'probabilityMap' ]
    if returnProbMapList != probabilityMapList:
        print("""ERROR
              returnProbMapList has to match probabilityMapList
              in BRAINSCutGenerateProbabilityMap
              """)
        sys.exit()
          
    return returnList[ 'probabilityMap' ] 
                                
#########################################################################################
def BRAINSCutCreateVector( configurationFilename, 
                           probabilityMapList ):
    import os.path
    import sys
    for roi in probabilityMapList.iterkeys():
        if not os.path.exists( probabilityMapList[ roi ]  ):
            print( """ ERROR   
                   {fn}  does not exist.
                   """.format( fn=probabilityMapList[roi]) )
            sys.exit()

    generateProbabilityMap = False
    createVectors = True
    trainModel = False
    applyModel = False
    rfTreeNumber = 0
    rfTreeDepth = 0
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                rfTreeNumber,
                                rfTreeDepth)
    outputVectorFilename = returnList[ 'inputVectorFilename' ]    
    outputVectorHdrFilename = outputVectorFilename + ".hdr"
    return outputVectorFilename, outputVectorHdrFilename 

#########################################################################################
def BRAINSCutTrainModel( configurationFilename, 
                         inputVectorFilename,
                         rfTreeNumber, 
                         rfTreeDepth):
    import os.path
    import sys
    for roi in probabilityMapList.iterkeys():
        if not os.path.exists( probabilityMapList[ roi ] ):
            print( """ ERROR   
                   probabilityMapList[ roi ]  does not exist.
                   """ )
            sys.exit()

    generateProbabilityMap = False
    createVectors = False
    trainModel = True
    applyModel = False
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                rfTreeNumber,
                                rfTreeDepth)
    outputVectorFilename = returnList[ 'inputVectorFilename' ]    
    return outputVectorFilename 

#########################################################################################
def BRAINSCutApplyModel( configurationFilename, 
                         trainModelFilename,
                         rfTreeNumber, 
                         rfTreeDepth):
    import os.path
    import sys
    for roi in probabilityMapList.iterkeys():
        if not os.path.exists( probabilityMapList[ roi ] ):
            print( """ ERROR   
                   probabilityMapList[ roi ]  does not exist.
                   """ )
            sys.exit()

    generateProbabilityMap = False
    createVectors = False
    trainModel = True
    applyModel = False
    from ConfigurationParser import BRAINSCutCMDFromConfigFile
    returnList= BRAINSCutCMDFromConfigFile( configurationFilename,
                                generateProbabilityMap,
                                createVectors,
                                trainModel,
                                applyModel,
                                rfTreeNumber,
                                rfTreeDepth)
    outputVectorFilename = returnList[ 'inputVectorFilename' ]    
    return outputVectorFilename 
     
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
    varToChange= ['xmlFilename'.lower(), 
                  'vectorFilename'.lower(), 
                  'roiBooleanCreator'.lower()]

    from ConfigurationParser import ConfigurationSectionMap
    from ConfigurationParser import updating 
    Options = ConfigurationSectionMap( originalFilename )['Options']
    roiDict = Options[ 'roiBooleanCreator'.lower() ]

    FileDescriptions =  ConfigurationSectionMap( originalFilename )['FileDescriptions' ]
    xmlFilename = FileDescriptions[ 'xmlFilename'.lower() ]
    vectorFilename = FileDescriptions[ 'vectorFilename'.lower() ]

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
        new_XMLFilename = xmlFilename + "_" + roi + ".xml"
        new_VectorFilename = vectorFilename + "_" + roi + ".txt"
        
        newValues = [ new_XMLFilename, new_VectorFilename, new_ROIDict ]
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
                    exit
    return TVC

#########################################################################################
def BalanceInputVectors( inputVectorFilenames ):
    ## read header file
    from ConfigurationParser import getTVCs 
    TVC = getTVCs( inputVectorFilenames )
    maxFile = max(TVC)
    print ( maxFile )
    print ( maxFile )
    print ( maxFile )
    print ( maxFile )

    maxTVC = TVC[ maxFile ]
    #print( "{file} = {tvc}".format( file=maxFile, tvc=TVC[maxFile])) 

    outputVectorFilenames = {}
    for inFile in inputVectorFilenames:
        outputVectorFilenames[ inFile ]  = inFile + "_upsampled.txtANN"
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
    return outputVectorFilenames.values()

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

    print( inputVectorFilenames[1] + ".hdr" )
    print( inputVectorFilenames[1] + ".hdr" )
    print( inputVectorFilenames[1] + ".hdr" )
    print( inputVectorFilenames[1] + ".hdr" )
    print( inputVectorFilenames[1] + ".hdr" )
    inHdrFile = open ( inputVectorFilenames[1] + ".hdr", "r")
    import os
    outHdrFilename = os.path.abspath( outputVectorFilename ) + ".hdr"
    outHdrFile = open ( outHdrFilename, "w")
     
    firstline = inHdrFile.readline() 
    print (firstline)
    print (firstline)
    print (firstline)
    print (firstline)
    print (firstline)
    outHdrFile.write( firstline )
    outHdrFile.write( inHdrFile.readline() )
    outHdrFile.write( "TVC {value}".format( value=newTVC))
    outHdrFile.close()

    return outputVectorFilename, outHdrFilename 

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

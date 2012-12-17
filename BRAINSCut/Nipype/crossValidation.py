def writeConfigFile( originalFilename,
                     outputConfigFilename, 
                     outputAdditionaListFiles ):
    
    print("""****************************
          writeConfigFile
          """)
    import ConfigParser

    inConfigParser = ConfigParser.ConfigParser()
    try:
        print( """read
               {fn}""".format( fn = originalFilename ))
        inConfigParser.read( originalFilename );
    except:
        print( """ERROR
               fail to read file {fn}
               """.format( fn = originalFilename ))


    outConfigParser = ConfigParser.RawConfigParser()

    for section in inConfigParser.sections():
        outConfigParser.add_section( section )
        for option in inConfigParser.options( section ):
             outConfigParser.set( section, option, inConfigParser.get( section ,option) )

    for option in outputAdditionaListFiles.iterkeys():
        print( outputAdditionaListFiles[ option ] )
        print( outputAdditionaListFiles[ option ] )
        print( outputAdditionaListFiles[ option ] )
        print( outputAdditionaListFiles[ option ] )
        outConfigParser.set( 'ListFiles', 
                             option, 
                             outputAdditionaListFiles[ option ] )
    
    with open( outputConfigFilename, 'wb' ) as outConfigFile:
        outConfigParser.write( outConfigFile )
    import os
    return os.path.abspath( outputConfigFilename)


#############################################################################
def writeListFile( sessionDict, 
                   outFilenameDict,
                   tagsToWrite):
    print("""****************************
          writeListFile
          """)
    import csv
    for outTag in outFilenameDict.iterkeys():
        outFile = open( outFilenameDict[ outTag ], "wb")

        writer = csv.DictWriter( outFile, 
                                 sessionDict[ sessionDict.keys()[0] ].keys() )
        writer.writeheader()

        print( tagsToWrite )
        for session in sessionDict.iterkeys():
            sessionRow = sessionDict[ session ]
            if tagsToWrite[ session ] == outTag:
                print( "Add {s} ".format( s = sessionRow['sessionID'] ))
                writer.writerow( sessionRow)
            else:
                print( "Drop {s} ".format( s = sessionRow['sessionID'] ))
        outFile.close()

    import os.path
    returnOutFilenameDict = {}
    for fn in outFilenameDict:
        returnOutFilenameDict = os.path.abspath( outFilenameDict[ fn] )
    return returnOutFilenameDict 

#############################################################################
def getStartAndEndIndex( p_iTh,
                         p_numberOfElementsPerSubset):
    print("""****************************
          getStartAndEndIndex
          """)
    if p_iTh == 0:
        StartIndex = 0
    else:
        StartIndex = sum( p_numberOfElementsPerSubset[0:p_iTh]) 
    EndIndx = StartIndex + p_numberOfElementsPerSubset[ p_iTh ] -1 
    print( p_numberOfElementsPerSubset )
    print( "({s},{e})".format( s=StartIndex, e=EndIndx ))
    return StartIndex, EndIndx

#############################################################################
def readListFileBySessionID( inputFilename,
                             totalNumber = -1 ):
    import csv
    listDict = {}

    try: 
        print("""Read
              {fn}""".format( fn = inputFilename ))
        with open(  inputFilename, "r") as inFile:
            reader=csv.reader( inFile, delimiter=",", skipinitialspace=True)
            header = reader.next()
            print( header )
            for row in reader:
                rowWithHeader = zip( header, row)
                rowDict = {}
                for ( name, value ) in rowWithHeader:
                    rowDict[ name ] = value.strip()
                listDict[ rowDict[ 'sessionID' ] ]=  rowDict 
    except:
        print( """ERROR
               fail to read file {fn}
               """.format( fn = inputFilename))
    import sys
    if totalNumber > 0 and len( listDict ) != totalNumber:
        print("""ERROR
              Total number of feature images are not equal to the main list.
              n( inputFilename ) = {n} != {t}
              """.format( n=len( listDict ) ,t=totalNumber ))
        sys.exit()

    return listDict
#############################################################################
def getTags( sessionList,
             nTest, 
             numberOfElementInSubset,
             randomize=False):
    print("""****************************
          getTags 
          """)
    if randomize:
        sessionOrder=getRandomizedSessionOrder(sessionList)
    else:
        orderIndex=0
        sessionOrder = {}
        for session in sessionList:
            sessionOrder[ session ] = orderIndex
            orderIndex = orderIndex +1
    applyStart, applyEnd = getStartAndEndIndex( nTest, numberOfElementInSubset)
    tags = {}
    for session in sessionList:
        if applyStart <= sessionOrder[ session ] and sessionOrder[ session ] <= applyEnd:
            tags[session]='Apply'
        else:
            tags[session]='Train'
    print("""Generate tags:::
             {t}""".format( t=tags))
    return tags 
#############################################################################
def getRandomizedSessionOrder( sessionList):
    print("""****************************
          getRandomizedSessionOrder 
          """)
    ## randomize the order 
    import random
    print ("""input list:::
           {s}""".format( s=sessionList ))
    random.shuffle( sessionList, random.random )
    print( """randomized list:::
           {s}""".format( s=sessionList ))
    orderIndex = 0
    sessionOrder = {}
    for s in sessionList:
        print( """ assign sessionOrder[{s}] = {orderIndex}""".format( s=s, orderIndex=orderIndex))
        sessionOrder[ s ] = orderIndex 
        orderIndex = orderIndex + 1
    return sessionOrder

#############################################################################
def generateNewFilenames( nTest, 
                          featureList,
                          outputPrefix):
    print("""****************************
          generateNewFilenames 
          """)
    returnConfigFilename = outputPrefix + "_Test" + str(nTest) + "_configuration.config"
    returnMainListFilename = { 'Train':outputPrefix + "_Test" + str(nTest) + "_mainTrainList.csv",
                               'Apply':outputPrefix + "_Test" + str(nTest) + "_mainApplyList.csv"}
    returnFeatureListFilenameDict = {}
    for ft in featureList:
        currentPefix=outputPrefix + "_" + "Test" +str(nTest) + "_" + str(ft)
        returnFeatureListFilenameDict[ft] = {'Train': currentPefix + "_featureTrainList.csv",
                                             'Apply': currentPefix + "_featureApplyList.csv" }
    print("""
          returnMainListFilename: {fn1}
          returnFeatureListFilenameDict: {fn2}
          """.format( fn1=returnMainListFilename, fn2=returnFeatureListFilenameDict))
    return returnConfigFilename, returnMainListFilename, returnFeatureListFilenameDict
    
#############################################################################
def createConfigurationFileForCrossValidationUnitTest( p_configurationFilename,
                                                       outputFilePrefix):
    print("""****************************
          createConfigurationFileForCrossValidationUnitTest
          """)
    import os.path
    outputFilePrefix = os.path.abspath( outputFilePrefix )

    import ConfigurationParser
    m_configurationMap =  ConfigurationParser.ConfigurationSectionMap( p_configurationFilename )

    # get list filenames
    import crossValidation as this
    listFilenames = m_configurationMap[ 'ListFiles' ]
    mainListFilename = listFilenames['subjectListFilename'.lower() ] 
    featureListFilenamesDict = listFilenames['featureListFileDictionary'.lower() ]
    numberOfElementsInSubset = listFilenames[  'numberOfElementInSubset'.lower() ]
    numberOfTotalSession = sum(numberOfElementsInSubset)

    # read files into sessionID -> data
    mainSessionDict = this.readListFileBySessionID( mainListFilename, 
                                                    numberOfTotalSession)
    featureSessionDict = {}
    for ft in featureListFilenamesDict.iterkeys():
        featureSessionDict[ft] = this.readListFileBySessionID( featureListFilenamesDict[ft],
                                                               numberOfTotalSession)


    returnConfigFile = {}
    #{ iterate throug subsets
    for nTest in range ( 0, len( numberOfElementsInSubset ) ): 
        trainApplyTagList = this.getTags( mainSessionDict.keys(),
                                          nTest, 
                                          numberOfElementsInSubset);
        newConfigFilename, newMainFilename, newFeatureFilenameDict = this.generateNewFilenames( nTest, 
                                   featureListFilenamesDict.keys(),
                                   outputFilePrefix)
        this.writeListFile( mainSessionDict, 
                            newMainFilename,
                            trainApplyTagList)
        trainFeatureStr = {}
        applyFeatureStr = {}
        for ft in featureSessionDict.iterkeys():
            this.writeListFile( featureSessionDict[ft],
                                newFeatureFilenameDict[ft],
                                trainApplyTagList)
            trainFeatureStr[ft]=newFeatureFilenameDict[ft]['Train']
            applyFeatureStr[ft]=newFeatureFilenameDict[ft]['Apply']
            
        print( newMainFilename['Train'] )
        print( newMainFilename['Apply'] )
        print( trainFeatureStr )
        print( applyFeatureStr )
        this.writeConfigFile( p_configurationFilename,
                              newConfigFilename, 
                              {'subjectListFilename':newMainFilename['Train'],
                               'applySubjectListFilename':newMainFilename['Apply'],
                               'featureListFileDictionary':str( trainFeatureStr ),
                               'applyFeatureListFileDictionary':str( applyFeatureStr )})
        returnConfigFile[ "Test"+ str(nTest) ] = os.path.abspath( newConfigFilename )
    return returnConfigFile
#############################################################################

def extractConfigFile ( configurationFiledict ):
    print("""****************************
          extractConfigFile
          """)
    return configurationFiledict.values()

def crossValidationWorkUp( crossValidationConfigurationFilename,
                           baseDir):
    print("""****************************
          crossValidationWorkUp
          """)
    from nipype import config
    config.enable_debug_mode()

    import crossValidation as this
    import ConfigurationParser
    myConfigurationMap = ConfigurationParser.ConfigurationSectionMap( 
                              crossValidationConfigurationFilename )
    
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function

    print( """ before
           createeachvalidationunitnd
           """)
    createEachValidationUnitND = pe.Node( name = "createEachValidationUnitND",
                                          interface = Function(  
                                             input_names = ['p_configurationFilename',
                                                            'outputFilePrefix'],
                                             output_names = ['outputConfigFilenameDict'],
                                             function = this.createConfigurationFileForCrossValidationUnitTest )
                                        )

    workflow = pe.Workflow( name = 'crossValidationWF' )
    workflow.base_dir = baseDir
    workflow.add_nodes( [createEachValidationUnitND] )

    createEachValidationUnitND.inputs.p_configurationFilename = crossValidationConfigurationFilename
    createEachValidationUnitND.inputs.outputFilePrefix = 'createEachValidationUnitND'
    
    extractConfigurationFileListND = pe.Node( name = "extractConfigurationFileListND",
                                              interface = Function(
                                                  input_names = ['configurationFiledict'],
                                                  output_names = ['configurationFileList'],
                                                  function = this.extractConfigFile )
                                            )
    workflow.connect( createEachValidationUnitND, 'outputConfigFilenameDict',
                      extractConfigurationFileListND, 'configurationFiledict')

    import crossValidationUnit

    createEachValidationUnitND = pe.MapNode( name = "unitFlow" ,
                                          interface = Function(
                                              input_names= [ 'configurationFilename',
                                                             'doApply',
                                                             'baseDir' ],
                                              output_names = [],
                                              function = crossValidationUnit.unitWorkUp ),
                                          iterfield = ['configurationFilename']
                                        )
    createEachValidationUnitND.inputs.doApply=True
    createEachValidationUnitND.inputs.baseDir='unitFlowBaseDir'

    workflow.connect( extractConfigurationFileListND, 'configurationFileList',
                      createEachValidationUnitND, 'configurationFilename' )

    workflow.run()

def main(argv=None):
    import os
    import sys
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function
    import ConfigurationParser
    
    from nipype import config
    config.enable_debug_mode()
    
    workflow = pe.Workflow( name = 'crossValidation' )
    workflow.base_dir = '.'
    
    #-------------------------------- argument parser
    import argparse
    argParser = argparse.ArgumentParser( description ="""****************************
        10-cross validation command line argument parser
        """)
    # workup arguments
    argWfGrp = argParser.add_argument_group( 'argWfGrp', """****************************
        auto workflow arguments for cross validation
        """)
    argWfGrp.add_argument( '--crossValidationConfigurationFilename',    
        help="""configurationFilename
        Configuration file name with FULL PATH""", 
        dest='crossValidationConfigurationFilename', required=True )
    argWfGrp.add_argument( '--baseDir',    help="""baseDir
        """, 
        dest='baseDir', required=False, default="." )

    # test arguments
    argTestGrp = argParser.add_argument_group( 'argTestGrp', """****************************
        arguments for testing
        """)
    argTestGrp.add_argument( '--unitTest', action='store_true',
        dest='unitTest', help="""****************************
        List of test function name
        """)
    args = argParser.parse_args()

    if not args.unitTest: 
        crossValidationWorkUp ( args.crossValidationConfigurationFilename,
            args.baseDir)
    
    if args.unitTest:
        testElementPerSubject = [ 3, 4, 5 ]
        getStartAndEndIndex ( 0, testElementPerSubject )
        getStartAndEndIndex ( 1, testElementPerSubject )
        getStartAndEndIndex ( 2, testElementPerSubject )
        
        featureDict = {'GadSG':'testGadFeatureList.csv',
                       't2':'t2FeatureList.csv'}


        sessionList = ["s1","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11","s12"]
        getRandomizedSessionOrder( sessionList )
        myTag = getTags( sessionList, 
                         2,
                         testElementPerSubject)
        featureFilenameDict = {'f1':'f1.csv', 'f2':'f2.csv'}
        configFilename,mainFilenameDict, featureFilenameDict = generateNewFilenames( 3,
                                                   featureFilenameDict.keys(),
                                                   "outputPrefix")
        import ConfigurationParser
        m_configurationMap =  ConfigurationParser.ConfigurationSectionMap( args.crossValidationConfigurationFilename )

        listFiles = m_configurationMap[ 'ListFiles' ]
        mainListFilename = listFiles['subjectListFilename'.lower() ]  
        sessionDict = readListFileBySessionID( mainListFilename )
        myTag = getTags( sessionDict.keys(),
                         2,
                         listFiles[  'numberOfElementInSubset'.lower() ] )
        writeListFile( sessionDict ,
                             mainFilenameDict,
                             myTag )

        #createConfigurationFileForCrossValidationUnitTest( args.crossValidationConfigurationFilename,
        #                                                   "./TEST")
    
import sys

if __name__ == "__main__":
    sys.exit(main())

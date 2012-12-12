import sys
#########################################################################################
#{#######################################################################################
def combineCSVs( dataFile, featureFileiList):
    import csv
    returnDictionary = {}
    with open( dataFile, "r") as dataListFile:
        dataListReader=csv.reader( dataListFile, delimiter=",", skipinitialspace=True)
        dataListHeader = dataListReader.next()
        for session in dataListReader:
            sessionWithHeader = zip( dataListHeader, session )

            sessionDict = {}
            for ( name, value) in sessionWithHeader:
                sessionDict[ name ] = value.strip()
            returnDictionary[ sessionDict[ 'sessionID' ] ] = sessionDict


    for featureKey in featureFileiList.iterkeys():
        with open( featureFileiList[ featureKey ], "r") as featureListFile:
            featureListReader = csv.reader( featureListFile, delimiter=",", skipinitialspace=True)
            featureListHeader = featureListReader.next()
            for session in featureListReader:
                sessionWithHeader = zip( featureListHeader, session )
                sessionFeatureDict = {}
                for ( name, value) in sessionWithHeader:
                    sessionFeatureDict[ name ] = value.strip()
                currSessionDict = returnDictionary[ sessionFeatureDict[ 'sessionID' ] ] 
                currSessionDict[ 'featureImageList' ] = sessionFeatureDict[ 'featureImageList' ]
                returnDictionary[ sessionFeatureDict[ 'sessionID' ] ] = currSessionDict
                #print( returnDictionary[ sessionFeatureDict[ 'sessionID' ] ] )
                #print("^^^^^^^^^^^^^^^^^^^")

    return returnDictionary

#}---------------------------------------------------------------------------------------
#########################################################################################
#{#######################################################################################
def addSession( subjectID, 
                dataType, # train/apply
                imageDict, 
                roiDict, 
                deformationDict,
                featureDict,
                outStream,
                outputDir=""):

    outStream.write( "  <DataSet Name=\"{id}\" Type=\"{str}\"".format( id=subjectID, str=dataType) )
    if dataType == "Apply":
      outStream.write( "      OutputDir=\"{str}\" >\n".format( str=outputDir ))
    else:
      outStream.write( " >\n")

    for imgType in imageDict.iterkeys():
        outStream.write( "    <Image Type=\"{str}\"".format( str=imgType ))
        outStream.write( " Filename=\"{str}\" />\n".format( str=imageDict[ imgType] ) )

    for featureType in featureDict.iterkeys():
        outStream.write( "    <Image Type=\"{str}\"".format( str=featureType ))
        outStream.write( " Filename=\"{str}\" />\n".format( str=featureDict[ featureType] ) )

    outStream.write( "    <Mask  Type=\"RegistrationROI\" Filename=\"{fn}\" />\n".format(fn="na"))

    for roiID in roiDict.iterkeys():
        outStream.write( "    <Mask Type=\"{str}\" ".format( str=roiID ))
        outStream.write( " Filename=\"{str}\" />\n".format( str=roiDict[ roiID] ))

    outStream.write( "    <Registration ")
    outStream.write( '   SubjToAtlasRegistrationFilename="{str}"\n'.format( str=deformationDict['subjectToAtlas']))
    outStream.write( '   AtlasToSubjRegistrationFilename="{str}"\n'.format( str=deformationDict['atlasToSubject']))
    outStream.write( "       ID=\"SyN\" /> \n")

    outStream.write( "  </DataSet>\n")
#}---------------------------------------------------------------------------------------



#########################################################################################
#{#######################################################################################
def addProbabilityMapElement( probabilityMapFilename, 
                              roiID, 
                              outStream,
                              roiCreateVector="true"):
    outStream.write( "  <ProbabilityMap StructureID    = \"{str}\"\n".format( str = roiID) )
    outStream.write( "      Gaussian       = \"0.5\"\n")
    outStream.write( "      GenerateVector = \"{str}\"\n".format( str=roiCreateVector ) )
    outStream.write( "      Filename       = \"{str}\"\n".format( str =  probabilityMapFilename ))
    outStream.write( "   />\n")
#---------------------------------------------------------------------------------------}

#########################################################################################
#{#######################################################################################
def xmlGenerator( p_templateDict, 
                  p_templateSpatialLocation,
                  p_inputVectorFilename,
                  p_inputVectorCreateDict,
                  p_modelFilename, 
                  p_roiList, 
                  p_imageTypeToUse,
                  p_dataListFilename ,
                  p_outputXMLFilename,
                  p_normalization,
                  p_featureImageFilenames = {} ):
    returnList = {}
    outStream = open( p_outputXMLFilename, 'w')
    m_registrationID = "SyN"

    #####################################################################################
    # header
    #
    outStream.write( "<AutoSegProcessDescription>\n" )

    #####################################################################################
    # template
    # :: p_templateDict { t1:t1Filename, 
    #                   t2:t2Filename }
    outStream.write( "  <DataSet Name=\"template\" Type=\"Atlas\" >\n" )
    for imgType in p_templateDict.iterkeys():
        outStream.write( "      <Image Type=\"{tp}\" Filename=\"{fn}\" />\n".format(tp=imgType, 
                                                                                    fn=p_templateDict[imgType]))
    for featureImgType in p_featureImageFilenames.iterkeys():
        outStream.write( "      <Image Type=\"{tp}\" Filename=\"na\" />\n".format(tp=featureImgType ))
    for spType in p_templateSpatialLocation.iterkeys():
        outStream.write( "      <SpatialLocation Type=\"{tp}\" Filename=\"{fn}\" />\n".format(tp=spType, 
                                                                                              fn=p_templateSpatialLocation[spType]))
    outStream.write( " </DataSet>\n")

    #####################################################################################
    # Registration parameters
    outStream.write( "  <RegistrationConfiguration \n")
    outStream.write( "          ImageTypeToUse  = \"{tp}\"\n".format( tp = p_imageTypeToUse ) )
    outStream.write( "          ID              = \"{rID}\"\n".format( rID = m_registrationID ) )
    outStream.write( "          BRAINSROIAutoDilateSize= \"1\"\n")
    outStream.write( "   />\n")

    #####################################################################################
    # training vector configuration  (feature vector)
    #
    outStream.write( "   <NeuralNetParams MaskSmoothingValue     = \"0.0\"\n")
    outStream.write( "          GradientProfileSize    = \"1\"\n")
    outStream.write( "          TrainingVectorFilename = \"{vectorFN}\"\n".format( vectorFN = p_inputVectorFilename ))
    outStream.write( "          TrainingModelFilename  = \"{modelFN}\"\n".format( modelFN = p_modelFilename ))
    outStream.write( "          TestVectorFilename     = \"na\"\n")
    outStream.write( "          Normalization          = \"{str}\"\n".format( str = p_normalization) )
    outStream.write( "   />\n")
    returnList ['inputVectorFilename'] = p_inputVectorFilename + "ANN"
    #####################################################################################
    # random forest parameters
    #
    outStream.write( "   <RandomForestParameters \n")
    outStream.write( "      MaxDepth= \"1\"\n")     #dummy
    outStream.write( "      MaxTreeCount= \"1\"\n") # dummy
    outStream.write( "      MinSampleCount= \"5\"\n")
    outStream.write( "      UseSurrogates= \"false\"\n")
    outStream.write( "      CalcVarImportance= \"false\"\n")
    outStream.write( "      />\n")

    #####################################################################################
    # ANN Parameters 
    # TODO: Simplify!!!
    #
    outStream.write( "   <ANNParameters Iterations             = \"5\"\n")
    outStream.write( "                     MaximumVectorsPerEpoch = \"700000\"\n")
    outStream.write( "                     EpochIterations        = \"100\"\n")
    outStream.write( "                     ErrorInterval          = \"1\"\n")
    outStream.write( "                     DesiredError           = \"0.000001\"\n")
    outStream.write( "                     NumberOfHiddenNodes    = \"100\"\n")
    outStream.write( "                     ActivationSlope        = \"1.0\"\n")
    outStream.write( "                     ActivationMinMax       = \"1.0\"\n")
    outStream.write( "    />\n")

    #####################################################################################
    # apply conditions
    #
    outStream.write( "<ApplyModel         CutOutThresh           = \"0.05\"\n")
    outStream.write( "                    MaskThresh             = \"0.5\"\n")
    outStream.write( "                    GaussianSmoothingSigma = \"0.0\"\n")
    outStream.write( "   />\n")

    #####################################################################################
    # add ROIs (ProbabilityMaps)
    #
    if not p_inputVectorCreateDict:
        p_inputVectorCreateDict = {}
        for roiID in p_roiList.iterkeys():
            p_inputVectorCreateDict[ roiID ] = 'true'
    
    for roiID in p_roiList.iterkeys():
        addProbabilityMapElement( p_roiList[roiID], 
                                  roiID, 
                                  outStream,
                                  p_inputVectorCreateDict[ roiID ] ) 
    returnList[ 'probabilityMap'] = p_roiList 

    #####################################################################################
    # merge feature list if necessary 
    #
    dataDictionary={}
    dataDictionary = combineCSVs( p_dataListFilename, p_featureImageFilenames )

    #####################################################################################
    # add session images
    #
    import ast
    for sessionKey  in dataDictionary.iterkeys():
        session = dataDictionary[ sessionKey ]
        if session.has_key( 'featureImageList' ) :
            featureImageDict =  ast.literal_eval( session[ 'featureImageList' ] )
        else:
            featureImageDict = {}

        addSession( session[ 'sessionID' ], 
                    'Train',
                    ast.literal_eval( session[ 'imageList' ] ),
                    ast.literal_eval( session[ 'roiList' ] ),
                    ast.literal_eval( session[ 'deformationList' ] ),
                    featureImageDict,
                    outStream  )
        
    #####################################################################################
    # closer 
    #
    outStream.write( "</AutoSegProcessDescription>\n" )

    return returnList
#}---------------------------------------------------------------------------------------

#########################################################################################
#{#######################################################################################
# TEST

if __name__ == "__main__":
      sys.exit(main())
#combineCSVs("trainingBAW20120801List.csv", "gadSGFeatureList.csv")
#---------------------------------------------------------------------------------------}

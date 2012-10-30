
# --------------------------------------------------------------------------------------- #
def GetProbabilityFilename  ( inputROI,
                              inputDir
                              ):

  outputFilename = inputDir + "/" + "/probabilityMaps/" + inputROI + "_ProbabilityMap.nii.gz"
  return outputFilename

# --------------------------------------------------------------------------------------- #
def ThresholdProbabilityMap ( inputVolume, 
                              lowerThreshold,
                              upperThreshold,
                              outputFilename):
  import os
  import sys
  import SimpleITK as sitk

  inImg = sitk.Cast( sitk.ReadImage( inputVolume ),
                     sitk.sitkFloat32 )
  outImg = sitk.BinaryThreshold( inImg, 
                                 lowerThreshold,
                                 upperThreshold )

  sitk.WriteImage( outImg, outputFilename )
  returnFile = os.path.realpath( outputFilename )

  return returnFile

# --------------------------------------------------------------------------------------- #
def SmoothProbabilityMap ( inputVolume, 
                           sigma,
                           outputVolume):
  import os
  import sys
  import SimpleITK as sitk

  inImg = sitk.Cast( sitk.ReadImage( inputVolume ),
                     sitk.sitkFloat32 )

  normalizeAcrossScale = False

  smoother = sitk.SmoothingRecursiveGaussianImageFilter()
  outImg = smoother.Execute( inImg, 
                             sigma,
                             normalizeAcrossScale )

  sitk.WriteImage( outImg, outputVolume )
  returnFile = os.path.realpath( outputVolume )

  return returnFile


# --------------------------------------------------------------------------------------- #
def LabelStatistics ( inputLabel,
                      inputVolume,
                      outputCSVFilename):
  labelValue=1

  import SimpleITK as sitk

  statCalculator = sitk.LabelStatisticsImageFilter()
  inImg = sitk.Cast( sitk.ReadImage( inputVolume ),
                     sitk.sitkFloat32 )
  inMsk = sitk.ReadImage( inputLabel) 


  statCalculator.Execute( inImg, inMsk )

  ## volume
  imageSpacing = inMsk.GetSpacing()
  Volume = imageSpacing[0] * imageSpacing[1] * imageSpacing[2] * statCalculator.GetCount( labelValue )

  Mean = statCalculator.GetMean( labelValue )
  Median = statCalculator.GetMedian( labelValue )
  Minimum = statCalculator.GetMinimum( labelValue )
  Maximum = statCalculator.GetMaximum( labelValue )
  Sigma = statCalculator.GetSigma( labelValue )
  Variance = statCalculator.GetVariance( labelValue )

  outputDictionary = dict()

  outputDictionary[ 'Mean' ] = Mean
  outputDictionary[ 'Median' ] = Median
  outputDictionary[ 'Minimum' ] = Minimum
  outputDictionary[ 'Maximum' ] = Maximum
  outputDictionary[ 'Sigma' ] = Sigma
  outputDictionary[ 'Variance' ] = Variance
  print "################################################## Mean:: "     + str(Mean) 
  print "################################################## Median:: "   + str(Median)
  print "################################################## Minimum:: "  + str(Minimum)
  print "################################################## Maximum:: "  + str(Maximum)
  print "################################################## Sigma:: "    + str(Sigma)
  print "################################################## Variance:: " + str(Variance)

  ## TODO 25/75 quantiles
  LowerHalfMsk = sitk.BinaryThreshold( inImg, 0, Median )
  Quantile25Calculator = sitk.LabelStatisticsImageFilter()
  Quantile25Calculator.Execute( inImg, inMsk*LowerHalfMsk  )
  Quantile25 = Quantile25Calculator.GetMedian( labelValue )
  outputDictionary[ 'Quantile25' ] = Quantile25
  print "################################################## Quantile25:: " + str(Quantile25)

  UpperHalfMsk = sitk.BinaryThreshold( inImg, Median, Maximum )
  Quantile75Calculator = sitk.LabelStatisticsImageFilter()
  Quantile75Calculator.Execute( inImg, inMsk*UpperHalfMsk )
  Quantile75 = Quantile75Calculator.GetMedian( labelValue )
  outputDictionary[ 'Quantile75' ] = Quantile75
  print "################################################## Quantile75:: " + str(Quantile75)
  
  ## TODO MAD 
  AbsoluteFilter = sitk.AbsImageFilter()
  AbsImg = AbsoluteFilter.Execute( inImg-Median )

  MEDCalculator = sitk.LabelStatisticsImageFilter()
  MEDCalculator.Execute( AbsImg, inMsk )
  MED = MEDCalculator.GetMedian( labelValue )
  outputDictionary[ 'MED' ] = MED
  print "################################################## MED:: " + str(MED)

  import csv
  csvFile = open( outputCSVFilename, 'w')
  dWriter = csv.DictWriter( csvFile, outputDictionary.keys() )
  dWriter.writeheader()
  dWriter.writerow( outputDictionary )

  import os
  import sys
  returnFile = os.path.realpath( outputCSVFilename )

  returnDict = { 'outputStatDictionary': outputDictionary,
                 'outputCSVFilename': returnFile }
  return  returnDict

# --------------------------------------------------------------------------------------- #
def NormalizeInputVolume ( inputMethod, 
                           inputStats,
                           outputVolume ):
  import SimpleITK as sitk
  
  inImg = sitk.Cast( sitk.ReadImage( inputVolume ),
                     sitk.sitkFloat32 )

  IQR = inputStats['Quantile75']-inputStats['Quantile25']

  if inputMethod == 'zScore':
    print "zScore Normalization"
    outImg = (inImg - inputStats['Mean']) / inputStats['Sigma']
  elif inputMethod == 'MAD':
    print "MAD Normalization"
    outImg = (inImg - inputStats['Median']) / inputStats['MAD']
  elif inputMethod == 'Sigmoid':
    print "Sigmoid Normalization"
    outImg = 1 / ( 1 + exp( -2 * ( inImg - inputStats['Median'] )/IQR ) )
  elif inputMethod == 'QEstimator':
    print "QEstimator Normalization"
    outImg = (inImg - inputStats['Median']) / IQR
  elif inputMethod == 'Linear':
    print "Linear Normalization"
    outImg = ( inImg - inputStats['Min'] ) / ( inputStats['Max']  - inputStats['Min'] )
  elif inputMethod == 'DoubleSigmoid':
    print "Double Sigmoid Normalization"
    temp1 = sitk.Threshold( inImg, inputStats['Min'], inputStats['Median'] )
    outImg1 = 1 / ( 1 + exp( -2 * ( temp1 - inputStats['Median'] )/ 
                        ( inputStats['Median']- inputStats['Quantile25']) ) )
    temp2 = sitk.Threshold( inImg, ( inputStats['Median']+0.00001) , inputStats['Max'] )
    outImg2 = 1 / ( 1 + exp( -2 * ( temp2 - ( inputStats['Median'] +0.00001) )/ 
                        ( inputStats['Quantile75']- (inputStats['Median']+0.00001  )) ) )
    outImg = outImg1 + outImg2 

  sitk.WriteImage( outImg, outVolume )
  returnFile = os.path.realpath( outVolume )

  return returnFile


    

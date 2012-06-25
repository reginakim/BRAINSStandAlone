#include "FeatureInputVector.h"
#include "BRAINSCutExceptionStringHandler.h"
#include "itkLabelStatisticsImageFilter.h"

const scalarType FeatureInputVector::MIN = -1.0F;
const scalarType FeatureInputVector::MAX = 1.0F;

FeatureInputVector
::FeatureInputVector() :
  m_gradientSize(-1),
  m_normalization(false)
{
  m_spatialLocations.clear();
  m_candidateROIs.clear();
  m_gradientOfROI.clear();
  m_featureInputOfROI.clear();
  imageInterpolator = ImageLinearInterpolatorType::New();
}

void
FeatureInputVector
::SetGradientSize(unsigned int length)
{
  m_gradientSize = length;
}

void
FeatureInputVector
::SetImagesOfInterestInOrder( WorkingImageVectorType& images)
{
  imagesOfInterestInOrder = images;
}

void
FeatureInputVector
::SetImagesOfSpatialLocation( std::map<std::string, WorkingImagePointer>& SpatialLocationImages)
{
  if( SpatialLocationImages.size() != 3 ||
      SpatialLocationImages.find("rho") == SpatialLocationImages.end() ||
      SpatialLocationImages.find("phi") == SpatialLocationImages.end()  ||
      SpatialLocationImages.find("theta") == SpatialLocationImages.end()  )
    {
    itkGenericExceptionMacro(<< "::number of images for spatial location should be 3 not " 
                             << SpatialLocationImages.size());
    }
  m_spatialLocations = SpatialLocationImages;
}

void
FeatureInputVector
::SetCandidateROIs( std::map<std::string, WorkingImagePointer>& candidateROIMap)
{
  m_candidateROIs = candidateROIMap;
}

void
FeatureInputVector
::SetROIInOrder( DataSet::StringVectorType roiInOrder)
{
  roiIDsInOrder = roiInOrder;
}

void
FeatureInputVector
::SetGradientImage( std::string ROIName )
{
  GradientFilterType::Pointer gradientFilter = GradientFilterType::New();

  gradientFilter->SetInput( m_candidateROIs.find( ROIName)->second );
  try
    {
    gradientFilter->Update();
    }
  catch( ... )
    {
    std::string errorMsg = " Fail to generate itk gradient image.";
    throw BRAINSCutExceptionStringHandler( errorMsg );
    }
  m_gradientOfROI.insert( std::pair<std::string, GradientImageType>( ROIName, gradientFilter->GetOutput() ) );
}

void
FeatureInputVector
::SetInputVectorSize()
{
  if( m_candidateROIs.empty() || imagesOfInterestInOrder.empty() || m_spatialLocations.empty() )
    {
    std::string errorMsg = " Cannot compute input vector size properly.";
    errorMsg += "Either ROI(probability maps) or feature images has to be set to compute input vector size.";
    throw BRAINSCutExceptionStringHandler( errorMsg );
    }
  m_inputVectorSize = m_candidateROIs.size() + imagesOfInterestInOrder.size() * 3 + m_spatialLocations.size();
}

unsigned int
FeatureInputVector
::GetInputVectorSize()
{
  return m_inputVectorSize;
}

void
FeatureInputVector
::SetNormalization( const bool doNormalize)
{
  m_normalization = doNormalize;
};

InputVectorMapType
FeatureInputVector
::GetFeatureInputOfROI( std::string ROIName )
{
  if( m_featureInputOfROI.find( ROIName ) == m_featureInputOfROI.end() )
    {
    ComputeFeatureInputOfROI( ROIName);
    }
  return InputVectorMapType(m_featureInputOfROI.find( ROIName )->second);
}

void
FeatureInputVector
::ComputeFeatureInputOfROI( std::string ROIName)
{
  SetGradientImage( ROIName );

  typedef itk::ImageRegionIterator<WorkingImageType> ImageRegionIteratorType;

  InputVectorMapType currentFeatureVector;

  WorkingImagePointer currentROIImage = m_candidateROIs.find( ROIName)->second;

  /* iterate through each voxel in the probability map */
  ImageRegionIteratorType eachVoxelInROI( currentROIImage, currentROIImage->GetLargestPossibleRegion() );

  eachVoxelInROI.GoToBegin();

  while( !eachVoxelInROI.IsAtEnd() )
    {
    if( (eachVoxelInROI.Value() > (0.0F + FLOAT_TOLERANCE) ) && (eachVoxelInROI.Value() < (1.0F - FLOAT_TOLERANCE) ) )
      {
      InputVectorType           oneRowInputFeature( m_inputVectorSize );
      InputVectorType::iterator featureElementIterator = oneRowInputFeature.begin();

      AddCandidateROIFeature( eachVoxelInROI.GetIndex(), featureElementIterator);
      AddSpatialLocation( eachVoxelInROI.GetIndex(), featureElementIterator);
      AddFeaturesImagesOfInterest(ROIName, eachVoxelInROI.GetIndex(), featureElementIterator);

      int oneRowKey = FeatureInputVector::HashKeyFromIndex( eachVoxelInROI.GetIndex() );

      currentFeatureVector.insert( std::pair<int, InputVectorType>( oneRowKey, oneRowInputFeature) );
      }
    ++eachVoxelInROI;

    }

  /* m_normalization */
  if( m_normalization )
    {
    SetNormalizationParameters( ROIName );
    NormalizationOfVector( currentFeatureVector, ROIName );
    }

  /* insert computed vector */
  m_featureInputOfROI.insert(std::pair<std::string, InputVectorMapType>( ROIName, currentFeatureVector) );
}

/* set m_normalization parameters */
void
FeatureInputVector
::SetNormalizationParameters( std::string ROIName )
{
  /* threshold roi */
  typedef itk::BinaryThresholdImageFilter<WorkingImageType,
                                          BinaryImageType> ThresholdType;

  ThresholdType::Pointer thresholder = ThresholdType::New();

  thresholder->SetInput( m_candidateROIs.find( ROIName)->second );
  thresholder->SetLowerThreshold( 0.0F + FLOAT_TOLERANCE );
  thresholder->SetInsideValue(1);
  thresholder->Update();

  /* get min and max for each image type*/

  minmaxPairVectorType currentMinMaxVector;
  for( WorkingImageVectorType::const_iterator eachTypeOfImage = imagesOfInterestInOrder.begin();
       eachTypeOfImage != imagesOfInterestInOrder.end();
       ++eachTypeOfImage )
    {
    BinaryImageType::Pointer binaryImage = thresholder->GetOutput();
    minmaxPairType           eachMinMax = SetMinMaxOfSubject( binaryImage, *eachTypeOfImage );
    currentMinMaxVector.push_back( eachMinMax );
    }

  m_minmax[ROIName] = currentMinMaxVector;

}

/** inline functions */
inline void
FeatureInputVector
::AddValueToElement( scalarType value, std::vector<scalarType>::iterator & elementIterator)
{
  try
    {
    *elementIterator = value;
    elementIterator++;
    }
  catch( ... )
    {
    std::string errorMsg = "Fail To Add Value To Element.";
    throw BRAINSCutExceptionStringHandler( errorMsg );
    }
  // std::cout<<value<<" ";
}

inline void
FeatureInputVector
::AddCandidateROIFeature( WorkingImageType::IndexType currentPixelIndex,
                          std::vector<scalarType>::iterator & elementIterator)
{
  for( DataSet::StringVectorType::const_iterator roiStringIt = roiIDsInOrder.begin();
       roiStringIt != roiIDsInOrder.end();
       ++roiStringIt )  // iterate each ROI candidates in order specified in "roi IDs in order"
    {
    WorkingPixelType currentProbability = m_candidateROIs.find( *roiStringIt )->second->GetPixel( currentPixelIndex );
    if( currentProbability > 0.0F +  FLOAT_TOLERANCE )
      {
      AddValueToElement( MAX, elementIterator );
      }
    else
      {
      AddValueToElement( MIN, elementIterator );
      }
    }
}

inline void
FeatureInputVector
::AddSpatialLocation( WorkingImageType::IndexType currentPixelIndex,
                      std::vector<scalarType>::iterator & elementIterator)
{
  // std::cout<<" (spatial) ";
  AddValueToElement( m_spatialLocations.find("rho")->second->GetPixel( currentPixelIndex ), elementIterator );
  AddValueToElement( m_spatialLocations.find("phi")->second->GetPixel( currentPixelIndex ), elementIterator );
  AddValueToElement( m_spatialLocations.find("theta")->second->GetPixel( currentPixelIndex ), elementIterator );
}

inline void
FeatureInputVector
::AddFeaturesImagesOfInterest(  std::string ROIName,
                                WorkingImageType::IndexType currentPixelIndex,
                                std::vector<scalarType>::iterator & elementIterator )
{
  for( WorkingImageVectorType::const_iterator wit = imagesOfInterestInOrder.begin();
       wit != imagesOfInterestInOrder.end();
       ++wit )
    {
    // std::cout<<"(IMG) ";
    AddFeaturesAlongGradient( ROIName, (*wit), currentPixelIndex, elementIterator);
    }
}

inline void
FeatureInputVector
::AddFeaturesAlongGradient( std::string ROIName,
                            WorkingImagePointer featureImage,
                            WorkingImageType::IndexType currentPixelIndex,
                            std::vector<scalarType>::iterator & elementIterator )
{
  const std::map<std::string, scalarType> delta = CalculateUnitDeltaAlongTheGradient( ROIName,
                                                                                      currentPixelIndex );
  itk::Point<WorkingPixelType, DIMENSION> CenterPhysicalPoint;
  featureImage->TransformIndexToPhysicalPoint( currentPixelIndex, CenterPhysicalPoint );

  imageInterpolator->SetInputImage( featureImage );
  for( float i = -m_gradientSize; i <= m_gradientSize; i = i + 1.0F )
    {
    // std::cout<<"(gradient at "<< i<<" )";
    itk::Point<WorkingPixelType, 3> gradientLocation = CenterPhysicalPoint;

    gradientLocation[0] = CenterPhysicalPoint[0] + i * (delta.find("deltaX")->second);
    gradientLocation[1] = CenterPhysicalPoint[1] + i * (delta.find("deltaY")->second);
    gradientLocation[2] = CenterPhysicalPoint[2] + i * (delta.find("deltaZ")->second);

    itk::ContinuousIndex<WorkingPixelType, DIMENSION> ContinuousIndexOfGradientLocation;

    featureImage->TransformPhysicalPointToContinuousIndex( gradientLocation, ContinuousIndexOfGradientLocation );

    AddValueToElement( static_cast<scalarType>( imageInterpolator->
                                                EvaluateAtContinuousIndex( ContinuousIndexOfGradientLocation ) ),
                       elementIterator );
    }
}

inline std::map<std::string, scalarType>
FeatureInputVector
::CalculateUnitDeltaAlongTheGradient( std::string ROIName,
                                      WorkingImageType::IndexType currentPixelIndex )
{
  WorkingPixelType deltaX = m_gradientOfROI.find( ROIName )->second->GetPixel( currentPixelIndex )[0];
  WorkingPixelType deltaY = m_gradientOfROI.find( ROIName )->second->GetPixel( currentPixelIndex )[1];
  WorkingPixelType deltaZ = m_gradientOfROI.find( ROIName )->second->GetPixel( currentPixelIndex )[2];

  const scalarType Length = vcl_sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
  const scalarType inverseLength =  ( Length > 0.0F ) ? 1.0 / Length : 1;

  std::map<std::string, scalarType> unitGradient;
  unitGradient["deltaX"] = deltaX * inverseLength;
  unitGradient["deltaY"] = deltaY * inverseLength;
  unitGradient["deltaZ"] = deltaZ * inverseLength;

  return unitGradient;
}

/* Hash Generator from index */
int
FeatureInputVector
::HashKeyFromIndex( const WorkingImageType::IndexType index )
{
  /*
   * calculating offset
   * hashValue = i[2] + i[1]*s[1] + i[0]*s[0]*s[1]
   */
  int hashValue = 0;

  unsigned int lastDimensionIndex = DIMENSION - 1;
  for( unsigned int i = 0; i < (lastDimensionIndex); i++ )
    {
    hashValue += index[i];
    hashValue *= ConstantHashIndexSize[i];
    }
  hashValue += index[lastDimensionIndex];
  return hashValue;
}

WorkingImageType::IndexType
FeatureInputVector
::HashIndexFromKey(const int offSet)
{
  WorkingImageType::IndexType key;

  int remainedOffSet = offSet;
  for( int d = DIMENSION - 1; d >= 0; d-- )
    {
    key[d] = remainedOffSet % ConstantHashIndexSize[d];
    remainedOffSet = remainedOffSet / ConstantHashIndexSize[d];
    }
  return WorkingImageType::IndexType( key );
}

inline std::pair<scalarType, scalarType>
FeatureInputVector
::SetMinMaxOfSubject( BinaryImageType::Pointer & labelImage, const WorkingImagePointer& Image )
{
  typedef itk::LabelStatisticsImageFilter<WorkingImageType, BinaryImageType> StatisticCalculatorType;
  StatisticCalculatorType::Pointer statisticCalculator = StatisticCalculatorType::New();

  statisticCalculator->SetInput( Image );
  statisticCalculator->SetLabelInput( labelImage);

  statisticCalculator->Update();

  /*std::cout << " * Min : " << statisticCalculator->GetMinimum(1)
            << " * Max : " << statisticCalculator->GetMaximum(1)
            << std::endl; */
  return minmaxPairType( std::pair<scalarType, scalarType>( statisticCalculator->GetMinimum(1),
                                                       statisticCalculator->GetMaximum(1) ) );
}

void
FeatureInputVector
::NormalizationOfVector( InputVectorMapType& currentFeatureVector, std::string ROIName )
{
  minmaxPairVectorType currentMinmaxPairVector = m_minmax.find(ROIName)->second;
  for( InputVectorMapType::iterator eachInputVector = currentFeatureVector.begin();
       eachInputVector != currentFeatureVector.end();
       ++eachInputVector )
    {
    InputVectorType::iterator featureElementIterator = (eachInputVector->second).begin();
    featureElementIterator += (roiIDsInOrder.size() + m_spatialLocations.size() );
    for( minmaxPairVectorType::const_iterator minmaxIt = currentMinmaxPairVector.begin();
         minmaxIt != currentMinmaxPairVector.end();
         ++minmaxIt )
      {
      for(  float i = -m_gradientSize; i <= m_gradientSize; i = i + 1.0F )
        {
        scalarType normalizedValue = ( *featureElementIterator - minmaxIt->first );
        normalizedValue = normalizedValue / ( minmaxIt->second - minmaxIt->first );
        *featureElementIterator = normalizedValue;
        featureElementIterator++;
        }
      }
    }
}

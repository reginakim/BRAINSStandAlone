#include "FeatureInputVector.h"
#include "BRAINSCutExceptionStringHandler.h"
#include "itkLabelStatisticsImageFilter.h"

#include "itkAbsoluteValueDifferenceImageFilter.h"

const scalarType FeatureInputVector::MIN = -1.0F;
const scalarType FeatureInputVector::MAX = 1.0F;

FeatureInputVector
::FeatureInputVector() :
  m_gradientSize(-1)
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
::SetImageTypesInOrder( DataSet::StringVectorType & imageList )
{
  imageTypesInOrder = imageList;
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
::SetNormalizationMethod( const std::string normalizationMethod )
{
  if( normalizationMethod == "NONE" )
    {
    m_normalizationMethod = NONE;
    }
  else if( normalizationMethod == "LINEAR" )
    {
    m_normalizationMethod = LINEAR;
    }
  else if( normalizationMethod == "SIGMOID" )
    {
    m_normalizationMethod = SIGMOID;
    }
  else if( normalizationMethod == "DOUBLESIGMOID" )
    {
    m_normalizationMethod = DOUBLESIGMOID;
    }
  else if( normalizationMethod == "ZSCORE" )
    {
    m_normalizationMethod = ZSCORE;
    }
  else if( normalizationMethod == "TANH" )
    {
    m_normalizationMethod = TANH;
    }
  else if( normalizationMethod == "MAD" )
    {
    m_normalizationMethod = MAD;
    }
  else
    {
    std::cout<<"Invalid normalization method is given \n";
    }
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

  /* normalization */

  // this variable can be deleted later on
  //
  SetNormalizationParameters(  ROIName );
  Normalization( currentFeatureVector, ROIName );

  /* insert computed vector */
  m_featureInputOfROI.insert(std::pair<std::string, InputVectorMapType>( ROIName, currentFeatureVector) );
}

/* linear normalization */
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

  DataSet::StringVectorType::iterator imgTyIt = imageTypesInOrder.begin();
  for( WorkingImageVectorType::const_iterator currentTypeOfImage = imagesOfInterestInOrder.begin();
       currentTypeOfImage != imagesOfInterestInOrder.end();
       ++currentTypeOfImage )
    {
    BinaryImageType::Pointer roiMask = thresholder->GetOutput();
    std::string currentParameterGroup =  ROIName + *imgTyIt;
    NormalizationParameterType currentParameter ;
    switch( m_normalizationMethod )
      {
        case LINEAR:
          currentParameter.linearParameter =
            GetLinearNormalizationParametersOfSubject( roiMask , *currentTypeOfImage ); 
          break;

        case SIGMOID:        // SIGMOID and DOUBLESIGMOID share same parameters
        case DOUBLESIGMOID:
          currentParameter.sigmoidParameter =
            GetSigmoidNormalizationParametersOfSubject( roiMask , 
                                                        *currentTypeOfImage ); 
          break;
        case MAD:
          currentParameter.madParameter=
            GetMADNormalizationParametersOfSubject( roiMask ,
                                                    *currentTypeOfImage );
          break;
        default:
          currentParameter.linearParameter =
            GetLinearNormalizationParametersOfSubject( roiMask , *currentTypeOfImage ); 
          break;
      }
    m_normalizationParametersPerImageType[ currentParameterGroup ] = currentParameter;
    ++imgTyIt;
    }
}

void
FeatureInputVector
::Normalization( InputVectorMapType& currentFeatureVector, std::string ROIName )
{

  for( InputVectorMapType::iterator eachInputVector = currentFeatureVector.begin();
       eachInputVector != currentFeatureVector.end();
       ++eachInputVector )
    {
    InputVectorType::iterator featureElementIterator = (eachInputVector->second).begin();
    featureElementIterator += (roiIDsInOrder.size() + m_spatialLocations.size() );

    for( DataSet::StringVectorType::iterator imgTyIt = imageTypesInOrder.begin(); 
         imgTyIt != imageTypesInOrder.end();
         ++imgTyIt ) // imgTyIt = image type iterator
      {
      std::string currentParameterGroup = ROIName + *imgTyIt ; 
      for(  float i = -m_gradientSize; i <= m_gradientSize; i = i + 1.0F )
        {
        // debuging 
        std::cout<<"[ "<< *featureElementIterator << " ]--> ";
        switch( m_normalizationMethod )
        { /* assuming all the ranges to 0-1 */
          case LINEAR:
            *featureElementIterator  = LinearTransform( 
                m_normalizationParametersPerImageType[ currentParameterGroup].linearParameter.min,
                m_normalizationParametersPerImageType[ currentParameterGroup].linearParameter.max,
                *featureElementIterator );
            break;
          case SIGMOID:               // SIGMOID and DOUBLESIGMOID shares a function 
          case DOUBLESIGMOID:         // :: functions will be distinquished by 'm_normalizationMethod'
            *featureElementIterator  = Sigmoid( 
                m_normalizationParametersPerImageType[ currentParameterGroup].sigmoidParameter.median,
                m_normalizationParametersPerImageType[ currentParameterGroup].sigmoidParameter.lowerQuantile,
                m_normalizationParametersPerImageType[ currentParameterGroup].sigmoidParameter.higherQuantile,
                *featureElementIterator,
                m_normalizationMethod);
            break;

          case ZSCORE:
            *featureElementIterator  = StandardTransform( 
                m_normalizationParametersPerImageType[ currentParameterGroup].zScoreParameter.mean,
                m_normalizationParametersPerImageType[ currentParameterGroup].zScoreParameter.std,
                *featureElementIterator );
            break;
          case MAD:
            *featureElementIterator  = StandardTransform( 
                m_normalizationParametersPerImageType[ currentParameterGroup].madParameter.median,
                m_normalizationParametersPerImageType[ currentParameterGroup].madParameter.MAD,
                *featureElementIterator );
            break;
          default:
            *featureElementIterator  = LinearTransform( 
                m_normalizationParametersPerImageType[ currentParameterGroup].linearParameter.min,
                m_normalizationParametersPerImageType[ currentParameterGroup].linearParameter.max,
                *featureElementIterator );
            break;
        }
        std::cout<<"[ "<< *featureElementIterator << " ]"<<std::endl;
        featureElementIterator++;
        }
      }
    }
}
/* linear function*/
inline double
FeatureInputVector
::LinearTransform( double min, double max, double x )
{
  std::cout<<" [LINEAR] :";
  double return_value;

  return_value = (x-min)/(max-min);

  std::cout<< "( "<<x<<" - "<<min<<" ) / ( "<<max<<" - "<<min <<" ) =";
  return return_value;
}

/* standard function*/
inline double
FeatureInputVector
::StandardTransform( double mu, double sigma, double x )
{
  std::cout<<" [Standard] :";
  double return_value;

  return_value = (x-mu)/sigma;

  std::cout<< "( "<<x<<" - "<<mu<<" ) / ( "<<sigma <<" ) = ";
  return return_value;
}

/* sigmoid function*/
inline double
FeatureInputVector
::Sigmoid( double median, double lowerQuantile, double higherQuantile, double x, 
           NormalizationMethodType whichSigmoid)
{
  std::cout<<" [Sigmoid] :";
  /* Implementation from 
   * http://wwwold.ece.utep.edu/research/webfuzzy/docs/kk-thesis/kk-thesis-html/node72.html 
   * */
  double exp_value;
  double return_value;

  const double beta = median;

  //                   1
  // x' = --------------------------------  alpha = (higher-lower )/2, if SIGMOID
  //                       x - beta               = ( beta-lower ), if DOUBLESIGMOID && x < beta
  //       1 + exp( -2 ( ------------ ) )         = ( higher-beta, otherwise
  //                        alpha

  double alpha=0.0F;
  if( whichSigmoid == SIGMOID )
    {
    alpha= (higherQuantile-lowerQuantile) /2.0F;
    }
  else if( whichSigmoid == DOUBLESIGMOID )
    {
    if( x < beta )
      {
      alpha = beta - lowerQuantile;
      }
    else
      {
      alpha = higherQuantile - beta;
      }
    }
  else
    {
    std::cout<<"SIGMOID function should be called only with SIGMOID TYPE function."<<std::endl 
             <<whichSigmoid << " != " << SIGMOID << " nor " << DOUBLESIGMOID 
             <<std::endl;
    exit( EXIT_FAILURE) ;
    }

  exp_value = exp( -2.0F * (x-beta)/alpha );
  return_value=1/(1+exp_value);

  std::cout<< " 1 / ( 1 + exp( -2 * ( "<< x << " - " << beta <<" ) / "<<alpha << " ) ) = "; 

  return return_value;
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

inline FeatureInputVector::LinearNormalizationParameterType 
FeatureInputVector
::GetLinearNormalizationParametersOfSubject( BinaryImageType::Pointer & labelImage, 
                                             const WorkingImagePointer& Image )
{
  typedef itk::LabelStatisticsImageFilter<WorkingImageType, BinaryImageType> StatisticCalculatorType;
  StatisticCalculatorType::Pointer statisticCalculator = StatisticCalculatorType::New();

  statisticCalculator->SetInput( Image );
  statisticCalculator->SetLabelInput( labelImage);

  statisticCalculator->Update();

  std::cout << " * Min : " << statisticCalculator->GetMinimum(1)
            << " * Max : " << statisticCalculator->GetMaximum(1)
            << std::endl; 
  LinearNormalizationParameterType returnParatemer;
  returnParatemer.min = statisticCalculator->GetMinimum(1);
  returnParatemer.max = statisticCalculator->GetMaximum(1);

  return returnParatemer;
}

inline FeatureInputVector::SigmoidNormalizationParameterType 
FeatureInputVector
::GetSigmoidNormalizationParametersOfSubject( BinaryImageType::Pointer & labelImage, 
                                              const WorkingImagePointer& Image )
{
  const unsigned char label = 1;

  typedef itk::LabelStatisticsImageFilter<WorkingImageType, BinaryImageType> StatisticCalculatorType;
  StatisticCalculatorType::Pointer statisticCalculator = StatisticCalculatorType::New();

  statisticCalculator->SetInput( Image );
  statisticCalculator->SetLabelInput( labelImage);

  statisticCalculator->Update();

  const double imgMin = statisticCalculator->GetMinimum( label );
  const double imgMax = statisticCalculator->GetMaximum( label );

  std::cout << " * imgMin :  " << imgMin << std::endl
            << " * imgMax :  " << imgMax << std::endl;

  // histogram on and set parameters has to be together 
  // before second update
  statisticCalculator->UseHistogramsOn();
  statisticCalculator->SetHistogramParameters( 255, imgMin, imgMax );
  statisticCalculator->Update();

  StatisticCalculatorType::HistogramType::Pointer histogram;
  histogram = statisticCalculator->GetHistogram( label );

  if( histogram.IsNull() )
    {
    std::cout<<"Histogram is null"<<std::endl;
    exit( EXIT_FAILURE );
    }
  double Quantile_02 = histogram->Quantile(0, 0.02);
  double Quantile_98 = histogram->Quantile(0, 0.98);
  double median =      histogram->Quantile(0, 0.5);

  SigmoidNormalizationParameterType sigmoidReturnValue;
  sigmoidReturnValue.lowerQuantile  = Quantile_02;
  sigmoidReturnValue.median         = median;
  sigmoidReturnValue.higherQuantile = Quantile_98;

  std::cout << " * Quantile_02 : " << Quantile_02 << std::endl
            << " * Quantile_98 : " << Quantile_98 << std::endl  
            << " * median : " << median << std::endl  ;

  return  sigmoidReturnValue;
}

inline FeatureInputVector::MADNormalizationParameterType
FeatureInputVector
::GetMADNormalizationParametersOfSubject( BinaryImageType::Pointer & labelImage, 
                                          const WorkingImagePointer& Image )
{
  const unsigned char label = 1;

  typedef itk::LabelStatisticsImageFilter<WorkingImageType, BinaryImageType> StatisticCalculatorType;
  StatisticCalculatorType::Pointer statisticCalculator = StatisticCalculatorType::New();

  statisticCalculator->SetInput( Image );
  statisticCalculator->SetLabelInput( labelImage);

  statisticCalculator->Update();

  const double imgMin = statisticCalculator->GetMinimum( label );
  const double imgMax = statisticCalculator->GetMaximum( label );

  std::cout << " * imgMin :  " << imgMin << std::endl
            << " * imgMax :  " << imgMax << std::endl;

  // histogram on and set parameters has to be together 
  // before second update
  statisticCalculator->UseHistogramsOn();
  statisticCalculator->SetHistogramParameters( 255, imgMin, imgMax );
  statisticCalculator->Update();

  StatisticCalculatorType::HistogramType::Pointer histogram;
  histogram = statisticCalculator->GetHistogram( label );

  if( histogram.IsNull() )
    {
    std::cout<<"Histogram is null"<<std::endl;
    exit( EXIT_FAILURE );
    }
  double median =      histogram->Quantile(0, 0.5);

  MADNormalizationParameterType madReturnValue;
  madReturnValue.median         = median;

  std::cout << " * median : " << median << std::endl;

  typedef itk::AbsoluteValueDifferenceImageFilter < WorkingImageType, 
                                                    WorkingImageType,
                                                    WorkingImageType > SubtractFilterType;
  SubtractFilterType::Pointer subtractor = SubtractFilterType::New();
  subtractor->SetInput( Image );
  subtractor->SetConstant( median );
  
  StatisticCalculatorType::Pointer MADStatCalculator= StatisticCalculatorType::New();

  double histMin = median-imgMin ;
  double histMax = imgMax-median ;
  if( histMin > histMax )
  {
    histMax = histMin;
    histMin = imgMax-median ;
  }

  MADStatCalculator->SetInput( subtractor->GetOutput() );
  MADStatCalculator->SetLabelInput(labelImage);
  MADStatCalculator->UseHistogramsOn();
  MADStatCalculator->SetHistogramParameters( 255, histMin , histMax );
  MADStatCalculator->Update();

  std::cout << " * median-imgMin:  " <<median-imgMin <<std::endl;
  std::cout << " * imgMax-median:  " <<imgMax-median <<std::endl;


  madReturnValue.MAD = MADStatCalculator->GetHistogram( label )->Quantile(0,0.5);

  std::cout << " * MAD: " << madReturnValue.MAD << std::endl;
          
  return  madReturnValue ;
}


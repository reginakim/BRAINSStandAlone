#ifndef FeatureInputVector_h
#define FeatureInputVector_h

#include "BRAINSCutDataHandler.h"
#include <itkLinearInterpolateImageFunction.h>
#include <itkGradientImageFilter.h>
/*
 * Note
 * - this class is to compute input vector of ONE subject for a given ROI
 *
 * in this class NO WARPING is occuring.
 * All the images should been warped onto subject space before hand
 */



class FeatureInputVector
{
public:
  FeatureInputVector();

  /** constants definition */
  static const scalarType MIN;
  static const scalarType MAX;

  /** type definition */
  enum NormalizationMethodType { NONE, LINEAR, SIGMOID, DOUBLESIGMOID, ZSCORE, TANH, MAD };

  typedef itk::GradientImageFilter<WorkingImageType,
                                   WorkingPixelType,
                                   WorkingPixelType> GradientFilterType;

  typedef itk::Image<itk::CovariantVector<WorkingPixelType, DIMENSION>, DIMENSION>::Pointer
  GradientImageType;

  typedef itk::Image<unsigned char, DIMENSION> BinaryImageType;

  typedef itk::LinearInterpolateImageFunction<WorkingImageType,
                                              WorkingPixelType> ImageLinearInterpolatorType;

  /** types for normalization **/
  struct LinearNormalizationParameterType {
    double min;
    double max;
  };

  struct SigmoidNormalizationParameterType {
    double median;
    double lowerQuantile;
    double higherQuantile;
  };

  struct ZScoreNormalizationParameterType {
    double mean;
    double std;
  };

  // MAD: Median & median absolute deviation
  struct MADNormalizationParameterType {
    double median;
    double MAD;
  };

  struct NormalizationParameterType {
    LinearNormalizationParameterType linearParameter;
    SigmoidNormalizationParameterType sigmoidParameter;
    ZScoreNormalizationParameterType zScoreParameter;
    MADNormalizationParameterType  madParameter;
  };

  typedef std::map<std::string, NormalizationParameterType> NormalizationParameterPerImageType;


  matrixType  GetInputVectorAt(WorkingImageVectorType & currentIndex);

  /** set functions */
  void SetGradientSize( unsigned int length);

  void SetImagesOfInterestInOrder( WorkingImageVectorType& images);

  void SetImageTypesInOrder( DataSet::StringVectorType & imageList);

  void SetImagesOfSpatialLocation(  std::map<std::string, WorkingImagePointer>& SpatialLocationImages);

  void SetCandidateROIs( std::map<std::string, WorkingImagePointer>& candidateROIMap);

  void SetROIInOrder( DataSet::StringVectorType roiInOrder );

  void SetFeatureInputOfROI( std::map<std::string, WorkingImagePointer>& featureImages );

  void SetInputVectorSize();

  unsigned int GetInputVectorSize();

  void SetNormalizationMethod( const std::string normalizationMethod);




  /** get function(s) */
  InputVectorMapType GetFeatureInputOfROI( std::string ROIName );

  /* HashGenerator From Index */
  /* hash function is based on fixed size of 'size'
   * This would not work if the size of image bigger than the size we are using here.
   * The size could be easily changed though.
   */
  static int                         HashKeyFromIndex(const WorkingImageType::IndexType index);

  static WorkingImageType::IndexType HashIndexFromKey(const int offSet);

private:
  int          m_gradientSize;
  unsigned int m_inputVectorSize;
  NormalizationMethodType m_normalizationMethod;

  ImageLinearInterpolatorType::Pointer imageInterpolator;

  WorkingImageVectorType    imagesOfInterestInOrder;
  DataSet::StringVectorType roiIDsInOrder;
  DataSet::StringVectorType imageTypesInOrder;

  /** deformed rho/phi/theta images*/
  std::map<std::string, WorkingImagePointer> m_spatialLocations;

  /** deformed candiateROIs */
  std::map<std::string, WorkingImagePointer> m_candidateROIs;

  /** gradient image of ROI */
  std::map<std::string, GradientImageType> m_gradientOfROI;

  /** feature output*/
  std::map<std::string, InputVectorMapType> m_featureInputOfROI;

  /** normalization parameters*/
  /*  mapping from ROIname to the vector of mean/max
   *  for given serios of imagesOfInterestInOrder
   */
  NormalizationParameterPerImageType m_normalizationParametersPerImageType;
  
  /** private functions */
  void ComputeFeatureInputOfROI( std::string ROIName);

  void SetGradientImage( std::string ROIName );

  /* normalization */
  void SetNormalizationParameters( std::string ROIName);
  void Normalization( InputVectorMapType& currentFeatureVector, std::string ROIName );

  /** inline functions */
  inline void AddValueToElement( scalarType value, std::vector<scalarType>::iterator & elementIterator);

  inline void AddCandidateROIFeature( WorkingImageType::IndexType currentPixelIndex,
                                      std::vector<scalarType>::iterator & elementIterator);

  inline void AddSpatialLocation( WorkingImageType::IndexType currentPixelIndex,
                                  std::vector<scalarType>::iterator & elementIterator);

  inline void AddFeaturesImagesOfInterest( std::string ROIName, WorkingImageType::IndexType currentPixelIndex,
                                           std::vector<scalarType>::iterator & elementIterator);

  inline void AddFeaturesAlongGradient( std::string ROIName, WorkingImagePointer featureImage,
                                        WorkingImageType::IndexType currentPixelIndex,
                                        std::vector<scalarType>::iterator & elementIterator );

  inline std::map<std::string, scalarType> CalculateUnitDeltaAlongTheGradient(
    std::string ROIName, WorkingImageType::IndexType currentPixelIndex );

  inline LinearNormalizationParameterType GetLinearNormalizationParametersOfSubject ( 
      BinaryImageType::Pointer & labelImage,
      const WorkingImagePointer& Image );
  inline SigmoidNormalizationParameterType GetSigmoidNormalizationParametersOfSubject ( 
      BinaryImageType::Pointer & labelImage,
      const WorkingImagePointer& Image );
  inline MADNormalizationParameterType GetMADNormalizationParametersOfSubject( 
      BinaryImageType::Pointer & labelImage, 
      const WorkingImagePointer& Image );

  inline double LinearTransform( double min, double max, double x );
  inline double StandardTransform( double mu, double sigma, double x );
  inline double Sigmoid( double median, double lowerQuantile, double higherQuantile, double x,
                         NormalizationMethodType whichSigmoid);

};
#endif

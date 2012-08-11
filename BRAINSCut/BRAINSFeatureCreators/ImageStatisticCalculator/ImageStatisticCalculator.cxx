#include "itkImage.h"
#include "itkImageFileReader.h"
#include "itkSubtractConstantFromImageFilter.h"
#include "itkAbsImageFilter.h"
#include "itkLabelStatisticsImageFilter.h"
#include "itkCastImageFilter.h"
#include "itkBinaryThresholdImageFilter.h"

#include "ImageStatisticCalculatorCLP.h"

int main(int argc, char *argv[])
{
  PARSE_ARGS;

  bool violated = false;
  if( inputVolume.size() == 0 )
    {
    violated = true; std::cout << "  --inputVolume Required! "  << std::endl;
    }
  if( violated )
    {
    return EXIT_FAILURE;
    }


  const unsigned int label = 255;

  const unsigned int Dimension = 3;

  // grey scale image 
  typedef double GreyScalePixelType;
  typedef itk::Volume<GreyScalePixelType,  Dimension> GreyScaleVolumeType;

  typedef itk::ImageFileReader<GreyScaleVolumeType>   GreyScaleVolumeReaderType;
  GreyScaleVolumeReaderType::Pointer greyScaleImageReader = GreyScaleVolumeReaderType::New();

  // read in multiple grey scale volumes
  std::map< std::string, GreyScaleVolumeType > greyScaleVolumes;
  for( std::vector< std::string>::const_iterator it = inputVolume.begin();
       it < inputVolume.end();
       it++)
    {
    GreyScaleVolumeReaderType::Pointer greyScaleImageReader = GreyScaleVolumeReaderType::New();
    greyScaleImageReader->SetFileName( *it );
    greyScaleImageReader->Update();

    greyScaleVolumes[ *it ] =  greyScaleImageReader->Update();
    }

  // binary image definition
  typedef unsigned char BinaryPixelType;
  typedef itk::Image<BinaryPixelType,  Dimension> BinaryVolumeType;

  // read in multiple binary (mask) volumes
  //
  typedef itk::BinaryThresholdImageFilter< GreyScaleVolumeType, GreyScaleVolumeType >
          ThresholderType;
  typedef itk::CastImageFilter < GreyScaleVolumeType, BinaryVolumeType >
          CasterImageFilterType;

  std::map< std::string, BinaryVolumeType > binaryVolumes;
  for( std::vector< std::string >::const_iterator it = inputBinaryVolumes.begin();
       it < inputBinaryVolumes.end();
       it++)
    {
    // read in as a grey scale and threshold image to be safe.
    GreyScaleVolumeReaderType::Pointer binaryVolumeReader = GreyScaleVolumeReaderType::New();
    binaryVolumeReader->SetFileName( *it );

    ThresholderType::Pointer thresholder = ThresholderType::New();
    thresholder->SetInput( binaryVolumeReader->GetOutput() );
    thresholder->SetInsideValue( label ); 
    thresholder->SetOutsideValue( 0 );
    thresholder->SetLowerThreshold( 0.5F );

    CasterImageFilterType::Pointer casterToBinaryVolume = CasterImageFilterType::New();
    casterToBinaryVolume->SetInput( thresholder->GetOutput() );
    casterToBinaryVolume->Update();

    binaryVolumes[ *it ] = casterToBinaryVolume->GetOutput() ;
    }

  // Label statistic calculator
  typedef itk::LabelStatisticImageFilter<GreyScaleVolumeType, BinaryVolumeType> LabelStatisticFilterType;

  // MAD calculator
  // Median & median absolute deviation 
  // MAD = median(  | x - median | )
  typedef itk::SubtractConstantFromImageFilter< GreyScaleVolumeType, double, GreyScaleVolumeType >
          SubtractConstantFromImageFilterType;

  typedef itk::AbsImageFilter< GreyScaleVolumeType, GreyScaleVolumeType > 
          AbsoluteImageFilterType;

  for( std::map< GreyScaleVolumeType >::const_iterator imgIt = greyScaleVolumes.begin();
       imgIt < greyScaleVolumes.end();
       imgIt++ )
    {
    // statistical calculation should be re-created for each grey scale images
    LabelStatisticFilterType::Pointer statCalculator= LabelStatisticFilterType::New();
    for( std::map< BinaryVolumeType >::const_iterator mskIt = binaryVolumes.begin();
         mskIt < binaryVolumes.end();
         mskIt++)
      {
      std::cout<<"Img, "<< imgIt->first <<", "
               <<"Msk, "<< mskIt->first <<", ";
      statCalculator->SetInput( imgIt->second );
      statCalculator->SetLabelInput( mskIt->second );
      statCalculator->UseHistogramOn();
      statCalculator->Update();

      std::cout<<"Mean, "<<statCalculator->GetMean( label )<<", ";
      std::cout<<"Maximum, "<<statCalculator->GetMaximum( label )<<", ";
      std::cout<<"Median, "<<statCalculator->GetMedian( label )<<", ";
      std::cout<<"Minimum, "<<statCalculator->GetMinimum( label )<<", ";
      std::cout<<"Count, "<<statCalculator->GetCount( label )<<", ";
      std::cout<<"Sigma, "<<statCalculator->GetSigma( label )<<", ";
      std::cout<<"Sum, "<<statCalculator->GetSum( label )<<", ";
      std::cout<<"Variance, "<<statCalculator->GetVariance( label )<<", ";
      std::cout<<"Mean, "<<statCalculator->GetMean( label )<<", ";

      for( double quantile=0.05; quantile <1.0F; quantile= quantile+0.05)
        {
        std::cout<<quantile*100<<"th Quantile, "
                 <<statCalculator->GetHistogram( label )->Quantile( 0, quantile )<<", ";
        }

      // MAD calculation
      SubtractConstantFromImageFilter::Pointer subtractor = SubtractConstantFromImageFilterType::New();
      subtractor->SetInput( imgIt->second );
      subtractor->SetConstant( statCalculator->GetMedian( label ) );

      AbsoluteImageFilterType::Pointer absoluteFilter = AbsoluteImageFilterType::New();
      absoluteFilter->SetInput( subtractor->GetOutput() );

      LabelStatisticFilterType::Pointer MADCalculator= LabelStatisticFilterType::New();
      MADCalculator->SetInput( absoluteFilter->GetOutput() );
      MADCalculator->UseHistogramOn();
      MADCalculator->Update();

      std::cout<<"MAD, "<<MADCalculator->GetMedian( label )<<", ";
      }

    std::cout<<"END"<<std::endl;
    }

  return EXIT_SUCCESS;
}

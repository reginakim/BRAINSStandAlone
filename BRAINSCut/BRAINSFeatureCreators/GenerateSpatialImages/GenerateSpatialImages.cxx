#include <iostream>
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"

#include "itkNoiseImageFilter.h"

#include "GenerateSpatialImagesCLP.h"


template<typename T> inline T sphericalRho(const x, const y, const z ) 
  {
  return (T) vcl_sqrt( x^2.0 + y^2.0 + z^2.0);
  }
template<typename T> inline T sphericalTheta(const x, const y, const z )
  {
  double rho = sphericalRho( x, y, z);
  return vcl_acos( z / rho );
  }
template<typename T> inline T sphericalPhi(const x, const y, const z ) 
  {
  return (T) vcl_atan2( y/ z )
  }
template<class TImage>
void
CreateNewImageFromTemplate( const TImage::Pointer &TemplateImage,
                            TImage::Pointer &OutputImage)
  {
  TImage::RegionType region;
  region.SetSize( TemplateImage->GetLargestPossibleRegion().GetSize());
  region.SetIndex( TemplateImage->GetLargestPossibleRegion().GetIndex());
  
  OutputImage = TImage::New();
  OutputImage->SetLargestPossibleRegion( region );
  OutputImage->CopyInformation( TemplateImage );
  OutputImage->Allocate();
  outputImage->FillBuffer( 0.0F );
  }
template<class TImage, class TPoint>
void
CartesianToSymetricalSpherical( const TImage inputImage, 
                                const TPoint center )
  {
  TImage::Pointer rhoImg, phiImg, thetaImg;

  CreateNewImageFromTemplate( inputImage, rhoImg );
  CreateNewImageFromTemplate( inputImage, phiImg );
  CreateNewImageFromTemplate( inputImage, thetaImg );

  
    
  }
int main(int argc, char *argv[])
{
  PARSE_ARGS;

  typedef float PixelType;
  const unsigned int Dimension = 3;

  typedef itk::Image<PixelType,  Dimension> ImageType;
  typedef itk::ImageFileReader<ImageType>   ReaderType;
  ReaderType::Pointer imageReader = ReaderType::New();

  imageReader->SetFileName( inputVolume.c_str() );

  typedef itk::NoiseImageFilter<ImageType, ImageType> NoiseImageFilterType;
  NoiseImageFilterType::Pointer noiseFilter = NoiseImageFilterType::New();

  try
    {
    noiseFilter->SetInput( imageReader->GetOutput() );
    noiseFilter->SetRadius( inputRadius);
    noiseFilter->Update();
    }

  catch( itk::ExceptionObject & excep )
    {
    std::cerr << argv[0] << ": exception caught !" << std::endl;
    std::cerr << excep << std::endl;
    throw excep;
    }

  typedef itk::ImageFileWriter<ImageType> ImageWriterType;
  ImageWriterType::Pointer imageWriter = ImageWriterType::New();
  imageWriter->UseCompressionOn();
  imageWriter->SetFileName(outputVolume);
  imageWriter->SetInput( noiseFilter->GetOutput() );
  imageWriter->Update();

  return EXIT_SUCCESS;
}

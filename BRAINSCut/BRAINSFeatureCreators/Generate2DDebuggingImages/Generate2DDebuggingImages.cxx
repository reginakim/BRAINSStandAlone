#include "itkImageFileWriter.h"
#include "itkImageRegionIterator.h"

#include "Generate2DDebuggingImagesCLP.h"

int main( int argc, char *argv[] )
{
  PARSE_ARGS;
  typedef itk::Image< unsigned char, 2> ImageType;
  // Create a black image with a white square
  ImageType::IndexType start;
  start.Fill(0);
         
  ImageType::SizeType size;
  size.Fill(inputSize);
             
  ImageType::RegionType region;
  region.SetSize(size);
  region.SetIndex(start);

  ImageType::SpacingType spacing;
  spacing.Fill( 1 );
                   
  ImageType::Pointer image = ImageType::New();

  image->SetLargestPossibleRegion( region);
  image->SetBufferedRegion( region );
  image->SetRequestedRegion( region );
  image->SetSpacing( spacing );
  image->Allocate();
  //image->FillBuffer(0);

  ImageType::DirectionType direction;
  direction.SetIdentity();

  image->SetDirection( direction );
                         
  itk::ImageRegionIterator<ImageType> imageIterator(image,region);
     
  while(!imageIterator.IsAtEnd())
    {
    if(imageIterator.GetIndex()[0] > begin && imageIterator.GetIndex()[0] < end &&
       imageIterator.GetIndex()[1] > begin && imageIterator.GetIndex()[1] < end)
      {
      imageIterator.Set(255);
      }
    ++imageIterator;
    }
    
  // Write the deformation field
  typedef itk::ImageFileWriter<  ImageType  > WriterType;
  WriterType::Pointer writer = WriterType::New();
  writer->SetInput (  image );
  writer->SetFileName( outputVolume );
  writer->Update();
  
  return EXIT_SUCCESS;
}

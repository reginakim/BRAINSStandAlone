/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkMultiLabelSTAPLEImageFilter.hxx,v $
  Language:  C++
  Date:      $Date: 2004/03/02 01:19:34 $
  Version:   $Revision: 1.3 $

  Copyright (c) 2002 Insight Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/
#ifndef _itkMultiLabelSTAPLEImageFilter_hxx
#define _itkMultiLabelSTAPLEImageFilter_hxx

#include "itkMultiLabelSTAPLEImageFilter.h"

#include "itkLabelVotingImageFilter.h"

#include "vnl/vnl_math.h"

namespace itk
{

template <typename TInputImage, typename TOutputImage, typename TWeights>
void
MultiLabelSTAPLEImageFilter<TInputImage, TOutputImage, TWeights>
::PrintSelf(std::ostream& os, Indent indent) const
{
  Superclass::PrintSelf(os,indent);
  os << indent << "m_HasLabelForUndecidedPixels = "
     << this->m_HasLabelForUndecidedPixels << std::endl;
  os << indent << "m_LabelForUndecidedPixels = "
     << this->m_LabelForUndecidedPixels << std::endl;
}
template< typename TInputImage, typename TOutputImage, typename TWeights >
void
MultiLabelSTAPLEImageFilter< TInputImage, TOutputImage, TWeights >
::GenerateLabelSet()
{
  std::set< unsigned int> labelSet;
  // Record the number of input files.
  const unsigned int numberOfInputs = this->GetNumberOfInputs();

  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    InputConstIteratorType it
      ( this->GetInput( k ), this->GetInput( k )->GetBufferedRegion() );

    for ( it.GoToBegin(); !it.IsAtEnd(); ++it )
      labelSet.insert( it.Get() );
    }

  unsigned int labelCount=0;
  for( std::set<unsigned int>::iterator it=labelSet.begin();
       it!=labelSet.end();
       ++it)
    {
    labelSetMap[labelCount]=*it;
    std::cout<<" "<<*it;
    }
  m_TotalLabelCount= labelSet.size() +1 ;
  std::cout<<std::endl;
}

template< typename TInputImage, typename TOutputImage, typename TWeights >
typename TInputImage::PixelType
MultiLabelSTAPLEImageFilter< TInputImage, TOutputImage, TWeights >
::ComputeMaximumInputValue()
{
  InputPixelType maxLabel = 0;

  // Record the number of input files.
  const unsigned int numberOfInputs = this->GetNumberOfInputs();

  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    InputConstIteratorType it
      ( this->GetInput( k ), this->GetInput( k )->GetBufferedRegion() );

    for ( it.GoToBegin(); !it.IsAtEnd(); ++it )
      maxLabel = vnl_math_max( maxLabel, it.Get() );
    }

  return maxLabel;
}

template< typename TInputImage, typename TOutputImage, typename TWeights >
void
MultiLabelSTAPLEImageFilter< TInputImage, TOutputImage, TWeights >
::AllocateConfusionMatrixArray()
{
  // we need one confusion matrix for every input
  const unsigned int numberOfInputs = this->GetNumberOfInputs();

  this->m_ConfusionMatrixArray.clear();
  this->m_UpdatedConfusionMatrixArray.clear();

  // create the confusion matrix and space for updated confusion matrix for
  // each of the input images
  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    // the confusion matrix has as many rows as there are input labels, and
    // one more column to accomodate "reject" classifications by the combined
    // classifier.
    this->m_ConfusionMatrixArray.push_back
      ( ConfusionMatrixType( this->m_TotalLabelCount+1, this->m_TotalLabelCount ) );
    this->m_UpdatedConfusionMatrixArray.push_back
      ( ConfusionMatrixType( this->m_TotalLabelCount+1, this->m_TotalLabelCount ) );
    }
}

template< typename TInputImage, typename TOutputImage, typename TWeights >
void
MultiLabelSTAPLEImageFilter< TInputImage, TOutputImage, TWeights >
::InitializeConfusionMatrixArrayFromVoting()
{
  const unsigned int numberOfInputs = this->GetNumberOfInputs();

  typedef LabelVotingImageFilter<TInputImage,TOutputImage> LabelVotingFilterType;
  typedef typename LabelVotingFilterType::Pointer LabelVotingFilterPointer;

  typename OutputImageType::Pointer votingOutput;
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  { // begin scope for local filter allocation
    LabelVotingFilterPointer votingFilter = LabelVotingFilterType::New();

    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      {
      votingFilter->SetInput( k, this->GetInput( k ) );
      }
    votingFilter->Update();
    votingOutput = votingFilter->GetOutput();
  } // begin scope for local filter allocation; de-allocate filter

  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  OutputIteratorType out =
    OutputIteratorType( votingOutput, votingOutput->GetRequestedRegion() );

  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  std::cout<< votingOutput ;
  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    this->m_ConfusionMatrixArray[k].Fill( 0.0 );
    std::cout<<__LINE__<<"::"<<__FILE__<<"::k::"<<k<<std::endl;

    InputConstIteratorType in =
      InputConstIteratorType( this->GetInput( k ), votingOutput->GetRequestedRegion() );

    std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

    for ( out.GoToBegin(); ! out.IsAtEnd(); ++out, ++in )
      {
      std::cout<<"["<<k<<","<<in.Get()<<","<<out.Get()<<"]:";
      std::cout<<this->m_ConfusionMatrixArray[k][labelSetMap[in.Get()]][labelSetMap[out.Get()]]
               <<std::endl;
      ++(this->m_ConfusionMatrixArray[k][labelSetMap[in.Get()]][labelSetMap[out.Get()]]);
      }
    }
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  // normalize matrix rows to unit probability sum
  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    for ( InputPixelType inLabel = 0; inLabel < this->m_TotalLabelCount+1; ++inLabel )
      {
      // compute sum over all output labels for given input label
      WeightsType sum = 0;
      for ( OutputPixelType outLabel = 0; outLabel < this->m_TotalLabelCount; ++outLabel )
	      {
	      sum += this->m_ConfusionMatrixArray[k][labelSetMap[inLabel]][labelSetMap[outLabel]];
	      }

      std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
      // make sure that this input label did in fact show up in the input!!
      if ( sum > 0 )
	      {
	      // normalize
	      for ( OutputPixelType outLabel = 0; outLabel < this->m_TotalLabelCount; ++outLabel )
	        {
	        this->m_ConfusionMatrixArray[k][inLabel][outLabel] /= sum;
	        }
        }
      }
    }
}

template< typename TInputImage, typename TOutputImage, typename TWeights >
void
MultiLabelSTAPLEImageFilter< TInputImage, TOutputImage, TWeights >
::InitializePriorProbabilities()
{
  // test for user-defined prior probabilities and create an estimated one if
  // none exists
  if ( this->m_HasPriorProbabilities )
    {
    if ( this->m_PriorProbabilities.GetSize() < this->m_TotalLabelCount )
      {
      itkExceptionMacro ("m_PriorProbabilities array has wrong size " << m_PriorProbabilities << "; should be at least " << 1+this->m_TotalLabelCount );
      }
    }
  else
    {
    this->m_PriorProbabilities.SetSize( 1+this->m_TotalLabelCount );
    this->m_PriorProbabilities.Fill( 0.0 );

    const unsigned int numberOfInputs = this->GetNumberOfInputs();
    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      {
      InputConstIteratorType in = InputConstIteratorType
	( this->GetInput( k ), this->GetOutput()->GetRequestedRegion() );

      for ( in.GoToBegin(); ! in.IsAtEnd(); ++in )
	{
	++(this->m_PriorProbabilities[in.Get()]);
	}
      }

    WeightsType totalProbMass = 0.0;
    for ( InputPixelType l = 0; l < this->m_TotalLabelCount; ++l )
      totalProbMass += this->m_PriorProbabilities[l];
    for ( InputPixelType l = 0; l < this->m_TotalLabelCount; ++l )
      this->m_PriorProbabilities[l] /= totalProbMass;
    }
}

template< typename TInputImage, typename TOutputImage, typename TWeights >
void
MultiLabelSTAPLEImageFilter< TInputImage, TOutputImage, TWeights >
::GenerateData()
{
  // determine the maximum label in all input images
  // this->m_TotalLabelCount = this->ComputeMaximumInputValue() + 1;
  this->GenerateLabelSet();
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  if ( ! this->m_HasLabelForUndecidedPixels )
    {
    this->m_LabelForUndecidedPixels = this->m_TotalLabelCount;
    }
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  // allocate and initialize the confusion matrices
  this->AllocateConfusionMatrixArray();
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  this->InitializeConfusionMatrixArrayFromVoting();

  // test existing or allocate and initialize new array with prior class
  // probabilities
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  this->InitializePriorProbabilities();

  // Allocate the output image.
  typename TOutputImage::Pointer output = this->GetOutput();
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  output->SetBufferedRegion( output->GetRequestedRegion() );
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
  output->Allocate();
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  // Record the number of input files.
  const unsigned int numberOfInputs = this->GetNumberOfInputs();

  // create and initialize all input image iterators
  InputConstIteratorType *it = new InputConstIteratorType[numberOfInputs];
  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
    it[k] = InputConstIteratorType
      ( this->GetInput( k ), output->GetRequestedRegion() );
    }

  // allocate array for pixel class weights
  WeightsType* W = new WeightsType[ this->m_TotalLabelCount ];
  std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

  for ( unsigned int iteration = 0;
	(!this->m_HasMaximumNumberOfIterations) ||
	  (iteration < this->m_MaximumNumberOfIterations);
	++iteration )
    {
    // reset updated confusion matrix
    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      {
      this->m_UpdatedConfusionMatrixArray[k].Fill( 0.0 );
      }

    // reset all input iterators to start
    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      it[k].GoToBegin();

    // use it[0] as indicator for image pixel count
    while ( ! it[0].IsAtEnd() )
      {
      // the following is the E step
      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	      W[ci] = this->m_PriorProbabilities[ci];

      std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
      for ( unsigned int k = 0; k < numberOfInputs; ++k )
	      {
	      const InputPixelType j = it[k].Get();
	      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        {
	        W[ci] *= this->m_ConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]];
	        }
        }
      std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

      // the following is the M step
      WeightsType sumW = W[0];
      for ( OutputPixelType ci = 1; ci < this->m_TotalLabelCount; ++ci )
	      sumW += W[ci];

      if ( sumW )
        {
        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
          W[ci] /= sumW;
        }

      for ( unsigned int k = 0; k < numberOfInputs; ++k )
      	{
	      const InputPixelType j = it[k].Get();
	      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        this->m_UpdatedConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]] += W[ci];

	      // we're now done with this input pixel, so update.
	      ++(it[k]);
	      }
      }
      std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

      // Normalize matrix elements of each of the updated confusion matrices
      // with sum over all expert decisions.
      for ( unsigned int k = 0; k < numberOfInputs; ++k )
        {
        // compute sum over all output classifications
        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        {
	        WeightsType sumW = this->m_UpdatedConfusionMatrixArray[k][0][labelSetMap[ci]];
	        for ( InputPixelType j = 1; j < 1+this->m_TotalLabelCount; ++j )
	          sumW += this->m_UpdatedConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]];

	        // normalize with for each class ci
	        if ( sumW )
	          {
	          for ( InputPixelType j = 0; j < 1+this->m_TotalLabelCount; ++j )
              this->m_UpdatedConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]] /= sumW;
            }
          }
        }
      std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

      // now we're applying the update to the confusion matrices and compute the
      // maximum parameter change in the process.
      WeightsType maximumUpdate = 0;
      for ( unsigned int k = 0; k < numberOfInputs; ++k )
        for ( InputPixelType j = 0; j < 1+this->m_TotalLabelCount; ++j )
	        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	          {
	          const WeightsType thisParameterUpdate =
	              fabs( this->m_UpdatedConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]] -
		            this->m_ConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]] );

	          maximumUpdate = vnl_math_max( maximumUpdate, thisParameterUpdate );

	          this->m_ConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]] =
	          this->m_UpdatedConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]];
	          }

      this->InvokeEvent( IterationEvent() );
      if( this->GetAbortGenerateData() )
        {
        this->ResetPipeline();
        // fake this to cause termination; we could really just break
        maximumUpdate = 0;
        }

      // if all confusion matrix parameters changes by less than the defined
      // threshold, we're done.
      if ( maximumUpdate < this->m_TerminationUpdateThreshold )
        break;
    } // end for ( iteration )
    std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

    // now we'll build the combined output image based on the estimated
    // confusion matrices

    // reset all input iterators to start
    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      it[k].GoToBegin();

    std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
    // reset output iterator to start
    OutputIteratorType out   = OutputIteratorType( output, output->GetRequestedRegion() );
    for ( out.GoToBegin(); !out.IsAtEnd(); ++out )
      {
      // basically, we'll repeat the E step from above
      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
        W[ci] = this->m_PriorProbabilities[ci];

      for ( unsigned int k = 0; k < numberOfInputs; ++k )
        {
        const InputPixelType j = it[k].Get();
        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        {
	        W[ci] *= this->m_ConfusionMatrixArray[k][labelSetMap[j]][labelSetMap[ci]];
	        }
        ++it[k];
        }

    std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;
    // now determine the label with the maximum W
    OutputPixelType winningLabel = this->m_TotalLabelCount;
    WeightsType winningLabelW = 0;
    for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
      {
      if ( W[ci] > winningLabelW )
	      {
	      winningLabelW = W[ci];
	      winningLabel = ci;
        }
      else
        if ( ! (W[ci] < winningLabelW ) )
          {
          winningLabel = this->m_TotalLabelCount;
          }
      }
    out.Set( winningLabel );
    }
    std::cout<<__LINE__<<"::"<<__FILE__<<std::endl;

    delete[] W;
    delete[] it;
}

} // end namespace itk

#endif

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
    m_LabelSetMap[*it]=labelCount;
    std::cout<<" "<<*it;
    labelCount++;
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
  { // begin scope for local filter allocation
    LabelVotingFilterPointer votingFilter = LabelVotingFilterType::New();

    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      {
      votingFilter->SetInput( k, this->GetInput( k ) );
      }
    votingFilter->Update();
    votingOutput = votingFilter->GetOutput();
  } // begin scope for local filter allocation; de-allocate filter

  OutputIteratorType out =
    OutputIteratorType( votingOutput, votingOutput->GetRequestedRegion() );

  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    this->m_ConfusionMatrixArray[k].Fill( 0.0 );

    InputConstIteratorType in =
      InputConstIteratorType( this->GetInput( k ), votingOutput->GetRequestedRegion() );

    in.GoToBegin();
    
    for ( out.GoToBegin(); ! out.IsAtEnd(); ++out, ++in )
      {
      unsigned int inLabel =m_LabelSetMap[in.Get()];
      unsigned int outLabel=m_LabelSetMap[out.Get()];
      ++(this->m_ConfusionMatrixArray[k][ inLabel ][ outLabel ] );
      }
    }

  // normalize matrix rows to unit probability sum
  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    //for ( InputPixelType inLabel = 0; inLabel < this->m_TotalLabelCount+1; ++inLabel )
    for( std::map<unsigned int, unsigned int>::iterator inLabelIt=m_LabelSetMap.begin();
         inLabelIt != m_LabelSetMap.end();
         ++inLabelIt)
      {
      // compute sum over all output labels for given input label
      WeightsType sum = 0;
      for( std::map<unsigned int, unsigned int>::iterator outLabelIt=m_LabelSetMap.begin();
           outLabelIt != m_LabelSetMap.end();
           ++outLabelIt )
	      {
	      sum += this->m_ConfusionMatrixArray[k][ (*inLabelIt).second ][ (*outLabelIt).second ];
	      }

      // make sure that this input label did in fact show up in the input!!
      if ( sum > 0 )
	      {
	      // normalize
        for( std::map<unsigned int, unsigned int>::iterator outLabelIt=m_LabelSetMap.begin();
             outLabelIt != m_LabelSetMap.end();
             ++outLabelIt )
	        {
	        this->m_ConfusionMatrixArray[k][ (*inLabelIt).second ][ (*outLabelIt).second ] /= sum;
	        }
        }
      std::cout<<"sum::"<<sum<<std::endl;
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
      itkExceptionMacro ("m_PriorProbabilities array has wrong size " 
                          << m_PriorProbabilities 
                          << "; should be at least " << 1+this->m_TotalLabelCount );
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
	      ++(this->m_PriorProbabilities[m_LabelSetMap[in.Get()]]);
	      }
      }

    WeightsType totalProbMass = 0.0;
    for ( InputPixelType l = 0; l < this->m_TotalLabelCount; ++l )
      totalProbMass += this->m_PriorProbabilities[m_LabelSetMap[l]];
    for ( InputPixelType l = 0; l < this->m_TotalLabelCount; ++l )
      this->m_PriorProbabilities[m_LabelSetMap[l]] /= totalProbMass;
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

  if ( ! this->m_HasLabelForUndecidedPixels )
    {
    this->m_LabelForUndecidedPixels = this->m_TotalLabelCount;
    }

  // allocate and initialize the confusion matrices
  this->AllocateConfusionMatrixArray();
  this->InitializeConfusionMatrixArrayFromVoting();

  // test existing or allocate and initialize new array with prior class
  // probabilities
  this->InitializePriorProbabilities();

  // Allocate the output image.
  typename TOutputImage::Pointer output = this->GetOutput();
  output->SetBufferedRegion( output->GetRequestedRegion() );
  output->Allocate();

  // Record the number of input files.
  const unsigned int numberOfInputs = this->GetNumberOfInputs();

  // create and initialize all input image iterators
  InputConstIteratorType *it = new InputConstIteratorType[numberOfInputs];
  for ( unsigned int k = 0; k < numberOfInputs; ++k )
    {
    it[k] = InputConstIteratorType
      ( this->GetInput( k ), output->GetRequestedRegion() );
    }

  // allocate array for pixel class weights
  WeightsType* W = new WeightsType[ this->m_TotalLabelCount ];

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
	      W[m_LabelSetMap[ci]] = this->m_PriorProbabilities[m_LabelSetMap[ci]];

      for ( unsigned int k = 0; k < numberOfInputs; ++k )
	      {
	      const InputPixelType j = it[k].Get();
	      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        {
	        W[m_LabelSetMap[ci]] *= this->m_ConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]];
	        }
        }

      // the following is the M step
      WeightsType sumW = W[0];
      for ( OutputPixelType ci = 1; ci < this->m_TotalLabelCount; ++ci )
	      sumW += W[m_LabelSetMap[ci]];

      if ( sumW )
        {
        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
          W[m_LabelSetMap[ci]] /= sumW;
        }

      for ( unsigned int k = 0; k < numberOfInputs; ++k )
      	{
	      const InputPixelType j = it[k].Get();
	      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        this->m_UpdatedConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]] += W[m_LabelSetMap[ci]];

	      // we're now done with this input pixel, so update.
	      ++(it[k]);
	      }
      }

      // Normalize matrix elements of each of the updated confusion matrices
      // with sum over all expert decisions.
      for ( unsigned int k = 0; k < numberOfInputs; ++k )
        {
        // compute sum over all output classifications
        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        {
	        WeightsType sumW = this->m_UpdatedConfusionMatrixArray[k][0][m_LabelSetMap[ci]];
	        for ( InputPixelType j = 1; j < 1+this->m_TotalLabelCount; ++j )
	          sumW += this->m_UpdatedConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]];

	        // normalize with for each class ci
	        if ( sumW )
	          {
	          for ( InputPixelType j = 0; j < 1+this->m_TotalLabelCount; ++j )
              this->m_UpdatedConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]] /= sumW;
            }
          }
        }

      // now we're applying the update to the confusion matrices and compute the
      // maximum parameter change in the process.
      WeightsType maximumUpdate = 0;
      for ( unsigned int k = 0; k < numberOfInputs; ++k )
        for ( InputPixelType j = 0; j < 1+this->m_TotalLabelCount; ++j )
	        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	          {
	          const WeightsType thisParameterUpdate =
	              fabs( this->m_UpdatedConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]] -
		            this->m_ConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]] );

	          maximumUpdate = vnl_math_max( maximumUpdate, thisParameterUpdate );

	          this->m_ConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]] =
	          this->m_UpdatedConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]];
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

    // now we'll build the combined output image based on the estimated
    // confusion matrices

    // reset all input iterators to start
    for ( unsigned int k = 0; k < numberOfInputs; ++k )
      it[k].GoToBegin();

    // reset output iterator to start
    OutputIteratorType out   = OutputIteratorType( output, output->GetRequestedRegion() );
    for ( out.GoToBegin(); !out.IsAtEnd(); ++out )
      {
      // basically, we'll repeat the E step from above
      for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
        W[m_LabelSetMap[ci]] = this->m_PriorProbabilities[m_LabelSetMap[ci]];

      for ( unsigned int k = 0; k < numberOfInputs; ++k )
        {
        const InputPixelType j = it[k].Get();
        for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
	        {
	        W[m_LabelSetMap[ci]] *= this->m_ConfusionMatrixArray[k][m_LabelSetMap[j]][m_LabelSetMap[ci]];
	        }
        ++it[k];
        }

    // now determine the label with the maximum W
    OutputPixelType winningLabel = this->m_TotalLabelCount;
    WeightsType winningLabelW = 0;
    for ( OutputPixelType ci = 0; ci < this->m_TotalLabelCount; ++ci )
      {
      if ( W[m_LabelSetMap[ci]] > winningLabelW )
	      {
	      winningLabelW = W[m_LabelSetMap[ci]];
	      winningLabel = m_LabelSetMap[ci];
        }
      else
        if ( ! (W[m_LabelSetMap[ci]] < winningLabelW ) )
          {
          winningLabel = this->m_TotalLabelCount;
          }
      }
    out.Set( winningLabel );
    }

    delete[] W;
    delete[] it;
}

} // end namespace itk

#endif

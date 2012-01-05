#include "BRAINSCutTrainModel.h"
#include "NeuralParams.h"

BRAINSCutTrainModel
::BRAINSCutTrainModel( std::string netConfigurationFIlename)
  : BRAINSCutPrimary( netConfigurationFIlename ),
  trainIteration(0),
  trainEpochIteration(0),
  trainDesiredError(0.0),
  trainMaximumDataSize(0),
  ANNHiddenNodesNumber(0),
  activationSlope(0),
  activationMinMax(0)
{
  ANNParameterNetConfiguration = BRAINSCutNetConfiguration.Get<ANNParams>("ANNParams");
  ANNLayerStructure = cvCreateMat( 1, 3, CV_32SC1);
}

/** train */
void
BRAINSCutTrainModel
::InitializeTrainDataSet()
{
  
  const std::string Local_ANNVectorFilenamePrefix = this->GetANNVectorFilenamePrefix();

  trainingDataSet = new BRAINSCutVectorTrainingSet( Local_ANNVectorFilenamePrefix);
  try
    {
    trainingDataSet->ReadHeaderFileInformation();
    }
  catch( BRAINSCutExceptionStringHandler& e )
    {
    std::cout << e.Error();
    exit(EXIT_FAILURE);
    }
  trainingDataSet->SetRecordSize();
  trainingDataSet->SetBufferRecordSize();
  trainingDataSet->ShuffleVectors();
  if( trainingDataSet->GetTotalVectorSize() > (int)trainMaximumDataSize )
    {
    unsigned int numberOfSubSet =  (float)trainingDataSet->GetTotalVectorSize() / (float)trainMaximumDataSize;
    numberOfSubSet = ceil(numberOfSubSet) + 1;
    std::cout << "Divide subset into " << numberOfSubSet << std::endl;
    trainingDataSet->SetNumberOfSubSet( numberOfSubSet );
    }
  else
    {
    trainingDataSet->SetNumberOfSubSet( 1 );
    }
}

void
BRAINSCutTrainModel
::InitializeNeuralNetwork()
{
  SetIterationFromNetConfiguration();
  SetEpochIterationFromNetConfiguration();
  SetDesiredErrorFromNetConfiguration();
  SetMaximumDataSizeFromNetConfiguration();
  SetANNHiddenNodesNumberFromNetConfiguration();
  SetActivatioinFunctionFromNetConfiguration();
  SetModelBasename();

}

inline void
BRAINSCutTrainModel
::TrainWithUpdate( neuralNetType& myTrainer, bool update, pairedTrainingSetType& currentTrainData )
{
  int updateOption = 0;
  if( update )
    {
    updateOption = CvANN_MLP::UPDATE_WEIGHTS;
    }
  // TODO change subset number properly

  myTrainer.train( currentTrainData.pairedInput,
                   currentTrainData.pairedOutput,
                   NULL, // Sample weight
                   0,    // Sample Index,
                   CvANN_MLP_TrainParams( cvTermCriteria( CV_TERMCRIT_ITER
                                                          | CV_TERMCRIT_EPS,
                                                          trainEpochIteration, trainDesiredError),
                                          CvANN_MLP_TrainParams::RPROP,  //
                                          0.1,                           //
                                          FLT_EPSILON ),
                   updateOption);
}

inline void
BRAINSCutTrainModel
::SaveRFTrainModelAtIteration( CvRTrees& myTrainer, int depth, int NTrees)
{
  char tempDepth[5];
  sprintf( tempDepth, "%04u", depth );

  char tempNTrees[5];
  sprintf( tempNTrees, "%04u", NTrees );

  std::string filename = modelBasename + "D"+tempDepth+"NF"+tempNTrees;

  myTrainer.save( filename.c_str() );
}

inline void
BRAINSCutTrainModel
::SaveANNTrainModelAtIteration( neuralNetType& myTrainer, unsigned int No)
{
  char tempid[10];

  sprintf( tempid, "%09u", No + 1 );
  std::string filename = modelBasename + tempid;

  myTrainer.save( filename.c_str() );
}

inline void
BRAINSCutTrainModel
::printTrainInformation( neuralNetType& myTrainer, unsigned int No )
{
  std::cout << " Error :: " << myTrainer.get_MSE()
            << " at " << No + 1
            << std::endl;
}

inline int *
BRAINSCutTrainModel
::GetANNLayerStructureArray()
{
  int * layer = new int[3];

  layer[0] = trainingDataSet->GetInputVectorSize();
  layer[1] = ANNHiddenNodesNumber;
  layer[2] = trainingDataSet->GetOutputVectorSize();

  return layer;
}

void
BRAINSCutTrainModel
::TrainANN()
{

  neuralNetType * trainner = new neuralNetType();
  int*            layer = GetANNLayerStructureArray();

  cvInitMatHeader( ANNLayerStructure, 1, 3, CV_32SC1, layer );

  trainner->create( ANNLayerStructure,
                    CvANN_MLP::SIGMOID_SYM,
                    activationSlope,
                    activationMinMax);

  for( unsigned int currentIteration = 0;
       currentIteration < trainIteration;
       currentIteration++ )
    {
    unsigned int subSetNo =  currentIteration % trainingDataSet->GetNumberOfSubSet();
    TrainWithUpdate( *trainner,
                     (currentIteration > 0),
                     *(trainingDataSet->GetTrainingSubSet(subSetNo) ) );
    SaveANNTrainModelAtIteration( *trainner, currentIteration );
    printTrainInformation( *trainner, currentIteration );
    if( trainner->get_MSE()  < trainDesiredError )
      {
      std::cout << "CONVERGED with " << trainner->get_MSE() << std::endl;
      break;
      }
    }
}

/** random forest training */
void
BRAINSCutTrainModel
::TrainRandomForest( int maxDepth, 
                     int minSampleCount, 
                     bool useSurrogates,
                     bool calcVarImportance,
                     int maxTreeCount
                     )
{
  CvRTrees forest;

  for( int depth=1; depth<maxDepth; depth++)
  {
    CvRTParams randomTreeTrainParamters=
      CvRTParams( depth, 
                  minSampleCount,
                  0.0F,             //float  _regression_accuracy=0, 
                  useSurrogates, 
                  10,               //int    _max_categories=10, 
                  0,                //float* _priors,
                  calcVarImportance, //bool   _calc_var_importance=false,
                  0,                //int    _nactive_vars=0, 
                  maxTreeCount,     
                  0,                //float  forest_accuracy=0, 
                  0
                );
        
    forest.train( trainingDataSet->GetTrainingSubSet(0)->pairedInput,
                CV_ROW_SAMPLE, // or CV_COL_SAMPLE
                trainingDataSet->GetTrainingSubSet(0)->pairedOutputRF,
                0,
                0,//CvMat* sampleIdx=0,
                0,//CvMat* varType=0,
                0,//CvMat* missingMask=0,
                randomTreeTrainParamters
                );

    SaveRFTrainModelAtIteration( forest, depth, maxTreeCount );
  }
}

/** setting function with net configuration */
void
BRAINSCutTrainModel
::SetModelBasename()
{
  NeuralParams * model = BRAINSCutNetConfiguration.Get<NeuralParams>("NeuralNetParams");

  modelBasename = model->GetAttribute<StringValue>("TrainingModelFilename");
}

std::string
BRAINSCutTrainModel
::GetANNVectorFilenamePrefix()
{
  NeuralParams * model = BRAINSCutNetConfiguration.Get<NeuralParams>("NeuralNetParams");

  return model->GetAttribute<StringValue>("TrainingVectorFilename");
}

void
BRAINSCutTrainModel
::SetIterationFromNetConfiguration()
{
  trainIteration = ANNParameterNetConfiguration->GetAttribute<IntValue>("Iterations");
}

void
BRAINSCutTrainModel
::SetEpochIterationFromNetConfiguration()
{
  trainEpochIteration = ANNParameterNetConfiguration->GetAttribute<IntValue>("EpochIterations");
}

void
BRAINSCutTrainModel
::SetDesiredErrorFromNetConfiguration()
{
  trainDesiredError = ANNParameterNetConfiguration->GetAttribute<FloatValue>("DesiredError");
}

void
BRAINSCutTrainModel
::SetMaximumDataSizeFromNetConfiguration()
{
  trainMaximumDataSize = ANNParameterNetConfiguration->GetAttribute<IntValue>("MaximumVectorsPerEpoch");
}

void
BRAINSCutTrainModel
::SetANNHiddenNodesNumberFromNetConfiguration()
{
  ANNHiddenNodesNumber = ANNParameterNetConfiguration->GetAttribute<IntValue>("NumberOfHiddenNodes");
}

void
BRAINSCutTrainModel
::SetActivatioinFunctionFromNetConfiguration()
{
  activationSlope = ANNParameterNetConfiguration->GetAttribute<FloatValue>("ActivationSlope");
  activationMinMax = ANNParameterNetConfiguration->GetAttribute<FloatValue>("ActivationMinMax");
}

/** default functions to set/get member variables */
void
BRAINSCutTrainModel
::SetIteration(unsigned int iteration)
{
  trainIteration = iteration;
}

unsigned int
BRAINSCutTrainModel
::GetIteration()
{
  return trainIteration;
}

void
BRAINSCutTrainModel
::SetEpochIteration( unsigned int epochIteration)
{
  trainEpochIteration = epochIteration;
}

unsigned int
BRAINSCutTrainModel
::GetEpochIteration()
{
  return trainEpochIteration;
}

void
BRAINSCutTrainModel
::SetDesiredError( float desiredError )
{
  trainDesiredError = desiredError;
}

float
BRAINSCutTrainModel
::GetDesiredError()
{
  return trainDesiredError;
}

void
BRAINSCutTrainModel
::SetMaximumDataSize( unsigned int maximumDataSize)
{
  trainMaximumDataSize = maximumDataSize;
}

unsigned int
BRAINSCutTrainModel
::GetMaximumDataSize()
{
  return trainMaximumDataSize;
}

void
BRAINSCutTrainModel
::SetANNHiddenNodesNumber( int hiddenNodes)
{
  ANNHiddenNodesNumber = hiddenNodes;
}

int
BRAINSCutTrainModel
::GetANNHiddenNodesNumber()
{
  return ANNHiddenNodesNumber;
}

void
BRAINSCutTrainModel
::SetActivationFunction( float slope, float minMax)
{
  activationSlope = slope;
  activationMinMax = minMax;
}

float
BRAINSCutTrainModel
::GetActivationSlope()
{
  return activationSlope;
}

float
BRAINSCutTrainModel
::GetActivationMinMax()
{
  return activationMinMax;
}

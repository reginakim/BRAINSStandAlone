#include "BRAINSCutExceptionStringHandler.h"
#include "BRAINSCutVectorTrainingSet.h"
#include "ANNParams.h"

class BRAINSCutTrainModel : public BRAINSCutPrimary
{
public:
  BRAINSCutTrainModel( std::string netConfigurationFilename );

  /** train */
  void InitializeNeuralNetwork();

  void InitializeTrainDataSet();

  void TrainANN();
  void TrainRandomForest( int maxDepth=5, 
                          int minSampleCount=10, 
                          bool useSurrogates=false,
                          bool calcVarImportance=false,
                          int maxTreeCount=10  );

  /** inline functions */
  inline void TrainWithUpdate(neuralNetType& myTrainer, bool update, pairedTrainingSetType& currentTrainData);

  inline void SaveANNTrainModelAtIteration( neuralNetType& myTrainer, unsigned int No);
  inline void SaveRFTrainModelAtIteration( CvRTrees& myTrainer, int depth, int NTrees);

  inline void printTrainInformation( neuralNetType& myTrainer, unsigned int No );

  inline int * GetANNLayerStructureArray();

  /** setting function with net configuration */
  std::string GetModelBasename();

  std::string GetANNVectorFilenamePrefix();

  void SetIterationFromNetConfiguration();

  void SetEpochIterationFromNetConfiguration();

  void SetDesiredErrorFromNetConfiguration();

  void SetMaximumDataSizeFromNetConfiguration();

  void SetANNHiddenNodesNumberFromNetConfiguration();

  void SetActivatioinFunctionFromNetConfiguration();

  void SetModelBasename();

  /** default functions to set/get member variables */
  void SetIteration(unsigned int iteration);

  unsigned int GetIteration();

  void SetEpochIteration( unsigned int epochIteration);

  unsigned int GetEpochIteration();

  void SetDesiredError( float desiredError );

  float GetDesiredError();

  void SetMaximumDataSize( unsigned int maximumDataSize);

  unsigned int GetMaximumDataSize();

  void SetANNHiddenNodesNumber( int hiddenNodes);

  int GetANNHiddenNodesNumber();

  void SetActivationFunction( float slope, float minMax);

  float GetActivationSlope();

  float GetActivationMinMax();

private:
  /* train parameters */
  ANNParams *ANNParameterNetConfiguration;

  unsigned int trainIteration;
  unsigned int trainEpochIteration;
  float        trainDesiredError;
  unsigned int trainMaximumDataSize;

  int ANNHiddenNodesNumber;

  float activationSlope;
  float activationMinMax;

  std::string                 modelBasename;
  std::string                 ANNVectorFilenamePrefix;
  BRAINSCutVectorTrainingSet* trainingDataSet;

  matrixType ANNLayerStructure;
};

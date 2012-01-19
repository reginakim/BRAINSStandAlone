#ifndef TrainingParameters_h
#define TrainingParameters_h
#include "StringValue.h"
#include "IntValue.h"
#include "FloatValue.h"
#include "BooleanValue.h"
#include "XMLElementParser.h"

class TrainingParameters : public XMLElementParser
{
public:
  typedef XMLElementParser SuperClass;
  virtual int PrintSelf(std::ostream & os, int indent) const
  {
    indent += SuperClass::PrintSelf(os, indent);
    os << this->PrintSpaces(indent) << "=== TrainingParameters ===" << std::endl;
    return indent + 2;
  }

  TrainingParameters(std::string method) : XMLElementParser(method.c_str())
  {
    if( method == "ANN" )
      {
      this->Add(new IntValue("Iterations", "20"), "Iterations");
      this->Add(new IntValue("MaximumVectorsPerEpoch", "2000"), "MaximumVectorsPerEpoch");
      this->Add(new IntValue("EpochIterations", 100), "EpochIterations");
      this->Add(new IntValue("ErrorInterval", 5), "ErrorInterval");
      this->Add(new FloatValue("DesiredError", 1.0), "DesiredError");
      this->Add(new FloatValue("ActivationSlope", 0.001), "ActivationSlope");
      this->Add(new FloatValue("ActivationMinMax", 1.0), "ActivationMinMax");
      this->Add(new IntValue("NumberOfHiddenNodes", 0), "NumberOfHiddenNodes");
      }
    else if( method == "RandomForest" )
      {
      // TODO :: ADD proper initialization
      this->Add(new IntValue("maxDepth", "5" ), "maxDepth");
      this->Add(new IntValue("minSampleCount", "5" ), "minSampleCount");
      this->Add(new BooleanValue("useSurrogates",false),"useSurrogates");
      this->Add(new BooleanValue("calcVarImportance",false),"calcVarImportance");
      this->Add(new IntValue("maxTreeCount", "5" ), "maxTreeCount");
      }
    else
      {
      std::cout<<"ERROR::: the training method `" 
               <<method
               <<" does not supported "
               <<std::endl;
      exit(EXIT_FAILURE);
      }
  }

};

#endif // TrainingParameters_h

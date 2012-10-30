##############################################################################
def get_global_sge_script(pythonPathsList,binPathsList,customEnvironment={}):
    """This is a wrapper script for running commands on an SGE cluster
so that all the python modules and commands are pathed properly"""

    custEnvString=""
    for key,value in customEnvironment.items():
        custEnvString+="export "+key+"="+value+"\n"

    PYTHONPATH=":".join(pythonPathsList)
    BASE_BUILDS=":".join(binPathsList)
    GLOBAL_SGE_SCRIPT="""#!/bin/bash
echo "STARTED at: $(date +'%F-%T')"
echo "Ran on: $(hostname)"
export PATH={BINPATH}
export PYTHONPATH={PYTHONPATH}

echo "========= CUSTOM ENVIORNMENT SETTINGS =========="
echo "export PYTHONPATH={PYTHONPATH}"
echo "export PATH={BINPATH}"
echo "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"

echo "With custom environment:"
echo {CUSTENV}
{CUSTENV}
## NOTE:  nipype inserts the actual commands that need running below this section.
""".format(PYTHONPATH=PYTHONPATH,BINPATH=BASE_BUILDS,CUSTENV=custEnvString)
    return GLOBAL_SGE_SCRIPT


# --------------------------------------------------------------------------------------- #
def findInputImagesForSubject( inputT1, outputDir ):
  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print inputT1
  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  import os
  import sys

  TissueClassifyDir = os.path.dirname( inputT1 )
  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print TissueClassifyDir
  outputT2 = TissueClassifyDir + "/t2_average_BRAINSABC.nii.gz"
  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print outputT2

  ScanDir = os.path.dirname( os.path.dirname( TissueClassifyDir ))
  outputInitialTransform = ScanDir + "/ACPCAlign/landmarkInitializer_atlas_to_subject_transform.h5"

  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print ScanDir
  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print outputInitialTransform

  result = {'t1':inputT1, 't2':outputT2, 'transform':outputInitialTransform}
  # --------------------------------------------------------------------------------------- #
  # subject workflow
  #

  ## find site
  subjectID_date_postFix  = os.path.basename( ScanDir )   # ex) 427997062_20090826_30

  siteID    = os.path.basename( os.path.dirname( os.path.dirname( ScanDir )))
  subjectID = subjectID_date_postFix.split( '_' )[0]
  date      = subjectID_date_postFix.split( '_' )[1]


  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print "site::" + siteID +", subjectID::" + subjectID + ",date::"+date
  print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

  import WFPerSubject   
  
  inputTemplateDir = "/ipldev/scratch/eunyokim/src/BRAINSStandAlone/build20121015/ReferenceAtlas-build/Atlas/Atlas_20120830/"

  WFPerSubject.WFPerSubjectDef( result,
                                inputTemplateDir,
                                outputDir+"_Cache/"+siteID+"/"+subjectID+"/"+date, 
                                outputDir+"_Result/"+siteID+"/"+subjectID+"/"+date)

# --------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------- #


import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function
import nipype.interfaces.io as nio

# --------------------------------------------------------------------------------------- #
# workflow
#
outputBaseDir = "/scratch/eunyokim/LabelStatistics/RobustStats/TrackOn_Analysis/"

myWF = pe.Workflow(name="Analysis")
myWF.base_dir = outputBaseDir+"/_Cache"


# --------------------------------------------------------------------------------------- #
# data src : looking for t1_average images
#

dataSrc =  nio.DataGrabber( outfields = ['t1'])

dataSrc.inputs.base_directory = "/hjohnson/TrackOn/Experiments/TrackOn_2012_Results/"
dataSrc.inputs.template = '*'
dataSrc.inputs.field_template = dict( t1 = 'HDNI*/*/*/TissueClassify/BABC//t1_average_BRAINSABC.nii.gz' )
results=dataSrc.run()

print results.outputs.t1
# --------------------------------------------------------------------------------------- #

# --------------------------------------------------------------------------------------- #
#connect discovered dataSrc to subject workflow
#

findRestInputsFromT1 = pe.Node( name = "FindInputsForSubject",
                                interface= Function ( input_names = ['inputT1','outputDir'],
                                                      output_names = [ 'outputListOfSubjectVolumes' ],
                                                      function = findInputImagesForSubject ),
                                iterfield = ['inputT1']
                              )
findRestInputsFromT1.inputs.outputDir = outputBaseDir
myWF.add_nodes( [findRestInputsFromT1] )
findRestInputsFromT1.iterables = ('inputT1', results.outputs.t1)

# if cluster
#BAWSrcDir="/ipldev/scratch/eunyokim/src/BRAINSStandAlone/BRAINSStandAlone/"
#BAWBuildDir="/ipldev/scratch/eunyokim/src/BRAINSStandAlone/build20121015/"
#
#pythonPath = BAWSrcDir+"/BRAINSCut/BRAINSFeatureCreators/RobustStatisticComputations:"+BAWSrcDir+"/AutoWorkup/:"+BAWSrcDir+"/AutoWorkup/BRAINSTools/:"+BAWBuildDir+"/SimpleITK-build/bin/"+BAWBuildDir+"/SimpleITK-build/lib:"
#
#binPath = BAWBuildDir + "/bin:" + BAWBuildDir + "/lib"
#binPath=binPath.split(':')
#binPath.extend(os.environ['PATH'].split(':'))
#os.environ['PATH']=':'.join(binPath)
#
#Cluster_Script = get_global_sge_script( pythonPath, 
#                                        binPath
#                                      )
myWF.run( plugin='SGE',
          plugin_args = dict( template = Cluster_Script, 
                              qsub_args = "-S /bin/bash -pe smp1 4-8 -o /dev/null -q all.q "))
# else        
myWF.run()

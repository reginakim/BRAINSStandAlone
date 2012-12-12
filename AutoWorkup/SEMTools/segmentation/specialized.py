"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os
from nipype.interfaces.slicer.base import SlicerCommandLine


class BRAINSCutInputSpec(CommandLineInputSpec):
    netConfiguration = File(desc="XML File defining BRAINSCut parameters. OLD NAME. PLEASE USE modelConfigurationFilename instead.", exists=True, argstr="--netConfiguration %s")
    modelConfigurationFilename = File(desc="XML File defining BRAINSCut parameters", exists=True, argstr="--modelConfigurationFilename %s")
    trainModelStartIndex = traits.Int(desc="Starting iteration for training", argstr="--trainModelStartIndex %d")
    verbose = traits.Int(desc="print out some debugging information", argstr="--verbose %d")
    multiStructureThreshold = traits.Bool(desc="multiStructureThreshold module to deal with overlaping area", argstr="--multiStructureThreshold ")
    histogramEqualization = traits.Bool(desc="A Histogram Equalization process could be added to the creating/applying process from Subject To Atlas. Default is false, which genreate input vectors without Histogram Equalization. ", argstr="--histogramEqualization ")
    computeSSEOn = traits.Bool(desc="compute Sum of Square Error (SSE) along the trained model until the number of iteration given in the modelConfigurationFilename file", argstr="--computeSSEOn ")
    generateProbability = traits.Bool(desc="Generate probability map", argstr="--generateProbability ")
    createVectors = traits.Bool(desc="create vectors for training neural net", argstr="--createVectors ")
    trainModel = traits.Bool(desc="train the neural net", argstr="--trainModel ")
    NoTrainingVectorShuffling = traits.Bool(desc="If this flag is on, there will be no shuffling.", argstr="--NoTrainingVectorShuffling ")
    applyModel = traits.Bool(desc="apply the neural net", argstr="--applyModel ")
    validate = traits.Bool(desc="validate data set.Just need for the first time run ( This is for validation of xml file and not working yet )", argstr="--validate ")
    method = traits.Enum("RandomForest", "ANN", argstr="--method %s")
    numberOfTrees = traits.Int(desc=" Random tree: number of trees. This is to be used when only one model with specified depth wish to be created. ", argstr="--numberOfTrees %d")
    randomTreeDepth = traits.Int(desc=" Random tree depth. This is to be used when only one model with specified depth wish to be created. ", argstr="--randomTreeDepth %d")
    modelFilename = traits.Str(desc=" model file name given from user (not by xml  configuration file) ", argstr="--modelFilename %s")


class BRAINSCutOutputSpec(TraitedSpec):
    pass


class BRAINSCut(SlicerCommandLine):
    """title: BRAINSCut (BRAINS)

category: Segmentation.Specialized

description: Automatic Segmentation using neural networks

version:  1.0

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: Vince Magnotta, Hans Johnson, Greg Harris, Kent Williams, Eunyoung Regina Kim

"""

    input_spec = BRAINSCutInputSpec
    output_spec = BRAINSCutOutputSpec
    _cmd = " BRAINSCut "
    _outputs_filenames = {}


class BRAINSROIAutoInputSpec(CommandLineInputSpec):
    inputVolume = File(desc="The input image for finding the largest region filled mask.", exists=True, argstr="--inputVolume %s")
    outputROIMaskVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="The ROI automatically found from the input image.", argstr="--outputROIMaskVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="The inputVolume with optional [maskOutput|cropOutput] to the region of the brain mask.", argstr="--outputVolume %s")
    maskOutput = traits.Bool(desc="The inputVolume multiplied by the ROI mask.", argstr="--maskOutput ")
    cropOutput = traits.Bool(desc="The inputVolume cropped to the region of the ROI mask.", argstr="--cropOutput ")
    otsuPercentileThreshold = traits.Float(desc="Parameter to the Otsu threshold algorithm.", argstr="--otsuPercentileThreshold %f")
    thresholdCorrectionFactor = traits.Float(desc="A factor to scale the Otsu algorithm's result threshold, in case clipping mangles the image.", argstr="--thresholdCorrectionFactor %f")
    closingSize = traits.Float(desc="The Closing Size (in millimeters) for largest connected filled mask.  This value is divided by image spacing and rounded to the next largest voxel number.", argstr="--closingSize %f")
    ROIAutoDilateSize = traits.Float(desc="This flag is only relavent when using ROIAUTO mode for initializing masks.  It defines the final dilation size to capture a bit of background outside the tissue region.  At setting of 10mm has been shown to help regularize a BSpline registration type so that there is some background constraints to match the edges of the head better.", argstr="--ROIAutoDilateSize %f")
    outputVolumePixelType = traits.Enum("float", "short", "ushort", "int", "uint", "uchar", desc="The output image Pixel Type is the scalar datatype for representation of the Output Volume.", argstr="--outputVolumePixelType %s")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSROIAutoOutputSpec(TraitedSpec):
    outputROIMaskVolume = File(desc="The ROI automatically found from the input image.", exists=True)
    outputVolume = File(desc="The inputVolume with optional [maskOutput|cropOutput] to the region of the brain mask.", exists=True)


class BRAINSROIAuto(SlicerCommandLine):
    """title: Foreground masking (BRAINS)

category: Segmentation.Specialized

description: This program is used to create a mask over the most prominant forground region in an image.  This is accomplished via a combination of otsu thresholding and a closing operation.  More documentation is available here: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/ForegroundMasking.


version: 2.4.1

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: Hans J. Johnson, hans-johnson -at- uiowa.edu, http://www.psychiatry.uiowa.edu

acknowledgements: Hans Johnson(1,3,4); Kent Williams(1); Gregory Harris(1), Vincent Magnotta(1,2,3);  Andriy Fedorov(5), fedorov -at- bwh.harvard.edu (Slicer integration); (1=University of Iowa Department of Psychiatry, 2=University of Iowa Department of Radiology, 3=University of Iowa Department of Biomedical Engineering, 4=University of Iowa Department of Electrical and Computer Engineering, 5=Surgical Planning Lab, Harvard)

"""

    input_spec = BRAINSROIAutoInputSpec
    output_spec = BRAINSROIAutoOutputSpec
    _cmd = " BRAINSROIAuto "
    _outputs_filenames = {'outputVolume':'outputVolume.nii','outputROIMaskVolume':'outputROIMaskVolume.nii'}


class BRAINSConstellationDetectorInputSpec(CommandLineInputSpec):
    houghEyeDetectorMode = traits.Int(desc=",                 This flag controls the mode of Hough eye detector.  By default, value of 1 is for T1W images, while the value of 0 is for T2W and PD images.,             ", argstr="--houghEyeDetectorMode %d")
    inputTemplateModel = File(desc="User-specified template model.,             ", exists=True, argstr="--inputTemplateModel %s")
    LLSModel = File(desc="Linear least squares model filename in HD5 format", exists=True, argstr="--LLSModel %s")
    inputVolume = File(desc="Input image in which to find ACPC points", exists=True, argstr="--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="ACPC-aligned output image with the same voxels, but updated origin, and direction cosign so that the AC point would fall at the physical location (0.0,0.0,0.0), and the mid-sagital plane is the plane where physical L/R coordinate is 0.0.", argstr="--outputVolume %s")
    outputResampledVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="ACPC-aligned output image in a resampled unifor space.  Currently this is a 1mm, 256^3, Identity direction image.", argstr="--outputResampledVolume %s")
    outputTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The filename for the original space to ACPC alignment to be written (in .h5 format).,             ", argstr="--outputTransform %s")
    outputLandmarksInInputSpace = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the original image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", argstr="--outputLandmarksInInputSpace %s")
    outputLandmarksInACPCAlignedSpace = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the output image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", argstr="--outputLandmarksInACPCAlignedSpace %s")
    outputLandmarkWeights = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the list of the landmarks and their correspond weight in (.wts) format.,             ", argstr="--outputLandmarkWeights %s")
    inputLandmarksPaired = File(desc=",               Paired use with outputLandmarks. It indicates the input landmark list filename (in a format of .fcsv) which contains the landmarks to be trainsformed to acpc-aligned space. The alignment transform will be calculated form the base landmarks provided, and then the rest of the landmarks are directly transformed to the acpc-aligned space rather than to estimate one by one.,             ", exists=True, argstr="--inputLandmarksPaired %s")
    outputLandmarksPaired = traits.Either(traits.Bool, File(), hash_files=False, desc=",               Paired use with inputLandmarks (in a format of .fcsv). It indicates the output acpc-aligned landmark list filename. The aligned landmarks are the landamrks that are defined in the file named inputLandmarks transformed by the acpc versor transform calculated by the constellation detector.,             ", argstr="--outputLandmarksPaired %s")
    outputMRML = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the new subject-specific scene definition file in the same format produced by Slicer3 (in .mrml format). Only the components that were specified by the user on command line would be generated. Compatible components include inputVolume, outputVolume, outputLandmarksInInputSpace, outputLandmarksInACPCAlignedSpace, and outputTransform.,             ", argstr="--outputMRML %s")
    outputVerificationScript = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the Slicer3 script that verifies the aligned landmarks against the aligned image file.  This will happen only in conjunction with saveOutputLandmarks and an outputVolume.,             ", argstr="--outputVerificationScript %s")
    mspQualityLevel = traits.Int(desc=",                 Flag cotrols how agressive the MSP is estimated. 0=quick estimate (9 seconds), 1=normal estimate (11 seconds), 2=great estimate (22 seconds), 3=best estimate (58 seconds), NOTE: -1= Prealigned so no estimate!.,             ", argstr="--mspQualityLevel %d")
    otsuPercentileThreshold = traits.Float(desc=",                 This is a parameter to FindLargestForegroundFilledMask, which is employed when acLowerBound is set and an outputUntransformedClippedVolume is requested.,             ", argstr="--otsuPercentileThreshold %f")
    acLowerBound = traits.Float(desc=",                 When generating a resampled output image, replace the image with the BackgroundFillValue everywhere below the plane This Far in physical units (millimeters) below (inferior to) the AC point (as found by the model.)  The oversize default was chosen to have no effect.  Based on visualizing a thousand masks in the IPIG study, we recommend a limit no smaller than 80.0 mm.,             ", argstr="--acLowerBound %f")
    cutOutHeadInOutputVolume = traits.Bool(desc=",                 Flag to cut out just the head tissue when producing an (un)transformed clipped volume.,             ", argstr="--cutOutHeadInOutputVolume ")
    outputUntransformedClippedVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output image in which to store neck-clipped input image, with the use of --acLowerBound and maybe --cutOutHeadInUntransformedVolume.", argstr="--outputUntransformedClippedVolume %s")
    rescaleIntensities = traits.Bool(desc=",                 Flag to turn on rescaling image intensities on input.,             ", argstr="--rescaleIntensities ")
    trimRescaledIntensities = traits.Float(desc=",                 Turn on clipping the rescaled image one-tailed on input.  Units of standard deviations above the mean.  Very large values are very permissive.  Non-positive value turns clipping off.  Defaults to removing 0.00001 of a normal tail above the mean.,             ", argstr="--trimRescaledIntensities %f")
    rescaleIntensitiesOutputRange = InputMultiPath(traits.Int, desc=",                 This pair of integers gives the lower and upper bounds on the signal portion of the output image.  Out-of-field voxels are taken from BackgroundFillValue.,             ", sep=",", argstr="--rescaleIntensitiesOutputRange %s")
    BackgroundFillValue = traits.Str(desc="Fill the background of image with specified short int value. Enter number or use BIGNEG for a large negative number.", argstr="--BackgroundFillValue %s")
    interpolationMode = traits.Enum("NearestNeighbor", "Linear", "ResampleInPlace", "BSpline", "WindowedSinc", "Hamming", "Cosine", "Welch", "Lanczos", "Blackman", desc="Type of interpolation to be used when applying transform to moving volume.  Options are Linear, ResampleInPlace, NearestNeighbor, BSpline, or WindowedSinc", argstr="--interpolationMode %s")
    forceACPoint = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the AC point from the original image on the command line.,             ", sep=",", argstr="--forceACPoint %s")
    forcePCPoint = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the PC point from the original image on the command line.,             ", sep=",", argstr="--forcePCPoint %s")
    forceVN4Point = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the VN4 point from the original image on the command line.,             ", sep=",", argstr="--forceVN4Point %s")
    forceRPPoint = InputMultiPath(traits.Float, desc=",                 Use this flag to manually specify the RP point from the original image on the command line.,             ", sep=",", argstr="--forceRPPoint %s")
    inputLandmarksEMSP = File(desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (in .fcsv) with the landmarks in the estimated MSP aligned space to be loaded. The detector will only process landmarks not enlisted on the file.,             ", exists=True, argstr="--inputLandmarksEMSP %s")
    forceHoughEyeDetectorReportFailure = traits.Bool(desc=",                 Flag indicates whether the Hough eye detector should report failure,             ", argstr="--forceHoughEyeDetectorReportFailure ")
    rmpj = traits.Float(desc=",               Search radius for MPJ in unit of mm,             ", argstr="--rmpj %f")
    rac = traits.Float(desc=",               Search radius for AC in unit of mm,             ", argstr="--rac %f")
    rpc = traits.Float(desc=",               Search radius for PC in unit of mm,             ", argstr="--rpc %f")
    rVN4 = traits.Float(desc=",               Search radius for VN4 in unit of mm,             ", argstr="--rVN4 %f")
    debug = traits.Bool(desc=",               Show internal debugging information.,             ", argstr="--debug ")
    verbose = traits.Bool(desc=",               Show more verbose output,             ", argstr="--verbose ")
    writeBranded2DImage = traits.Either(traits.Bool, File(), hash_files=False, desc=",               The filename for the 2D .png branded midline debugging image.  This will happen only in conjunction with requesting an outputVolume.,             ", argstr="--writeBranded2DImage %s")
    resultsDir = traits.Either(traits.Bool, Directory(), hash_files=False, desc=",               The directory for the debuging images to be written.,             ", argstr="--resultsDir %s")
    writedebuggingImagesLevel = traits.Int(desc=",                 This flag controls if debugging images are produced.  By default value of 0 is no images.  Anything greater than zero will be increasing level of debugging images.,             ", argstr="--writedebuggingImagesLevel %d")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSConstellationDetectorOutputSpec(TraitedSpec):
    outputVolume = File(desc="ACPC-aligned output image with the same voxels, but updated origin, and direction cosign so that the AC point would fall at the physical location (0.0,0.0,0.0), and the mid-sagital plane is the plane where physical L/R coordinate is 0.0.", exists=True)
    outputResampledVolume = File(desc="ACPC-aligned output image in a resampled unifor space.  Currently this is a 1mm, 256^3, Identity direction image.", exists=True)
    outputTransform = File(desc="The filename for the original space to ACPC alignment to be written (in .h5 format).,             ", exists=True)
    outputLandmarksInInputSpace = File(desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the original image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", exists=True)
    outputLandmarksInACPCAlignedSpace = File(desc=",               The filename for the new subject-specific landmark definition file in the same format produced by Slicer3 (.fcsv) with the landmarks in the output image space (the detected RP, AC, PC, and VN4) in it to be written.,             ", exists=True)
    outputLandmarkWeights = File(desc=",               The filename for the list of the landmarks and their correspond weight in (.wts) format.,             ", exists=True)
    outputLandmarksPaired = File(desc=",               Paired use with inputLandmarks (in a format of .fcsv). It indicates the output acpc-aligned landmark list filename. The aligned landmarks are the landamrks that are defined in the file named inputLandmarks transformed by the acpc versor transform calculated by the constellation detector.,             ", exists=True)
    outputMRML = File(desc=",               The filename for the new subject-specific scene definition file in the same format produced by Slicer3 (in .mrml format). Only the components that were specified by the user on command line would be generated. Compatible components include inputVolume, outputVolume, outputLandmarksInInputSpace, outputLandmarksInACPCAlignedSpace, and outputTransform.,             ", exists=True)
    outputVerificationScript = File(desc=",               The filename for the Slicer3 script that verifies the aligned landmarks against the aligned image file.  This will happen only in conjunction with saveOutputLandmarks and an outputVolume.,             ", exists=True)
    outputUntransformedClippedVolume = File(desc="Output image in which to store neck-clipped input image, with the use of --acLowerBound and maybe --cutOutHeadInUntransformedVolume.", exists=True)
    writeBranded2DImage = File(desc=",               The filename for the 2D .png branded midline debugging image.  This will happen only in conjunction with requesting an outputVolume.,             ", exists=True)
    resultsDir = Directory(desc=",               The directory for the debuging images to be written.,             ", exists=True)


class BRAINSConstellationDetector(SlicerCommandLine):
    """title: Brain Landmark Constellation Detector (BRAINS)

category: Segmentation.Specialized

description:
    This program will find the mid-sagittal plane, a constellation of landmarks in a volume, and create an AC/PC aligned data set with the AC point at the center of the voxel lattice (labeled at the origin of the image physical space.)  Part of this work is an extention of the algorithms originally described by Dr. Babak A. Ardekani, Alvin H. Bachman, Model-based automatic detection of the anterior and posterior commissures on MRI scans, NeuroImage, Volume 46, Issue 3, 1 July 2009, Pages 677-682, ISSN 1053-8119, DOI: 10.1016/j.neuroimage.2009.02.030.  (http://www.sciencedirect.com/science/article/B6WNP-4VRP25C-4/2/8207b962a38aa83c822c6379bc43fe4c)


version: 1.0

documentation-url: http://www.nitrc.org/projects/brainscdetector/

"""

    input_spec = BRAINSConstellationDetectorInputSpec
    output_spec = BRAINSConstellationDetectorOutputSpec
    _cmd = " BRAINSConstellationDetector "
    _outputs_filenames = {'outputVolume':'outputVolume.nii.gz','outputResampledVolume':'outputResampledVolume.nii.gz','outputMRML':'outputMRML.mrml','outputLandmarksPaired':'outputLandmarksPaired.fcsv','resultsDir':'resultsDir','outputTransform':'outputTransform.h5','writeBranded2DImage':'writeBranded2DImage.png','outputLandmarksInACPCAlignedSpace':'outputLandmarksInACPCAlignedSpace.fcsv','outputLandmarksInInputSpace':'outputLandmarksInInputSpace.fcsv','outputLandmarkWeights':'outputLandmarkWeights.wts','outputUntransformedClippedVolume':'outputUntransformedClippedVolume.nii.gz','outputVerificationScript':'outputVerificationScript.sh'}


class BinaryMaskEditorBasedOnLandmarksInputSpec(CommandLineInputSpec):
    inputBinaryVolume = File(desc="Input binary image in which to be edited", exists=True, argstr="--inputBinaryVolume %s")
    outputBinaryVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output binary image in which to be edited", argstr="--outputBinaryVolume %s")
    inputLandmarksFilename = File(desc=" The filename for the  landmark definition file in the same format produced by Slicer3 (.fcsv). ", exists=True, argstr="--inputLandmarksFilename %s")
    inputLandmarkNames = InputMultiPath(traits.Str, desc=" A target input landmark name to be edited. This should be listed in the inputLandmakrFilename Given. ", sep=",", argstr="--inputLandmarkNames %s")
    setCutDirectionForLandmark = InputMultiPath(traits.Str, desc="Setting the cutting out direction of the input binary image to the one of anterior, posterior, left, right, superior or posterior. (ENUMERATION: ANTERIOR, POSTERIOR, LEFT, RIGHT, SUPERIOR, POSTERIOR) ", sep=",", argstr="--setCutDirectionForLandmark %s")
    setCutDirectionForObliquePlane = InputMultiPath(traits.Str, desc="If this is true, the mask will be thresholded out to the direction of inferior, posterior,  and/or left. Default behavrior is that cutting out to the direction of superior, anterior and/or right. ", sep=",", argstr="--setCutDirectionForObliquePlane %s")
    inputLandmarkNamesForObliquePlane = InputMultiPath(traits.Str, desc=" Three subset landmark names of inputLandmarksFilename for a oblique plane computation. The plane computed for binary volume editing. ", sep=",", argstr="--inputLandmarkNamesForObliquePlane %s")


class BinaryMaskEditorBasedOnLandmarksOutputSpec(TraitedSpec):
    outputBinaryVolume = File(desc="Output binary image in which to be edited", exists=True)


class BinaryMaskEditorBasedOnLandmarks(SlicerCommandLine):
    """title: BRAINS Binary Mask Editor Based On Landmarks(BRAINS)

category: Segmentation.Specialized

description:


version: 1.0

documentation-url: http://www.nitrc.org/projects/brainscdetector/

"""

    input_spec = BinaryMaskEditorBasedOnLandmarksInputSpec
    output_spec = BinaryMaskEditorBasedOnLandmarksOutputSpec
    _cmd = " BinaryMaskEditorBasedOnLandmarks "
    _outputs_filenames = {'outputBinaryVolume':'outputBinaryVolume.nii'}


class BRAINSABCInputSpec(CommandLineInputSpec):
    inputVolumes = InputMultiPath(File(exists=True), desc="The list of input image files to be segmented.", argstr="--inputVolumes %s...")
    atlasDefinition = File(desc="Contains all parameters for Atlas", exists=True, argstr="--atlasDefinition %s")
    inputVolumeTypes = InputMultiPath(traits.Str, desc="The list of input image types corresponding to the inputVolumes.", sep=",", argstr="--inputVolumeTypes %s")
    outputDir = traits.Either(traits.Bool, Directory(), hash_files=False, desc="Ouput directory", argstr="--outputDir %s")
    atlasToSubjectTransformType = traits.Enum("ID", "Rigid", "Affine", "BSpline", "SyN", desc=" What type of linear transform type do you want to use to register the atlas to the reference subject image.", argstr="--atlasToSubjectTransformType %s")
    atlasToSubjectTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The transform from atlas to the subject", argstr="--atlasToSubjectTransform %s")
    atlasToSubjectInitialTransform = traits.Either(traits.Bool, File(), hash_files=False, desc="The initial transform from atlas to the subject", argstr="--atlasToSubjectInitialTransform %s")
    subjectIntermodeTransformType = traits.Enum("ID", "Rigid", "Affine", "BSpline", desc=" What type of linear transform type do you want to use to register the atlas to the reference subject image.", argstr="--subjectIntermodeTransformType %s")
    outputVolumes = traits.Either(traits.Bool, InputMultiPath(File(), ), hash_files=False, desc="Corrected Output Images: should specify the same number of images as inputVolume, if only one element is given, then it is used as a file pattern where %s is replaced by the imageVolumeType, and %d by the index list location.", argstr="--outputVolumes %s...")
    outputLabels = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Label Image", argstr="--outputLabels %s")
    outputDirtyLabels = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Dirty Label Image", argstr="--outputDirtyLabels %s")
    posteriorTemplate = traits.Str(desc="filename template for Posterior output files", argstr="--posteriorTemplate %s")
    outputFormat = traits.Enum("NIFTI", "Meta", "Nrrd", desc="Output format", argstr="--outputFormat %s")
    interpolationMode = traits.Enum("BSpline", "NearestNeighbor", "WindowedSinc", "Linear", "ResampleInPlace", "Hamming", "Cosine", "Welch", "Lanczos", "Blackman", desc="Type of interpolation to be used when applying transform to moving volume.  Options are Linear, NearestNeighbor, BSpline, WindowedSinc, or ResampleInPlace.  The ResampleInPlace option will create an image with the same discrete voxel values and will adjust the origin and direction of the physical space interpretation.", argstr="--interpolationMode %s")
    maxIterations = traits.Int(desc="Filter iterations", argstr="--maxIterations %d")
    medianFilterSize = InputMultiPath(traits.Int, desc="The radius for the optional MedianImageFilter preprocessing in all 3 directions.", sep=",", argstr="--medianFilterSize %s")
    filterIteration = traits.Int(desc="Filter iterations", argstr="--filterIteration %d")
    filterTimeStep = traits.Float(desc="Filter time step should be less than (PixelSpacing/(1^(DIM+1)), value is set to negative, then allow automatic setting of this value. ", argstr="--filterTimeStep %f")
    filterMethod = traits.Enum("None", "CurvatureFlow", "GradientAnisotropicDiffusion", "Median", desc="Filter method for preprocessing of registration", argstr="--filterMethod %s")
    maxBiasDegree = traits.Int(desc="Maximum bias degree", argstr="--maxBiasDegree %d")
    atlasWarpingOff = traits.Bool(desc="Deformable registration of atlas to subject", argstr="--atlasWarpingOff ")
    gridSize = InputMultiPath(traits.Int, desc="Grid size for atlas warping with BSplines", sep=",", argstr="--gridSize %s")
    defaultSuffix = traits.Str(argstr="--defaultSuffix %s")
    implicitOutputs = traits.Either(traits.Bool, InputMultiPath(File(), ), hash_files=False, desc="Outputs to be made available to NiPype. Needed because not all BRAINSABC outputs have command line arguments.", argstr="--implicitOutputs %s...")
    debuglevel = traits.Int(desc="Display debug messages, and produce debug intermediate results.  0=OFF, 1=Minimal, 10=Maximum debugging.", argstr="--debuglevel %d")
    writeLess = traits.Bool(desc="Does not write posteriors and filtered, bias corrected images", argstr="--writeLess ")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class BRAINSABCOutputSpec(TraitedSpec):
    outputDir = Directory(desc="Output directory", exists=True)
    atlasToSubjectTransform = File(desc="The transform from atlas to the subject", exists=True)
    atlasToSubjectInitialTransform = File(desc="The initial transform from atlas to the subject", exists=True)
    outputVolumes = OutputMultiPath(File(exists=True), desc="Corrected Output Images: should specify the same number of images as inputVolume, if only one element is given, then it is used as a file pattern where %s is replaced by the imageVolumeType, and %d by the index list location.", exists=True)
    outputLabels = File(desc="Output Label Image", exists=True)
    outputDirtyLabels = File(desc="Output Dirty Label Image", exists=True)
    implicitOutputs = OutputMultiPath(File(exists=True), desc="Outputs to be made available to NiPype. Needed because not all BRAINSABC outputs have command line arguments.", exists=True)


class BRAINSABC(SlicerCommandLine):
    """title: Intra-subject registration, bias Correction, and tissue classification (BRAINS)

category: Segmentation.Specialized

description: Atlas-based tissue segmentation method.  This is an algorithmic extension of work done by XXXX at UNC and Utah XXXX need more description here.


"""

    input_spec = BRAINSABCInputSpec
    output_spec = BRAINSABCOutputSpec
    _cmd = " BRAINSABC "
    _outputs_filenames = {'outputLabels':'outputLabels.nii.gz','atlasToSubjectTransform':'atlasToSubjectTransform.h5','atlasToSubjectInitialTransform':'atlasToSubjectInitialTransform.h5','outputDirtyLabels':'outputDirtyLabels.nii.gz','outputVolumes':'outputVolumes.nii.gz','outputDir':'outputDir','implicitOutputs':'implicitOutputs.nii.gz'}


class ESLRInputSpec(CommandLineInputSpec):
    inputVolume = File(desc="Input Label Volume", exists=True, argstr="--inputVolume %s")
    outputVolume = traits.Either(traits.Bool, File(), hash_files=False, desc="Output Label Volume", argstr="--outputVolume %s")
    low = traits.Int(desc="The lower bound of the labels to be used.", argstr="--low %d")
    high = traits.Int(desc="The higher bound of the labels to be used.", argstr="--high %d")
    closingSize = traits.Int(desc="The closing size for hole filling.", argstr="--closingSize %d")
    openingSize = traits.Int(desc="The opening size for hole filling.", argstr="--openingSize %d")
    safetySize = traits.Int(desc="The safetySize size for the clipping region.", argstr="--safetySize %d")
    preserveOutside = traits.Bool(desc="For values outside the specified range, preserve those values.", argstr="--preserveOutside ")
    numberOfThreads = traits.Int(desc="Explicitly specify the maximum number of threads to use.", argstr="--numberOfThreads %d")


class ESLROutputSpec(TraitedSpec):
    outputVolume = File(desc="Output Label Volume", exists=True)


class ESLR(SlicerCommandLine):
    """title: Clean Contiguous Label Map (BRAINS)

category: Segmentation.Specialized

description: From a range of label map values, extract the largest contiguous region of those labels

"""

    input_spec = ESLRInputSpec
    output_spec = ESLROutputSpec
    _cmd = " ESLR "
    _outputs_filenames = {'outputVolume':'outputVolume.nii.gz'}

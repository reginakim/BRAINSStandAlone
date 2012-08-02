#################################################################################
## Program:   Build Template Parallel
## Language:  Python
##
## Authors:  Jessica Forbes and Grace Murray, University of Iowa
##
##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.
##
#################################################################################

import argparse
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import antsAverageImages
import antsAverageAffineTransform
import antsMultiplyImages
import antsRegistration
import antsWarp
import antsMultiplyImages
from nipype.interfaces.io import DataGrabber

def antsRegistrationTemplateBuildSingleIterationWF(iterationPhasePrefix):

    antsTemplateBuildSingleIterationWF = pe.Workflow(name = 'antsRegistrationTemplateBuildSingleIterationWF')

    inputSpec = pe.Node(interface=util.IdentityInterface(fields=['images', 'fixed_image']), name='InputSpec')
    outputSpec = pe.Node(interface=util.IdentityInterface(fields=['template']), name='OutputSpec')

    ### NOTE MAP NODE! warp each of the original images to the provided fixed_image as the template
    BeginANTS=pe.MapNode(interface=antsRegistration.antsRegistration(), name = 'BeginANTS', iterfield=['moving_image'])
    BeginANTS.inputs.dimension = 3
    BeginANTS.inputs.output_transform_prefix = 'AffineInitialRegistration'
    BeginANTS.inputs.metric = 'CC'
    BeginANTS.inputs.metric_weight = 1
    BeginANTS.inputs.radius = 5
    BeginANTS.inputs.transform = ["Affine[1]","SyN[0.25,3.0,0.0]"]
    BeginANTS.inputs.number_of_iterations = [[10, 10, 10], [50, 35, 15]]
    BeginANTS.inputs.use_histogram_matching = True
    BeginANTS.inputs.shrink_factors = [[3,2,1],[3,2,1]]
    BeginANTS.inputs.smoothing_sigmas = [[0,0,0],[0,0,0]]
    #BeginANTS.inputs.mi_option = [32, 16000]
    #BeginANTS.inputs.regularization = 'Gauss'
    #BeginANTS.inputs.regularization_gradient_field_sigma = 3
    #BeginANTS.inputs.regularization_deformation_field_sigma = 0
    #BeginANTS.inputs.number_of_affine_iterations = [10000,10000,10000,10000,10000]
    antsTemplateBuildSingleIterationWF.connect(inputSpec, 'images', BeginANTS, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(inputSpec, 'fixed_image', BeginANTS, 'fixed_image')

    ## Utility Function
    ## This will make a list of list pairs for defining the concatenation of transforms
    ## wp=['wp1.nii','wp2.nii','wp3.nii']
    ## af=['af1.mat','af2.mat','af3.mat']
    ## ll=map(list,zip(af,wp))
    ## ll
    ##[['af1.mat', 'wp1.nii'], ['af2.mat', 'wp2.nii'], ['af3.mat', 'wp3.nii']]
    def MakeListsOfTransformLists(warpTransformList, AffineTransformList):
        return map(list, zip(warpTransformList,AffineTransformList))
    MakeTransformsLists = pe.Node(interface=util.Function(function=MakeListsOfTransformLists,input_names=['warpTransformList', 'AffineTransformList'], output_names=['out']), 
                    run_without_submitting=True,
                    name='MakeTransformsLists')
    MakeTransformsLists.inputs.function_str = functionString1
    MakeTransformsLists.inputs.ignore_exception = True
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'warp_transform', MakeTransformsLists, 'warpTransformList')
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'affine_transform', MakeTransformsLists, 'AffineTransformList')

    ## Now warp all the images
    wimtdeformed = pe.MapNode(interface = antsWarp.WarpImageMultiTransform(), name ='wimtdeformed', iterfield=['transformation_series', 'moving_image'])
    antsTemplateBuildSingleIterationWF.connect(inputSpec, 'images', wimtdeformed, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(MakeTransformsLists, 'out', wimtdeformed, 'transformation_series')

    ## Now average all affine transforms together
    AvgAffineTransform = pe.Node(interface=antsAverageAffineTransform.AntsAverageAffineTransform(), name = 'AvgAffineTransform')
    AvgAffineTransform.inputs.dimension = 3
    AvgAffineTransform.inputs.output_affine_transform = iterationPhasePrefix+'Affine.mat'
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'affine_transform', AvgAffineTransform, 'transforms')

    ## Now average the warp fields togther
    AvgWarpImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgWarpImages')
    AvgWarpImages.inputs.dimension = 3
    AvgWarpImages.inputs.output_average_image = iterationPhasePrefix+'warp.nii.gz'
    AvgWarpImages.inputs.normalize = 1
    antsTemplateBuildSingleIterationWF.connect(BeginANTS, 'warp_transform', AvgWarpImages, 'images')

    ## Now average the images together
    MultiplyWarpImage=pe.Node(interface=antsMultiplyImages.AntsMultiplyImages(), name='MultiplyWarpImage')
    MultiplyWarpImage.inputs.dimension = 3
    MultiplyWarpImage.inputs.second_input = -0.25
    MultiplyWarpImage.inputs.output_product_image = iterationPhasePrefix+'warp.nii.gz'
    antsTemplateBuildSingleIterationWF.connect(AvgWarpImages, 'average_image', MultiplyWarpImage, 'first_input')

    ## Now 
    AvgDeformedImages=pe.Node(interface=antsAverageImages.AntsAverageImages(), name='AvgDeformedImages')
    AvgDeformedImages.inputs.dimension = 3
    AvgDeformedImages.inputs.output_average_image = iterationPhasePrefix+'.nii.gz'
    AvgDeformedImages.inputs.normalize = 1
    antsTemplateBuildSingleIterationWF.connect(wimtdeformed, "output_image", AvgDeformedImages, 'images')

    Warptemplates = pe.Node(interface = antsWarp.WarpImageMultiTransform(), name = 'Warptemplates')
    Warptemplates.inputs.invert_affine = [1]
    antsTemplateBuildSingleIterationWF.connect(AvgDeformedImages, 'average_image', Warptemplates, 'reference_image')
    antsTemplateBuildSingleIterationWF.connect(MultiplyWarpImage, 'product_image', Warptemplates, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(AvgAffineTransform, 'affine_transform', Warptemplates, 'transformation_series')

    WarpAll = pe.Node(interface = antsWarp.WarpImageMultiTransform(), name = 'WarpAll')
    WarpAll.inputs.invert_affine = [1]
    antsTemplateBuildSingleIterationWF.connect(AvgDeformedImages, 'average_image', WarpAll, 'moving_image')
    antsTemplateBuildSingleIterationWF.connect(AvgDeformedImages, 'average_image', WarpAll, 'reference_image')

    functionString2 = 'def func(arg1, arg2, arg3, arg4, arg5): return [arg1, arg2, arg3, arg4, arg5]'
    fi = pe.Node(interface=util.Function(input_names=['arg1', 'arg2', 'arg3', 'arg4', 'arg5'], output_names=['out']), name='ListAppender2')
    fi.inputs.function_str = functionString2
    fi.inputs.ignore_exception = True



    antsTemplateBuildSingleIterationWF.connect(AvgAffineTransform, 'affine_transform', fi, 'arg1')
    antsTemplateBuildSingleIterationWF.connect(Warptemplates, 'output_image', fi, 'arg2')
    antsTemplateBuildSingleIterationWF.connect(Warptemplates, 'output_image', fi, 'arg3')
    antsTemplateBuildSingleIterationWF.connect(Warptemplates, 'output_image', fi, 'arg4')
    antsTemplateBuildSingleIterationWF.connect(Warptemplates, 'output_image', fi, 'arg5')

    antsTemplateBuildSingleIterationWF.connect(fi, 'out', WarpAll, 'transformation_series')


    antsTemplateBuildSingleIterationWF.connect(WarpAll, 'output_image', outputSpec, 'template')

    return antsTemplateBuildSingleIterationWF

inputDir=(`pwd`)
echo "siteID, subjectID, sessionID, imageList, roiList, deformationList"
while read site subject session
do
    roiDict=""
    for roi in accumben caudate putamen globus thalamus hippocampus
    do
        for side in l r
        do
            filename=(`ls $inputDir/Manuals/BRAINSCutMultiNetMask/${session}_${side}_$roi.nii.gz`)
            if [ "$roiDict" == "" ]; then
                roiDict="'${side}_$roi':'$filename'"
            else
              roiDict="$roiDict,'${side}_$roi':'$filename'"
            fi
        done
    done
    roiDict="{$roiDict}"

    ################################################################################
    
    imageDict=""
    for type in t1 t2
    do
        filename=(`ls $inputDir/$session/TissueClassify/BABC/${type}_average_BRAINSABC.nii.gz`)
        if [ "$imageDict" == "" ]; then
            imageDict="'$type':'$filename'"
        else
            imageDict="$imageDict, '$type':'$filename'"
        fi
    done
    imageDict="{$imageDict}"

    ################################################################################

    atlasToSubject=(`ls  $inputDir/Deformations/AtlasToSubject/AtlasToSubject_${session}.mat`)
    subjectToAtlas=(`ls  $inputDir/Deformations/SubjectToAtlas/SubToAtlas_${session}.mat`)
    deformationDict="{'atlasToSubject':'$atlasToSubject','subjectToAtlas':'$subjectToAtlas'}"
    echo $site, $subject, $session, \"$imageDict\", \"$roiDict\", \"$deformationDict\"
done < scans.list

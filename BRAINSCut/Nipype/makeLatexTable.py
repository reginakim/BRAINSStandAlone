##{
def insertFigureBlock( figureList, label, document ):
    """ make latex figure block with given input"""

    """
    begin figure block 
    """
    figureHeader="""
\\begin{figure}
    \centering"""
    document.write( figureHeader )

    """
    insert figure
    """
    for figure in figureList:
        figureStr = """
    \\begin{subfigure}[b]{0.6\\textwidth} 
					\includegraphics[width=\\textwidth=0.6]{""" + figure + """}
    \end{subfigure}
        """
        document.write( figureStr )
    
    """
    end figure block
    """
    figureFooter="""
    \caption{""" + label + """ }
\end{figure}
    """
    document.write( figureFooter )

##}

##{
def insertTabelBlock( inputFileList, label, document, doLandScape=True ):
    """ make latex figure block with given input"""
    if doLandScape:
        document.write( """\\begin{landscape}""")
    for inputFile in inputFileList:
        document.write("""
    \\input{""" + inputFile + """ }""")
    if doLandScape:
       document.write("""\end{landscape}""")

    
##}

##{
def insertDocumentHeader( document, title ):
    header="""
\documentclass{scrartcl}
\usepackage{graphicx}
\usepackage{lscape}
\usepackage{caption}
\usepackage{subcaption}


\\begin{document}

\\title{Experiment Report by \LaTeX{}}
\\author{Eun Young (Regina) Kim}
\\subtitle{("""+title + """)}

\maketitle
\pagebreak
    """
    document.write( header )
    return document
##}

##{
def insertDocumentFooter( document ):
    footer=""" 
\end{document}
    """
    document.write( footer )
    document.close()
##}

##{
def getROIFileListWithExtension( inputPath, searchKeyWord, extension ):
    import re
    import os
    import glob

    if os.path.exists( inputPath ):
        fileList = glob.glob( inputPath + "/*" + searchKeyWord + "*" + extension )
    else:
        print( """Invalid path! ::
               {path}""".format( path=inputPath ))
        exit
    
    return fileList
##}
##{
def generateICC( inputPath, outputTexFilename ):
    """ make latex documentation 
        to display table and figures
    """
    outputLatexFile = open( outputTexFilename, 'w' )
    
    import makeLatexTable as this
    import re
    this.insertDocumentHeader( outputLatexFile, re.sub( "_", " ", inputPath ) )
    #{

    import makeLatexTable as this
    roiList=['l_accumben', 'l_caudate', 'l_globus', 'l_thalamus', 'l_hippocampus', 'l_putamen',
             'r_accumben', 'r_caudate', 'r_globus', 'r_thalamus', 'r_hippocampus', 'r_putamen']

    import glob
    methodDirList = glob.glob( inputPath + "/outputDataCollector/_doRawComparison_*" )

    import os

    if methodDirList:
        for methodDir in methodDirList:
            print( """ directory search in ::
                   {str}
                   ==========================
                   """.format(str=methodDir))
            sessionTitle = re.sub( "_", " ", os.path.basename( methodDir ) )
            sessionTitle = re.sub( "doRawComparison", "doRawComparison= ", sessionTitle )
            sessionTitle = re.sub( "methodParameter", "", sessionTitle )
            sessionTitle = re.sub( " TreeDepth", ", Tree Depth= ", sessionTitle )
            sessionTitle = re.sub( " TreeNumber", ", Tree No= ", sessionTitle )
            sessionTitle = re.sub( "normalization", ", Normalization= ", sessionTitle )
            sessionTitle = re.sub( " ,", ",", sessionTitle )

            #outputLatexFile.write("\section{ " + sessionTitle + "} " )
            for roi in roiList:
                roiStr = re.sub( "l_", "ROI= left ", roi )
                roiStr = re.sub( "r_", "ROI= right ", roiStr )
                currentLabel = sessionTitle + ", " + roiStr 
                #outputLatexFile.write("\subsection{ " + currentLabel + "} " )
                for ext in ['pdf','tex']:
                    collectiveList = []
                    for keyWord in [ '*icc' ]:
                        currentFilenames = this.getROIFileListWithExtension( methodDir +"/summaryND/", roi + keyWord , ext )
                        if currentFilenames:
                            print( roi + ", " + keyWord + ", " + ext ) 
                            print(currentFilenames)
                            for filename in currentFilenames:
                                collectiveList.append( filename )
                    if collectiveList:
                        if ext == 'pdf':
                            insertFigureBlock( collectiveList, currentLabel, outputLatexFile)
                        elif ext == 'tex':
                            insertTabelBlock( collectiveList, currentLabel, outputLatexFile, False)
                outputLatexFile.write( "\clearpage" )

    #}
    this.insertDocumentFooter( outputLatexFile )
    return os.path.abspath( outputTexFilename )
##}
##{
def generateLatexDocument( inputPath, outputTexFilename ):
    """ make latex documentation 
        to display table and figures
    """
    outputLatexFile = open( outputTexFilename, 'w' )
    
    import makeLatexTable as this
    import re
    this.insertDocumentHeader( outputLatexFile, re.sub( "_", " ", inputPath ) )
    #{

    import makeLatexTable as this
    roiList=['l_accumben', 'l_caudate', 'l_globus', 'l_thalamus', 'l_hippocampus', 'l_putamen',
             'r_accumben', 'r_caudate', 'r_globus', 'r_thalamus', 'r_hippocampus', 'r_putamen']

    import glob
    methodDirList = glob.glob( inputPath + "/outputDataCollector/_doRawComparison_*" )

    import os

    if methodDirList:
        for methodDir in methodDirList:
            print( """ directory search in ::
                   {str}
                   ==========================
                   """.format(str=methodDir))
            sessionTitle = re.sub( "_", " ", os.path.basename( methodDir ) )
            sessionTitle = re.sub( "doRawComparison", "doRawComparison= ", sessionTitle )
            sessionTitle = re.sub( "methodParameter", "", sessionTitle )
            sessionTitle = re.sub( " TreeDepth", ", Tree Depth= ", sessionTitle )
            sessionTitle = re.sub( " TreeNumber", ", Tree No= ", sessionTitle )
            sessionTitle = re.sub( "normalization", ", Normalization= ", sessionTitle )
            sessionTitle = re.sub( " ,", ",", sessionTitle )

            #outputLatexFile.write("\section{ " + sessionTitle + "} " )
            for roi in roiList:
                roiStr = re.sub( "l_", "ROI= left ", roi )
                roiStr = re.sub( "r_", "ROI= right ", roiStr )
                currentLabel = sessionTitle + ", " + roiStr 
                #outputLatexFile.write("\subsection{ " + currentLabel + "} " )
                for ext in ['pdf','tex']:
                    collectiveList = []
                    for keyWord in [ '*summary', '*icc' ]:
                        currentFilenames = this.getROIFileListWithExtension( methodDir +"/summaryND/", roi + keyWord , ext )
                        if currentFilenames:
                            print( roi + ", " + keyWord + ", " + ext ) 
                            print(currentFilenames)
                            for filename in currentFilenames:
                                collectiveList.append( filename )
                    if collectiveList:
                        if ext == 'pdf':
                            insertFigureBlock( collectiveList, currentLabel, outputLatexFile)
                        elif ext == 'tex':
                            insertTabelBlock( collectiveList, currentLabel, outputLatexFile)
    #}
    this.insertDocumentFooter( outputLatexFile )
    return os.path.abspath( outputTexFilename )
##}

##{
def main(argv=None):
    import os
    import sys
    
    from nipype import config
    config.enable_debug_mode()
    
    #-------------------------------- argument parser
    import argparse
    argParser = argparse.ArgumentParser( description ="""****************************
        This is making report from a input directory 
        by discovering figures (*pdf) and tables (*tex)
        pre-created.
        Highly depend on the directory hierarchy of analysis.py
        """)
    argParser.add_argument( '--inputDir',    help="""inputDir
        """, 
        dest='inputDir', required=False, default="." )
    argParser.add_argument( '--outputTexFilename',    help="""outputTexFilename
        """, 
        dest='outputTexFilename', required=False, default="test.tex" )

    args =argParser.parse_args()

    outputTexFilename= generateLatexDocument( args.inputDir,
                                              args.outputTexFilename )
    import subprocess
    return_value = subprocess.call(['pdflatex', outputTexFilename], shell=False)

    iccOutputTexFilename= generateICC( args.inputDir,
                                       args.outputTexFilename+ "ICC.tex" )

    return_value = subprocess.call(['pdflatex', iccOutputTexFilename], shell=False)

    print(""" return value from subprocess call:::
          {str}""".format( str=return_value ))

    import glob
    for rmfile in glob.glob( "./*aux" ):
        os.remove( rmfile )
    for rmfile in glob.glob( "./*log" ):
        os.remove( rmfile )

##}

##{
import sys

if __name__ == "__main__":
    sys.exit(main())
##}


##{
"""
unit test
"""

#generateLatexDocument( '/hjohnson/HDNI/PREDICT_TRAINING/regina_ann/TrainingModels/BAW2012Dec/Experiments/Normalization_Test/accumben/', './test.tex' )

"""
summaryOutput_l_accumben_icc.pdf
summaryOutput_l_accumben_summary.csv
summaryOutput_l_accumben_summary.tex
summaryOutput_r_accumben_icc.pdf
summaryOutput_r_accumben_summary.csv
summaryOutput_r_accumben_summary.tex
summaryOutput_l_accumben_icc.csv
summaryOutput_l_accumben_icc.tex
summaryOutput_l_accumben_summary.pdf
summaryOutput_r_accumben_icc.csv
summaryOutput_r_accumben_icc.tex
summaryOutput_r_accumben_summary.pdf
"""
##}

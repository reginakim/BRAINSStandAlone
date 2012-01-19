plotOOB <- function( filename, titleTxt)
{
## read data
  dt<-read.csv( filename, header=T);

## color scheme
  numDepth = levels(factor( dt$depth)) ;
  myColors=topo.colors( length( numDepth) );

## range
  error.range <- max(dt$error) - min( dt$error ) ;
  error.min   <- min(dt$error ) - error.range * 0.05;
  error.max   <- max(dt$error ) + error.range * 0.05;

  NTree.range <- max(dt$NTree) - min( dt$NTree ) ;
  NTree.min   <- min(dt$NTree ) - NTree.range * 0.05;
  NTree.max   <- max(dt$NTree ) + NTree.range * 0.1;

## start counting
  currDepth <- 1;

## extract first group and plot
  pdf( paste(titleTxt,".pdf",sep=""));##, width=500, height=800 );
  subDt <- subset( dt, dt$depth==currDepth );
  plot( subDt$NTree, subDt$error,
        type="l", 
        xlim=c(NTree.min,NTree.max),
        ylim=c(error.min,error.max),
        xlab="number of trees",
        ylab="out of back training error",
        col=myColors[ currDepth ]);

  title( titleTxt );
## add plots
  for( currDepth in 2:length(numDepth) )
    {
    subDt <- subset( dt, dt$depth==currDepth );
    points( subDt$NTree, subDt$error,
            type="l", 
            col=myColors[ currDepth ]);

    }

  legend( "topright", 
          paste("d=",numDepth ),
          col=myColors, pch=15,
          bty="n",
          cex=0.8,
          pt.cex=1.2
          )
  
  dev.off();
}

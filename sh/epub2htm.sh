#!/bin/csh

# TODO
# more natural than cwbreakstring in the output htm is to
# use the unzipping which unzips to multiple htmfiles

setenv input $1
if ( -f $input ) then

  setenv wrkdir /tmp/epub2txt_$$
  setenv wrkfile $wrkdir/input_$$.epub
  setenv sedfile /Users/wiggins/gd/local/seiton/sed/epub2htm.sed 
  setenv outfile $wrkdir/output.htm
  setenv txtfile $wrkdir/output.txt
  #setenv outdir $2
  if ( $#argv == 2 ) then
    setenv slug $2
  else
    setenv slug output
  endif

  echo '...' $input = inputfile
  echo '...' starting at `date`
  echo '...' workding directory = $wrkdir

  mkdir $wrkdir
  cp -f $input $wrkfile
  cp $sedfile $wrkdir
  cd $wrkdir


  # clean
  rm -f $outfile $txtfile starts.dat stops.dat start-shift.dat output-ch*.txt seds.sh minstas.sh

  # pandoc
  # most important line in the code
  pandoc $wrkfile -o $outfile
  # sed once
  sed -f $sedfile < $outfile > $txtfile

  # SPLIT
  # find splits, decrement 1 for the title to define starts
  #
  # examples:
  ## for Lepore, I added '----' 
  ## for Worm, I added '[Chapter 10: Cybarmageddon]{.calibre38}'. that failed
  ##   so I added {.calibre12}
  ## for cities, I added 'Chapter-Title'

  ## to do: change all of these to a special cwbreakchar in $sedfile,
  ## none of this should be done here. all in the sedfile
   
  grep -n -e 'cw_epub_breakstring' $txtfile | cut -d: -f1 | awk '{print $0-1}' > starts.dat

  ## # debug:
  ## cp starts.dat /tmp

  # make decrement 1 more to define stops
  cat starts.dat | awk '{print $0-1}' >! stops.dat

  # shift the starts
  echo "1" >! start-shift.dat
  cat starts.dat >> start-shift.dat
  mv -f start-shift.dat starts.dat
  # shift the stops
  wc -l $txtfile | awk '{print $1}' >> stops.dat

  # do the splitting
  ## first make the sed script
  paste starts.dat stops.dat \
    | awk -F'\t' '{print "sed -n -e "$1","$2"p < $txtfile >! $slug-ch"NR".htm"}' \
    >! seds.sh
  ## now source the sed script
  source seds.sh

  foreach htm_chapter ( $slug-ch*.htm )
    lynx -width=999 -dump -hiddenlinks=ignore -image_links=no -minimal -nobold -nolist -pseudo_inlines -force_html $htm_chapter > $htm_chapter:r.txt
  end

  seq 1 `wc -l starts.dat | awk '{print $1}'` | awk '{print "sleep 2 ; cat '$slug'-ch"NR".txt | minsta -s '$slug'-ch"NR}' >! minstas.sh

  echo '...' successfully split into `wc -l seds.sh| awk '{print $1}'` files
  echo '...' completed at `date`
else
  echo input file $input not found
endif

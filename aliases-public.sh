alias no "pbcopy < ~/.no.txt"
alias gcomp 'open https://mail.google.com/mail/u/0/#compose/\!*'
alias mcomp "open 'https://mail.google.com/mail/u/0/x/?&v=b&eot=1&pv=tl&cs=b'"
alias dv "setenv vstr ~/Desktop/cwnote_`date +20%yy%mm%dd%Hh%M`;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
alias dv "setv;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
alias learn "source $cwaliases ; source $cwpaliases"
alias teach "vi + $cwaliases;vi + $cwpaliases"
alias l '/bin/ls -ltrFsA'
alias mi 'mv -i'
alias up "cd .."
alias cd-htm cd /Users/wiggins/Documents/public_html
alias cd-mise cd $mise
alias dump "learn;pbpaste > `datestr`"
alias please sudo
alias jsc /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Resources/jsc
alias dusort "learn;du | sort -nr >! dusort_`date +%yy%mm%dd_%Hh%Mm%Ss`"
alias rstudio open /Applications/RStudio.app/
alias permute "perl -MList::Util=shuffle -e 'print shuffle <>'"
alias hai open http://example.com



# unix essentials
alias l '/bin/ls -ltrFsA'
alias mi 'mv -i'
alias up "cd .."
alias please sudo

# places to go
alias cd-htm cd /Users/wiggins/Documents/public_html
alias cd-mise cd $mise

alias dump "learn;pbpaste > `datestr`"
alias jsc /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Resources/jsc
alias dusort "learn;du | sort -nr >! dusort_`date +%yy%mm%dd_%Hh%Mm%Ss`"
alias rstudio open /Applications/RStudio.app/
alias permute "perl -MList::Util=shuffle -e 'print shuffle <>'"
alias hai open http://example.com
alias chrome "open ~/mise/bin/chrome"
alias fox "open -a 'Firefox' \!:*"
alias inpr "open http://www.npr.org/infiniteplayer/"

# google-fu
alias gcomp 'open https://mail.google.com/mail/u/0/#compose/\!*'
alias mcomp "open 'https://mail.google.com/mail/u/0/x/?&v=b&eot=1&pv=tl&cs=b'"
alias mm "open https://mail.google.com/mail/u/0/x/"
alias gread "fox  'http://www.google.com/reader/view/#overview-page'"
alias frm "gm from:\!*"
alias to "gm to:\!*"
#alias gcal fox http://www.google.com/calendar/render
#alias gcal camino http://www.google.com/calendar/render
#alias gcal camino https://www.google.com/calendar/
#alias gcal fox https://www.google.com/calendar/
#alias gcal chrome http://www.google.com/calendar/render
alias gcal fox https://www.google.com/calendar/b/0/render
# NB: 'gc' intended for use with google <- /usr/local/bin/google
alias gc google calendar add

#news
#alias npr "open -a RealPlayer rtsp://real.npr.na-central.speedera.net/real.npr.na-central/news.db.rm"
#alias npr "open 'http://www.npr.org/player/v2/mediaPlayer.html?action=1&t=4&islist=false';osascript -e 'set volume 3'"
#alias npr "open 'http://stitcher.com/listen.php?fid=4801'"
#alias bbc "open -a RealPlayer http://www.bbc.co.uk/worldservice/news/summary.ram"
#alias bbc "open -a RealPlayer http://www.bbc.co.uk/worldservice/meta/tx/nb/summary5min_au_nb.ram"
#alias bbc "open 'http://www.bbc.co.uk/worldservice/audioconsole/?stream=news_bulletin';osascript -e 'set volume 5'"
alias bbc "open 'http://www.bbc.co.uk/worldservice/audioconsole/?stream=news_bulletin'"
#alias 1010 "open 'http://infinity.wm.llnwd.net/infinity_wins-am?MSWMExt=.asf'"
alias 1010 "open 'http://69.28.176.133:80/infinity_wins-am?MSWMExt=.asf'"
#alias 880 "open 'http://infinity.wm.llnwd.net/infinity_wbcs-am?MSWMExt=.asf'"



# meta (aliases to help make aliases) 
alias aalias 'echo "alias \!*" >> $cwaliases ; learn '
alias palias 'echo "alias \!*" >> $paliases ; learn '
alias learn "source $cwaliases ; source $cwpaliases"
alias teach "vi + $cwaliases;vi + $cwpaliases"
alias pteach "vi + $cwpaliases"
alias gugc "git pull origin master;git commit -a;git push origin master"
alias miseup "cd-mise;gugc;cd -"

# misc:
alias sniff open /Applications/iStumbler.app/
alias estrip "pbpaste | fix | tr ' , (){}:;[]=<>' '\n' | grep @ | sort -bfdu | grep -v wiggins@tantanmen | tr '\n' ' ' | fix | sed -e 's/ [ ]*/,/g' | pbcopy"
## misc auxfile tricks:
alias dv "setenv vstr ~/Desktop/cwnote_`date +20%yy%mm%dd%Hh%M`;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
alias dv "setv;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
alias no "pbcopy < ~/.no.txt"
alias avail "vi ~/available.txt; pbcopy < ~/available.txt"
### taking/using quicknotes:
alias v 'setenv vstr $ndir/cwnote_`date +20%yy%mm%dd%Hh%M`; vi $vstr; echo vstr=$vstr'
alias pv 'pbcopy < $vstr'
alias sv 'source $vstr'
#alias hg 'history 99999999999999 | grep \!:1 | grep -v hg'
alias hG 'history 99999999999999 | grep -i \!:1 | grep -v hG'
alias similar "go related:\!:*"
#alias repof "mkdir mat/ dat/ doc/ fig/ log/ ref/ src/ out/ aux/; touch mat/.DS_store dat/.DS_store doc/.DS_store fig/.DS_store log/.DS_store ref/.DS_store src/.DS_store out/.DS_store aux/.DS_store "
alias repo "mkdir mat/ dat/ doc/ fig/ log/ ref/ src/ out/ aux/ lit/"
alias bday "lynx -dump -hiddenlinks=ignore -image_links=no -minimal -nobold -nolist -pseudo_inlines -force_html http://en.m.wikipedia.org/wiki/`date +%h_%d` | awk '/^Births/,/^Deaths/' | grep -v -f $boring"
alias boring "sort -bfdu $boring > $tmp ; mv -f $tmp $boring ; vi $boring; wig2cu $boring ~/Documents/Scripts/aux/boring_people.asc"
alias dsnyc "open -a safari https://plus.google.com/u/0/communities/102074015406128769868"

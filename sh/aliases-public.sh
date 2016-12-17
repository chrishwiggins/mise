# SET VARIABLES

## DIRECTORIES
set cwhome=$home
set mise=$cwhome/mise/
## FILES
set cwpaliases=$mise/sh/aliases-public.sh

## conditionals
if (! $?ndir) then
  set ndir=$cwhome/Documents/ndir
endif
if (! $?phonefile) then
  set phonefile=$cwhome/Documents/phonebook.txt
endif

# unix essentials
alias l '/bin/ls -ltrFsA'
alias mi 'mv -i'
alias up "cd .."
alias please sudo

# places to go
alias cd-htm cd ~/Documents/public_html
alias cd-mise cd $mise

# handy, needed below
alias datestr 'date +%Y-%m-%dT%H:%M:%S'


alias dump "learn;pbpaste > `datestr`"
alias mdump "learn;pbpaste > `datestr`.eml;pbmunpack;mv mail-dump `datestr`-files"
alias jsc /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Resources/jsc
alias dusort "learn;date;du | sort -nr >! dusort_`date +%yy%mm%dd_%Hh%Mm%Ss`;date"
alias rstudio open /Applications/RStudio.app/
alias permute "perl -MList::Util=shuffle -e 'print shuffle <>'"
alias hai open http://example.com
alias fox "open -a 'Firefox' \!:*"
alias inpr "open http://www.npr.org/infiniteplayer/"

# google-fu
alias drive "open /Applications/Google\ Drive.app/"
alias filter "open 'https://mail.google.com/mail/u/0/#settings/filters'"
alias dsnyc "open -a safari https://plus.google.com/u/0/communities/102074015406128769868"
alias star "open 'https://mail.google.com/mail/u/0/?tab=mm#starred'"
alias gcomp 'open https://mail.google.com/mail/u/0/#compose/\!*'
alias mcomp "open 'https://mail.google.com/mail/u/0/x/?&v=b&eot=1&pv=tl&cs=b'"
alias mm "open https://mail.google.com/mail/u/0/x/"
#alias gread "fox  'http://www.google.com/reader/view/#overview-page'"
alias frm "gm from:\!*"
alias to "gm to:\!*"
#alias gcal fox http://www.google.com/calendar/render
#alias gcal camino http://www.google.com/calendar/render
#alias gcal camino https://www.google.com/calendar/
#alias gcal fox https://www.google.com/calendar/
#alias gcal chrome http://www.google.com/calendar/render
alias gcal fox https://www.google.com/calendar/b/0/render
alias ccal chrome https://www.google.com/calendar/b/0/render
# NB: 'gc' intended for use with google <- /usr/local/bin/google
alias gc google calendar add

#news
#alias npr "open -a RealPlayer rtsp://real.npr.na-central.speedera.net/real.npr.na-central/news.db.rm"
#alias npr "open 'http://www.npr.org/player/v2/mediaPlayer.html?action=1&t=4&islist=false';osascript -e 'set volume 3'"
#alias npr "open 'http://stitcher.com/listen.php?fid=4801'"
#alias bbc "open -a RealPlayer http://www.bbc.co.uk/worldservice/news/summary.ram"
#alias bbc "open -a RealPlayer http://www.bbc.co.uk/worldservice/meta/tx/nb/summary5min_au_nb.ram"
#alias bbc "open 'http://www.bbc.co.uk/worldservice/audioconsole/?stream=news_bulletin';osascript -e 'set volume 5'"
alias bbc "fox 'http://www.bbc.co.uk/worldservice/audioconsole/?stream=news_bulletin'"
#alias 1010 "open 'http://infinity.wm.llnwd.net/infinity_wins-am?MSWMExt=.asf'"
alias 1010 "open 'http://69.28.176.133:80/infinity_wins-am?MSWMExt=.asf'"
#alias 880 "open 'http://infinity.wm.llnwd.net/infinity_wbcs-am?MSWMExt=.asf'"



# meta (aliases to help make aliases) 
alias palias 'echo "alias \!*" >> $paliases ; learn '
# alias learn "source $cwpaliases"
alias pteach "vi + $cwpaliases"
alias gugc "git pull origin master;git commit -a ;git push origin master"
alias miseup "cd-mise;gugc;cd -"
alias remise "cd-mise;git pull origin master;cd -"

# misc:
alias att gm has:attachment
alias sniff open /Applications/iStumbler.app/
alias estrip "fix | tr ' , (){}:;[]=<>' '\n' | grep @ | sort -bfdu | grep -v -e wiggins@tantanmen -e wiggins@karaage -e '^@' -e git@github.com | tr '\n' ' ' | fix | sed -e 's/ [ ]*/,/g' "
## misc auxfile tricks:
#alias dv "setenv vstr ~/Desktop/cwnote_`date +20%yy%mm%dd%Hh%M`;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
#alias dv "setv;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
alias avail "vi ~/available.txt; sed '/^=/q'  ~/available.txt | grep -v '^=' | pbcopy"


### taking/using quicknotes:
# alias setv 'setenv vstr $ndir/cwnote_`date +20%yy%mm%dd%Hh%M`'
alias setv 'setenv vstr $ndir/cwnote_`date +%Y_%m_%dT%H_%M_%S`.md'
alias vv 'setv; pbpaste >! $vstr; vi $vstr; echo vstr=$vstr'
alias v 'setv; vi +star $vstr; echo vstr=$vstr'
alias pv 'pbcopy < $vstr'
alias sv 'source $vstr'

#alias hg 'history 99999999999999 | grep \!:1 | grep -v hg'
alias hG 'history 99999999999999 | grep -i \!:1 | grep -v hG'
alias similar "gsearch related:\!:*"
#alias repof "mkdir mat/ dat/ doc/ fig/ log/ ref/ src/ out/ aux/; touch mat/.DS_store dat/.DS_store doc/.DS_store fig/.DS_store log/.DS_store ref/.DS_store src/.DS_store out/.DS_store aux/.DS_store "
#alias bday "lynx -dump -hiddenlinks=ignore -image_links=no -minimal -nobold -nolist -pseudo_inlines -force_html http://en.m.wikipedia.org/wiki/`date +%h_%d` | awk '/^Births/,/^Deaths/' | grep -v -f $boring"
#alias repo "mkdir dat/ doc/ fig/ log/ ref/ src/ out/ aux/ lit/ www/ eml/ nul/; wget -O README.md --quiet --no-check-certificate https://gist.githubusercontent.com/anonymous/4fa592e17f1bdfd79e6dbdb0cf820df5/raw/9f0e81a77d94d74257641eb8279303b65fa0a85e/a.rb"
alias repo "mkdir git/ dat/ doc/ fig/ log/ ref/ src/ out/ aux/ lit/ www/ eml/ nul/; wget -O README.md --quiet --no-check-certificate https://gist.githubusercontent.com/chrishwiggins/e31c6d0129365d8100f20f97750f49b7/raw/7527ef00dde566c7cfe57d6bee6136482faa5330/repo-structure.md"
#alias boring "sort -bfdu $boring > $tmp ; mv -f $tmp $boring ; vi $boring; wig2cu $boring ~/Documents/Scripts/aux/boring_people.asc"
alias rewind "ls -t $ndir | xargs -I % more $ndir/%" 
alias http "open http://\!*"
alias clean-browser 'open /Applications/Camino.app \!*'
alias disp 'open /System/Library/PreferencePanes/Displays.prefPane/'
alias print 'open /System/Library/PreferencePanes/PrintAndScan.prefPane/'
alias json-grep jgrep
alias g gsearch
#alias tend "backup-tantanmen&;supdate&;sweep&;open /Applications/App\ Store.app/;brew-tend;pip-tend;conda-tend;cd ~;dusort"
#alias tend "supdate&;sweep&;open /Applications/App\ Store.app/;qtend;cd ~;dusort;brew link openssl --force;mas upgrade"
alias tend "sweep&;open /Applications/App\ Store.app/;qtend;cd ~;dusort;brew link openssl --force"
alias qtend "brew-tend;pip-tend;conda-tend;brews;cabal-tend;gem-tend;gc-tend;mas upgrade"
alias gc-tend "gcloud components update"
alias gem-tend "gem cleanup;gem update"
# ":" is read as "%" or "/" and is bad for makefile variables:
# alias datestr date +%Y-%m-%dT%H-%M-%S
# alias datestr date +%Y-%m-%dT%H-%M-%S
alias datestr date +%Y-%m-%dT%Hh%Mm%S
#alias brew-tend "brew upgrade --all ; brew update;brew doctor;brew linkapps;brew prune;brew link openssl --force; brew cleanup -s"
alias brew-tend "brew upgrade ; brew update;brew doctor;brew linkapps;brew prune;brew link openssl --force; brew cleanup -s"
alias pip-tend "pip install --upgrade distribute; pip install --upgrade pip"
alias hask-tend "cabal update;  ghc-pkg check --simple-output"
#alias conda-tend "/sw/anaconda/bin/conda update conda;conda update --prefix /sw/anaconda anaconda"
alias conda-tend "conda update conda;conda update --prefix /anaconda anaconda;conda clean -tipsy"
alias cabal-tend "cabal update"
alias ogit "open 'https://github.com/chrishwiggins?tab=repositories'"
alias normalize "sed -f $mise/sed/normalize "
alias openjpgs "find . | grep -i -e 'jpg' -e 'jpeg' | normalize | xargs open"
alias cdc "pwd | normalize | pbcopy"
alias cdp 'cd `pbpaste`'
alias mise "open https://github.com/chrishwiggins/mise"
alias citibike open http://www.citibikenyc.com/stations

# spelling while typing is hard
alias docus focus
alias aalais aalias
alias gcmop gcomp
alias mdkdir mkdir
alias duff diff
alias mdkir mkdir
alias mkddir mkdir
alias oepn open
alias fidn find
alias gttp http
alias alais alias
alias moer more
alias mroe more
alias pbvx "pbpaste >! /tmp/$$_pbcx; source /tmp/$$_pbcx; rm -f /tmp/$$_pbcx"
alias pbcx "pbcopy;pbvx"
alias mor more
alias poen open
alias pu up


#alias onion 'open http://www.theonion.com/content/index'
alias onion echo "try mindful breathing instead. go ahead"

alias appstore "open /Applications/App\ Store.app/"
alias st 'open /Applications/Sublime\ Text\ 2.app/'
alias st2 '/Applications/Sublime\ Text\ 2.app/Contents/SharedSupport/bin/subl'

alias get git clone

#alias airport 'open /Applications/Utilities/AirPort\ Admin\ Utility.app/'
alias airport 'open /Applications/Utilities/AirPort\ Utility.app/'
alias els "echo 'For reasons explained in detail at http://bactra.org/weblog/864.html, I will not review for any Elsevier publication. I look forward to assisting your journal in the future, after it switches publishers.' | pbcopy"
alias duplist 'dupseek -f hn .'
alias hh history -h
alais grr g rstats
alias rstack "open 'http://stats.stackexchange.com/search?q=%5Br%5D+'"
alias urls "asciify| fix | tr '<>[]()\ ' '\n' | grep -i 'http'"
alias pbmunpack "mkdir mail-dump ;pbpaste | munpack -t -f -C mail-dump"
alias deck "open /Applications/TweetDeck.app/;awk '/Keyboard shortcuts/,/   Related articles:/' < $cwhome/Documents/Help/TweetDeck/20170322.txt"
alias deck onion
alias otb fox http://www.onetimebox.org/
alias sql "mysql.server start;mysql -uroot;mysql.server stop"
alias sheet "open https://docs.google.com/spreadsheet/"

#phone aliases
alias call "echo \!* >> $phonefile"
alias ph "grep -i \!* $phonefile | tr '\' '\n'"
alias phone "vi + $phonefile"
alias mtg-no "grep -v '^%' ~/mise/aux/rp-decline.asc| pbcopy"
alias mtg-q "grep -v '^%' ~/mise/aux/rp-mtg.asc| pbcopy"

# LaTeX stuff
alias plat "pdflatex \!:*:r ; bibtex \!:*:r ; pdflatex \!:*:r ; pdflatex \!:*:r ; grep Citation \!:*:r.log "
alias lat "latex \!:*:r ; bibtex \!:*:r ; latex \!:*:r ; latex \!:*:r ; grep Citation \!:*:r.log;dvipdf \:*:r.dvi "
alias plath "pdflatex -halt-on-error \!:*:r ; bibtex \!:*:r ; pdflatex -halt-on-error \!:*:r ; pdflatex -halt-on-error \!:*:r "
alias platf "pdff \!:*:r ; bibtex \!:*:r ; pdff \!:*:r ; pdff \!:*:r ; grep Citation \!:*:r.log "
alias pdff pdflatex -interaction=nonstopmode

# more misc
alias asciify "/usr/bin/perl -pe 's/[^[:ascii:]]/+/g'"
alias bow "asciify | fix | lower | words | nodud | sort -bfd | uniq -c | sort -nr"
alias newdoc "open https://docs.google.com/document/"
#alias addy "open /Applications/Address\ Book.app/"
alias addy "open /Applications/Contacts.app/"
alias skindle "open -a /Applications/Send\ to\ Kindle/Send\ to\ Kindle.app/ \!:*"
alias mute-fix sudo killall coreaudiod
alias bs "curl -silent http://www.wisdomofchopra.com/iframe.php | grep 'og:description' | cut -d\' -f2"
alias dir-nyt 'pbcopy < $cwaux/dir-nyt.txt'
alias dir-205 'pbcopy < $cwaux/dir-205.txt'
alias dir-428 'pbcopy < $cwaux/dir-428.txt'
alias muttf "cat /dev/null | mutt -H \!:*"
alias omail "open mailto:\!*"
#alias mail "mutt \!*"
alias distract "boxes;ichat;adium;skype;voice"
alias brews "brew list > $cwaux/homebrew-`date +%Y-%m-%dT%H:%M:%S`.asc;rmdups $cwaux/homebrew-*.asc"
alias r-installed "which-r > $cwaux/r-installed-`date +%Y-%m-%dT%H:%M:%S`.asc;rmdups $cwaux/r-installed-*.asc"
alias pb2gist gist -o -P

alias pocket "pbpaste | mutt -s '\!:* @`date +%yy%mm%dd_%Hh%Mm%Ss`' add@getpocket.com"
alias ttweather "lynx -nolist -width=1000 -dump 'http://www.freeweather.com/cgi-bin/weather/weather.cgi?daysonly=0&maxdays=11&zipcode=10027' | asciify | fix | awk '/^Daily/,/^Sunset/'"
alias omail open /Applications/Mail.app/
alias olede open https://github.com/ledeprogram/courses/tree/master/algorithms
#alias mypy /usr/bin/python
#alias mbo "skype; boxes ; voice ; ichat; focus;telegram;slack;DECK"
#alias mbo "skype; boxes ; voice ; ichat; telegram;slack;DECK;focus"
# alias mbo "iboxes; ichat; voice"
alias mbo "f;boxes; ichat; voice"
alias md2pdf "pandoc --number-sections \!:1 -s -o \!:1:r.pdf"
alias md2htm "pandoc \!:1 -s -o \!:1:r.htm"
alias clio "fox 'http://clio.cul.columbia.edu'"
alias roi "open ~/Music/iTunes/iTunes\ Media/Music/The\ Breeders/LSXX/1-05\ Roi.m4a"
alias beet "open /Users/wiggins/Music/iTunes/iTunes\ Media/Music/Compilations/7\ Conductors\ vs.\ Beethoven\'s\ 7th/06\ Symphony\ No.\ 7\ in\ A\ Major,\ Op.\ 92_\ II.\ Allegretto.m4a"
alias pbpate pbpaste
alias acal fox http://registrar.columbia.edu/event/academic-calendar
alias omutts "cd $odir;mutts;cd -"
alias lock "/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend"

alias zip4 "open 'https://tools.usps.com/go/ZipLookupAction'!'input.action?mode=0&refresh=true'"
# alias rest sudo shutdown -s now
alias rest pmset sleepnow
alias oed "fox 'http://www.columbia.edu/cgi-bin/cul/resolve?AKV9469'"
alias thus "echo ∴|pbcopy"
alias sheets "open 'https://drive.google.com/drive/u/0/#search?q=type%3Aspreadsheet'"
alias hamming "pbcopy < ~/Documents/Science/Advising/Ideas/Hamming/hamming-you-and-your-research.txt"
alias kreps "echo 'https://twitter.com/jaykreps/status/219977241839411200' | pbcopy "
alias pbstrip "pbpaste|estrip|pbcopy"
alias reline "tr '\n' ' ' | tr '+' '\n' | fix "
alias ngit "open https://github.com/new"
alias wiktionary open "https://en.wiktionary.org/wiki/\!:*"
alias cwnotes "head `ls -1t $ndir/cwnote_201* | grep -v -e '(' -e ')'` | more"
alias cwnotes 'head `ls -1t $ndir/cwnote_201* | normalize` | more'

# add commodore basic
alias basic cbmbasic
alias no-wiml "cat $mise/aux/no-wiml.txt $setup/aux/wiml.tsv | pbcopy"
alias shrug "echo '¯\_(ツ)_/¯' | pbcopy"
alias rand 'echo `jot -r 1 0 1000`/1000 | bc -l| cut -c 1-4'
alias vi-null vim -u NONE

alias nterm 'open `find ~/gd/aux/osx-terminal-themes/schemes | gshuf | head -\!:* | normalize`'
# alias term 'open `find ~/gd/aux/osx-terminal-themes/schemes | gshuf | head -1 | normalize`'
# good fu: exploits quick add but adds browser to edit event, send invitesjj
alias oslow 'fox `slow \!:* | tr '"'"' '"'"' '"'"'\n'"'"' | grep ^http`'
alias logo open /Applications/ACSLogo.app/
alias remake 'vi makefile'
alias polls "lynx -dump 'http://projects.fivethirtyeight.com/2016-election-forecast/?ex_cid=rrpromo#plus' | grep -A 2 'Hillary Clinton' | more | head -3 | grep '%'; lynx -dump 'http://www.nytimes.com/interactive/2016/upshot/presidential-polls-forecast.html' | more | grep Clinton | grep 'chance to win'"
#alias polls "lynx -dump 'http://www.nytimes.com/interactive/2016/upshot/presidential-polls-forecast.html' | more | grep Clinton | grep 'chance to win'"



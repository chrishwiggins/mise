# SET VARIABLES

## DIRECTORIES
set cwhome=$home
set mise=$cwhome/mise/
## FILES
set cwpaliases=$mise/sh/aliases-public.sh

 #echo conditionals
## conditionals
if (! $?ndir) then
  set ndir=$cwhome/Documents/ndir/
  mkdir -p $ndir
  touch $ndir/cwnote_201y_mm_ddThh_mm_ss.md
endif
if (! $?phonefile) then
  set phonefile=$cwhome/Documents/phonebook.txt
endif
#if (! $?cwaux) then
  #echo resetting cwaux
  #set cwaux=$cwhome/Documents/aux/
#endif
set mise_aux=${mise}/aux

 #echo unix
# unix essentials
alias l '/bin/ls -ltrFsA'
alias ll '/bin/ls -ltrFs'
alias mi 'mv -i'
alias up "cd .."
alias please sudo

# places to go
alias cd-mise cd $mise

# handy, needed below
#alias datestr 'date +%Y-%m-%dT%H-%M-%S '
#alias datestr 'date +%Y-%m-%dT%H:%M:%S '
#alias datestr 'date +%Y-%m-%dT%Hh%Mm%Ss'
#alias datestr    date +%Y_%m_%dT%Hh%Mm%Ss
alias datestr    date +%Y-%m-%dT%Hh%Mm%Ss
alias datetxt 'date "+%a, %Y-%m-%d, %H:%M"'
alias datecp "datestr|pbcopy"
alias dstr datestr
alias pbdate 'datestr| pbcopy'
alias dstr 'setenv dstr `datestr`'


alias dump "learn;pbpaste > `datestr`"
alias mdump "learn;pbpaste > `datestr`.eml;pbmunpack;mv mail-dump `datestr`-files"
alias jsc /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Resources/jsc
alias dusort "learn;date;du | sort -nr >! dusort_`date +%yy%mm%dd_%Hh%Mm%Ss`;date"
alias rstudio open /Applications/RStudio.app/
alias permute "perl -MList::Util=shuffle -e 'print shuffle <>'"
alias hai open http://example.com
#alias fox "open -a 'Firefox' \!:*"
alias fox "open "
alias inpr "open http://www.npr.org/infiniteplayer/"

# google-fu
alias drive "open /Applications/Google\ Drive.app/"
alias filter "open 'https://mail.google.com/mail/u/0/#settings/filters'"
alias dsnyc "open -a safari https://plus.google.com/u/0/communities/102074015406128769868"
alias star "open 'https://mail.google.com/mail/u/0/?tab=mm#starred'"
alias gcomp 'open https://mail.google.com/mail/u/0/#compose/\!*'
alias mcomp "open 'https://mail.google.com/mail/u/0/x/?&v=b&eot=1&pv=tl&cs=b'"
alias mm "open https://mail.google.com/mail/u/0/x/"
alias mma "open 'https://mail.google.com/mail/u/0/x/?&s=a'"
#alias gread "fox  'http://www.google.com/reader/view/#overview-page'"
#alias gcal fox http://www.google.com/calendar/render
#alias gcal camino http://www.google.com/calendar/render
#alias gcal camino https://www.google.com/calendar/
#alias gcal fox https://www.google.com/calendar/
#alias gcal chrome http://www.google.com/calendar/render
# alias gcal fox https://www.google.com/calendar/b/0/render
alias gcal pers-gmail-browser https://www.google.com/calendar/b/0/render
alias gcals "pers-gmail-browser 'https://calendar.google.com/calendar/u/0/r/search?q=\!:*'"
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
#deprecated/older public repos
alias gugc "echo try gugm;git pull origin master;git commit -a ;git push origin master"
alias gugm "git pull origin main;git commit -a ;git push origin main"
alias gbgb "git pull ;git commit -a ;git push "
alias miseup "cd-mise;gugm;cd -"
#alias remise "cd-mise;git pull origin master;cd -"
alias remise "cd-mise;git pull origin main;cd -"

# misc:
#alias sniff open /Applications/iStumbler.app/
#alias estrip "pbpaste | tr '\,:;[]= <>' '\n' | grep @ | tr '\n' ' ' | fix | sed -e 's/ [ ]*/,/g' | pbcopy"
alias estrip "fix | /usr/bin/perl -pe 's/[^[:ascii:]]/+/g' | tr ' , (){}:;[]=<>\*' '\n' | grep @ | sort -bfdu | grep -v -e wiggins@tantanmen -e wiggins@karaage -e '^@' -e git@github.com | tr '\n' ' ' | fix | sed -e 's/\.\ /\ /g' -e 's/ [ ]*/,/g' "
## misc auxfile tricks:
#alias dv "setenv vstr ~/Desktop/cwnote_`date +20%yy%mm%dd%Hh%M`;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
#alias dv "setv;grep '[A-z]' $gtddir/cwttd_20* | sort -rn | cut -d_ -f2- | sed 's/\:/\: /' | pbcopy; vv"
alias avail "vi ~/available.txt; sed '/^=/q'  ~/available.txt | grep -v '^=' | pbcopy"


### taking/using quicknotes:
# alias setv 'setenv vstr $ndir/cwnote_`date +20%yy%mm%dd%Hh%M`'
alias setv 'setenv vstr $ndir/cwnote_`date +%Y_%m_%dT%H_%M_%S`.md'
alias setd 'setenv dstr $ndir/cwnote_`date +%Y_%m_%d`.md'
alias vv 'setv; pbpaste >! $vstr; vi $vstr; echo vstr:;echo $vstr'
alias v 'setv; vi $vstr; echo vstr:;echo $vstr'
alias tv 'setv; echo % `datetxt` >$vstr ; vi +16 -c startinsert $vstr; echo vstr:;echo $vstr'
alias d 'setd; date +"%a %b %d, week %U of %Y" >>! $dstr; vi $dstr; echo dstr:;echo $dstr'
alias o 'setv; vi $vstr; oai-f $vstr'
alias sv 'source $vstr'
alias gv 'smail $vstr'
# v & b (quicknotes+longnotes)
alias pv 'pbcopy < $vstr'
alias pb 'pbcopy < $bstr'
alias iv 'ispell $vstr'
alias ib 'ispell $bstr'

#alias hg 'history 99999999999999 | grep \!:1 | grep -v hg'
alias hG 'history 99999999999999 | grep -i \!:1 | grep -v hG'
alias similar "gsearch related:\!:*"
#alias repof "mkdir mat/ dat/ doc/ fig/ log/ ref/ src/ out/ aux/; touch mat/.DS_store dat/.DS_store doc/.DS_store fig/.DS_store log/.DS_store ref/.DS_store src/.DS_store out/.DS_store aux/.DS_store "
#alias bday "lynx -dump -hiddenlinks=ignore -image_links=no -minimal -nobold -nolist -pseudo_inlines -force_html http://en.m.wikipedia.org/wiki/`date +%h_%d` | awk '/^Births/,/^Deaths/' | grep -v -f $boring"
#alias repo "mkdir dat/ doc/ fig/ log/ ref/ src/ out/ aux/ lit/ www/ eml/ nul/; wget -O README.md --quiet --no-check-certificate https://gist.githubusercontent.com/anonymous/4fa592e17f1bdfd79e6dbdb0cf820df5/raw/9f0e81a77d94d74257641eb8279303b65fa0a85e/a.rb"
# alias repo "mkdir git/ dat/ doc/ fig/ log/ ref/ src/ out/ aux/ lit/ www/ eml/ nul/; wget -O README.md --quiet --no-check-certificate https://gist.githubusercontent.com/chrishwiggins/e31c6d0129365d8100f20f97750f49b7/raw/7527ef00dde566c7cfe57d6bee6136482faa5330/repo-structure.md"
# alias repo "mkdir git/ dat/ doc/ doc/backups fig/ log/ ref/ src/ out/ aux/ lit/ www/ eml/ nul/; wget -O README.md --quiet --no-check-certificate https://gist.githubusercontent.com/chrishwiggins/e31c6d0129365d8100f20f97750f49b7/raw/7527ef00dde566c7cfe57d6bee6136482faa5330/repo-structure.md; wget -O doc/makefile  --quiet --no-check-certificate https://gist.githubusercontent.com/chrishwiggins/ccd26e1c07ccb20644c808c7e1aed376/raw/a7a0ebdaede5f9d19a82a2903b5e473b78cb4e60/makefile-2017-01-18c; wget -O doc/writeup.sed --no-check-certificate https://gist.githubusercontent.com/chrishwiggins/804c317cfde389bc16ba7b2bfa5a2126/raw/ee67df7025ae2cb15f0c8ec8c9f4c3889b9e87a8/a.rb"
alias repo "mkdir git/ dat/ doc/ doc/backups fig/ log/ ref/ src/ out/ aux/ lit/ www/ eml/ nul/; curl -o README.md --silent  https://gist.githubusercontent.com/chrishwiggins/e31c6d0129365d8100f20f97750f49b7/raw/7527ef00dde566c7cfe57d6bee6136482faa5330/repo-structure.md; curl -o doc/makefile  --silent  https://gist.githubusercontent.com/chrishwiggins/ccd26e1c07ccb20644c808c7e1aed376/raw/a7a0ebdaede5f9d19a82a2903b5e473b78cb4e60/makefile-2017-01-18c; curl -o doc/writeup.sed  https://gist.githubusercontent.com/chrishwiggins/804c317cfde389bc16ba7b2bfa5a2126/raw/ee67df7025ae2cb15f0c8ec8c9f4c3889b9e87a8/a.rb"
alias g-writeup "mkdir writeup/ writeup/backups ;curl -o writeup/makefile  --silent  https://gist.githubusercontent.com/chrishwiggins/ccd26e1c07ccb20644c808c7e1aed376/raw/a7a0ebdaede5f9d19a82a2903b5e473b78cb4e60/makefile-2017-01-18c; curl -o writeup/writeup.sed  https://gist.githubusercontent.com/chrishwiggins/804c317cfde389bc16ba7b2bfa5a2126/raw/ee67df7025ae2cb15f0c8ec8c9f4c3889b9e87a8/a.rb;cd writeup"
alias rewind "ls -t $ndir | xargs -I % more $ndir/%" 
alias http "open http://\!*"
alias clean-browser 'open /Applications/Camino.app \!*'
alias disp 'open /System/Library/PreferencePanes/Displays.prefPane/'
alias print 'open /System/Library/PreferencePanes/PrintAndScan.prefPane/'
alias json-grep jgrep
alias g gsearch
#alias tend "backup-tantanmen&;supdate&;sweep&;open /Applications/App\ Store.app/;brew-tend;pip-tend;conda-tend;cd ~;dusort"
#alias tend "supdate&;sweep&;open /Applications/App\ Store.app/;qtend;cd ~;dusort;brew link openssl --force;mas upgrade"
#alias tend "date;sweep&;open /Applications/App\ Store.app/;qtend;cd ~;dusort;brew link openssl --force;date"
#alias tend "date;open /Applications/App\ Store.app/;qtend;cd ~;dusort;brew link openssl --force;date"
#alias tend "date;open /Applications/App\ Store.app/;qtend;cd ~;brew link openssl --force;date"
#alias tend "date;gback;qtend;cd ~;brew link openssl --force;  softwareupdate --all --install ; date"
#alias tend "clear;date;gback;qtend;cd ~;brew link openssl --force;  softwareupdate --all --install ; date"
alias tend "clear;date;qtend;cd ~;brew link openssl --force;  softwareupdate --all --install ; date"
#alias qtend "brew-tend;pip-tend;conda-tend;brews;cabal-tend;gem-tend;gc-tend;mas upgrade"
#alias qtend "brew-tend;pip-tend;brews;cabal-tend;gem-tend;gc-tend;mas upgrade;port-tend"
#alias qtend "brew-tend;pip3-tend;brews;cabal-tend;gem-tend;gc-tend;mas upgrade;port-tend"
alias qtend "brew-tend;pip3-tend;brews;cabal-tend;gem-tend;gc-tend;mas upgrade"
alias qqtend "q-brew-tend;pip-tend;brews;cabal-tend;gem-tend;gc-tend;mas upgrade"
alias gc-tend "gcloud components update -q"
# 2019-01-27 this needs sudo sadly: 
alias gem-tend "gem cleanup;gem update"
alias sudo-gem-tend "sudo gem cleanup;sudo gem update"
# ":" is read as "%" or "/" and is bad for makefile variables:
#alias brew-tend "brew upgrade --all ; brew update;brew doctor;brew linkapps;brew prune;brew link openssl --force; brew cleanup -s"
#alias brew-tend "brew upgrade ; brew update;brew doctor;brew linkapps;brew prune;brew link openssl --force; brew cleanup -s"
#alias brew-tend "brew upgrade ; brew update;brew doctor;brew cask cleanup;brew link openssl --force; brew cleanup -s;brew prune"
#alias brew-tend "brew upgrade ; brew update;brew doctor;brew cleanup;brew link openssl --force; brew cleanup -s;brew prune"
# alias brew-tend "brew upgrade | tee /tmp/brew_upgrade_`datestr` ; brew update;brew doctor;brew cleanup;brew link openssl --force; brew cleanup -s;brew prune"
# alias q-brew-tend "brew update;brew doctor;brew cleanup;brew link openssl --force; brew cleanup -s;brew prune"
alias brew-tend "brew upgrade | tee /tmp/brew_upgrade_`datestr` ; brew update;doctor-link;brew cleanup;brew link openssl --force; brew cleanup -s"
alias q-brew-tend "brew update;brew doctor;brew cleanup;brew link openssl --force; brew cleanup -s"
alias pip-tend "pip install --upgrade distribute; pip install --upgrade pip;pips"
alias pip3-tend "pip3 install --upgrade distribute; pip3 install --upgrade pip3;pip3s"
#alias hask-tend "cabal update;  ghc-pkg check --simple-output"
alias hask-tend "cabal new-update;  ghc-pkg check --simple-output"
#alias conda-tend "/sw/anaconda/bin/conda update conda;conda update --prefix /sw/anaconda anaconda"
alias conda-tend "conda update conda;conda update --prefix /anaconda anaconda;conda clean -tipsy"
alias cabal-tend "cabal update"
#alias ogit "open 'https://github.com/chrishwiggins?tab=repositories'"
alias normalize "sed -f $mise/sed/normalize "
alias openjpgs "find . | grep -i -e 'jpg' -e 'jpeg' | normalize | xargs open"
alias cdc "pwd | normalize | pbcopy"
alias cdp 'cd `pbpaste`'
alias mise "open https://github.com/chrishwiggins/mise"
alias citibike open http://www.citibikenyc.com/stations

# spelling while typing is hard
alias plan plat
alias opne open
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
alias airport-util 'open /Applications/Utilities/AirPort\ Utility.app/'
alias els "echo 'For reasons explained in detail at http://bactra.org/weblog/864.html, I will not review for any Elsevier publication. I look forward to assisting your journal in the future, after it switches publishers.' | pbcopy"
alias duplist 'dupseek -f hn .'
alias hh history -h
alais grr g rstats
alias rstack "open 'http://stats.stackexchange.com/search?q=%5Br%5D+'"
#alias urls "asciify| fix | tr '<>[]()\ ' '\n' | grep -i 'http'| sed -e 's/[,.]\$//'"
#alias urls "asciify| fix | tr '<>[]()\ ' '\n' | grep -i 'http'| sed -e 's/[,.]$//'"
#alias urls "asciify| fix | tr ';<>[]()\ ' '\n' | grep -i 'http'"
alias urls "asciify| fix | tr '{};<>[]()\ ' '\n' | grep -i 'http'"
alias pbmunpack "mkdir mail-dump ;pbpaste | munpack -t -f -C mail-dump"
alias deck "open /Applications/TweetDeck.app/;awk '/Keyboard shortcuts/,/   Related articles:/' < $cwhome/Documents/Help/TweetDeck/20170322.txt"
alias deck onion
#alias otb fox http://www.onetimebox.org/
alias sql "mysql.server start;mysql -uroot;mysql.server stop"
#alias sheet "open https://docs.google.com/spreadsheet/"
alias sheet "open http://sheet.new"

#phone aliases
alias call "echo \!* >> $phonefile"
alias ph "grep -i \!* $phonefile | tr '\' '\n'"
alias phone "vi + $phonefile"
alias mtg-no "grep -v '^%' ~/mise/aux/rp-decline.asc| pbcopy"
alias mtg-q "grep -v '^%' ~/mise/aux/rp-mtg.asc| pbcopy"

# LaTeX stuff
alias sty-install "sudo tlmgr update --self;sudo tlmgr install \!:*:t:r"
#alias plat "pdflatex \!:*:r ; bibtex \!:*:r ; pdflatex \!:*:r ; pdflatex \!:*:r ; grep Citation \!:*:r.log "
alias plat "pdflatex --shell-escape \!:*:r ; bibtex \!:*:r ; pdflatex --shell-escape \!:*:r ; pdflatex --shell-escape \!:*:r ; grep Citation \!:*:r.log "
alias lat "latex \!:*:r ; bibtex \!:*:r ; latex \!:*:r ; latex \!:*:r ; grep Citation \!:*:r.log;dvipdf \:*:r.dvi "
alias plath "pdflatex -halt-on-error \!:*:r ; bibtex \!:*:r ; pdflatex -halt-on-error \!:*:r ; pdflatex -halt-on-error \!:*:r "
alias platf "pdff \!:*:r ; bibtex \!:*:r ; pdff \!:*:r ; pdff \!:*:r ; grep Citation \!:*:r.log "
alias pdff pdflatex -interaction=nonstopmode

# more misc
alias manel "pbcopy < $mise/aux/manel.txt"
alias yeats "pbcopy < $mise/aux/yeats.txt"
alias takeout "open 'https://takeout.google.com/settings/takeout'"
alias oct ocr
alias profile py3 -m cProfile
alias atom open /Applications/Atom.app/
alias eee "echo 'Do you know your estimated time of arrival?'|pbcopy"
alias zork echo back to work, you.
alias asciify "/usr/bin/perl -pe 's/[^[:ascii:]]/+/g'"
alias asciify-clean "/usr/bin/perl -pe 's/[^[:ascii:]]//g'"
alias bow "asciify | fix | lower | words | nodud | sort -bfd | uniq -c | sort -nr"
alias newdoc "open https://docs.google.com/document/"
#alias addy "open /Applications/Address\ Book.app/"
alias addy "open /Applications/Contacts.app/"
alias skindle "open -a /Applications/Send\ to\ Kindle/Send\ to\ Kindle.app/ \!:*"
alias mute-fix sudo killall coreaudiod
alias bs "curl -silent http://www.wisdomofchopra.com/iframe.php | grep 'og:description' | cut -d\' -f2"
#alias muttf "cat /dev/null | mutt -H \!:*"
alias omail "open mailto:\!*"
#alias mail "mutt \!*"
alias pb2gist gist -o -P

alias pocket "pbpaste | mutt -s '\!:* @`date +%yy%mm%dd_%Hh%Mm%Ss`' add@getpocket.com"
alias ttweather "lynx -nolist -width=1000 -dump 'http://www.freeweather.com/cgi-bin/weather/weather.cgi?daysonly=0&maxdays=11&zipcode=10027' | asciify | fix | awk '/^Daily/,/^Sunset/'"
alias omail open /Applications/Mail.app/
alias olede open https://github.com/ledeprogram/courses/tree/master/algorithms
#alias mypy /usr/bin/python
#alias mbo "skype; boxes ; voice ; ichat; focus;telegram;slack;DECK"
#alias mbo "skype; boxes ; voice ; ichat; telegram;slack;DECK;focus"
# alias mbo "iboxes; ichat; voice"
#alias mbo "signal;nyt-hang;ghang;nytcal;boxes;ichat;voice;slack;f"
alias mbo "signal;nyt-hang;ghang;nytcal;boxes;ichat;voice;slack;f;open /Applications/Keybase.app"
alias md2pdf "pandoc --number-sections \!:1 -s -o \!:1:r.pdf"
alias md2htm "pandoc \!:1 -s -o \!:1:r.htm"
#alias clio "fox 'http://clio.cul.columbia.edu'"
#alias roi "open -a /Applications/iTunes.app/ ~/Music/iTunes/iTunes\ Media/Music/The\ Breeders/LSXX/1-05\ Roi.m4a;osascript -e 'tell application '"'"'iTunes'"'"' to set song repeat to one'"
#alias roi "open -a /Applica!tions/iTunes.app/ ~/Music/iTunes/iTunes\ Media/Music/The\ Breeders/LSXX/1-05\ Roi.m4a;osascript -e 'tell application iTunes to set song repeat to one'"
alias roi "open -a /Applications/iTunes.app/ ~/Music/iTunes/iTunes\ Media/Music/The\ Breeders/LSXX/1-05\ Roi.m4a;$mise/osa/replay"
alias beet "open ~//Music/iTunes/iTunes\ Media/Music/Compilations/7\ Conductors\ vs.\ Beethoven\'s\ 7th/06\ Symphony\ No.\ 7\ in\ A\ Major,\ Op.\ 92_\ II.\ Allegretto.m4a"
alias pbpate pbpaste
#alias acal fox http://registrar.columbia.edu/calendar
alias acal "open 'https://www.registrar.columbia.edu/event/academic-calendar?acfy=48&acterm=7&acschool=All&keys=&field_event_type1_tid%5B%5D=21&field_event_type1_tid%5B%5D=22&field_event_type1_tid%5B%5D=23'"
#alias omutts "cd $odir;mutts;cd -"
#big sur killed this, now an osascript: alias lock "/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend"
#alias zip4 open http://zip4.usps.com/zip4/welcome.jsp
#alias zip4 "open 'https://tools.usps.com/go/ZipLookupAction'!'input.action?mode=0&refresh=true'"
#alias zip4 "open 'https://tools.usps.com/zip-code-lookup.htm?byaddress'"
# alias rest sudo shutdown -s now
alias rest pmset sleepnow
#alias oed "fox 'http://www.columbia.edu/cgi-bin/cul/resolve?AKV9469'"
alias oed "c-cu https://resolver.library.columbia.edu/AKV9469"
alias sheets "open 'https://drive.google.com/drive/u/0/#search?q=type%3Aspreadsheet'"

alias kreps "echo 'https://twitter.com/jaykreps/status/219977241839411200' | pbcopy "
alias pbstrip "pbpaste|asciify|estrip|pbcopy"
alias reline "tr '\n' ' ' | tr '+' '\n' | fix "
alias ngit "open https://github.com/new"
alias wiktionary open "https://en.wiktionary.org/wiki/\!:*"
#alias cwnotes "head `ls -1t $ndir/cwnote_201* | grep -v -e '(' -e ')'` | more"
#alias cwnotes 'head `ls -1t $ndir/cwnote_201* | normalize` | more'
#alias cwnotes 'head `ls -1t $ndir/cwnote_2023_*T*_*_*.md | normalize` | more'
#alias cwnotes 'head `ls -1t $ndir/cwnote_2024_*T*_*_*.md | normalize` | more'
#alias cwnotes 'head `ls -1t $ndir/cwnote_2025_*T*_*_*.md | normalize` | more'
alias cwnotes 'head `ls -1t $ndir/cwnote_2026_*T*_*_*.md | normalize` | more'


alias no-wiml "cat $mise/aux/no-wiml.txt $setup/aux/wiml.tsv | pbcopy"
alias rand 'echo `jot -r 1 0 1000`/1000 | bc -l| cut -c 1-4'
#alias vi-null vim -u NONE
alias vi-null "vi -c 'set nonumber' -c 'set list!'"


# good fu: exploits quick add but adds browser to edit event, send invitesjj
# barfing 2019-07-21, chrome nonresponsive
#alias oslow 'pers-gmail-browser `slow \!:* | tr '"'"' '"'"' '"'"'\n'"'"' | grep ^http`'
alias oslow 'pers-gmail-browser  `slow \!:* | tr '"'"' '"'"' '"'"'\n'"'"' | grep ^http`'
alias remake 'vi makefile'
alias polls "lynx -dump 'http://projects.fivethirtyeight.com/2016-election-forecast/?ex_cid=rrpromo#plus' | grep -A 2 'Hillary Clinton' | more | head -3 | grep '%'; lynx -dump 'http://www.nytimes.com/interactive/2016/upshot/presidential-polls-forecast.html' | more | grep Clinton | grep 'chance to win'"
#alias polls "lynx -dump 'http://www.nytimes.com/interactive/2016/upshot/presidential-polls-forecast.html' | more | grep Clinton | grep 'chance to win'"


# alias pycharm open /Applications/PyCharm.app/
alias lower "tr '[A-Z]' '[a-z]'"
alias upper "tr '[a-z]' '[A-Z]'"
alias refine open /Applications/OpenRefine.app/

# aliases for PPF class
alias des "echo Alain Desrosières"
alias pbdes "echo Desrosières|pbcopy"
alias ppf-server open http://104.196.215.242:8000 
alias ppf-server open http://data-ppf.dsi.columbia.edu:8000

# misc google fu
alias ndoc "open 'https://docs.google.com/document/u/0/create?usp=docs_home&ths=true'"
alias cdoc "chrome 'https://docs.google.com/document/u/0/create?usp=docs_home&ths=true'"

# uke tuning via sox:
alias smile open https://smile.amazon.com/
alias unxml plutil -convert xml1
alias pdfmerge "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=pdfmerge-out.pdf \!:*"
#alias fmail 'setenv fmail `lynxx -nolist -dump https://maildrop.cc/ | grep @maildrop.cc`;echo $fmail|pbcopy'
#alias fmail-open 'open https://maildrop.cc/inbox/`echo $fmail|cut -d@ -f1`'

alias drive "open /Applications/Backup\ and\ Sync.app/"
alias mlok mlook
alias toro open -a /Applications/TorBrowser.app/
alias prand "python3 -c 'import random;print(random.randint(0,99))'"
alias conda-nav open ~//anaconda3/Anaconda-Navigator.app
#alias nb ~//anaconda3/bin/jupyter_mac.command
alias nb c-irl https://notebooklm.google.com/
alias htm2pdf '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --print-to-pdf '
alias htm2png '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --disable-gpu --screenshot '
alias salganik open http://www.bitbybitbook.com/en/ethics/
#alias teen "seq 1 \!:1 | awk '{print \"i was like\"}' | tr '\n' ' ' | say"
alias undos "tr '\r' '\n'"
alias gpgp 'git pull; git push'
alias nuzz open http://nuzzel.com/
alias leaf fox https://v2.overleaf.com/project
alias txt2aiff-quick 'say -v Jamie -r 270 -f \!:1 -o \!:1.aiff'
alias txt2aiff 'say -v Jamie -r 200 -f \!:1 -o \!:1.aiff'
alias txt2m4a 'say -v Jamie -r 200 -f \!:1 -o \!:1:r.m4a'
alias txt2m4a-quick 'say -v Jamie -r 270 -f \!:1 -o \!:1:r.m4a'
alias remkae make
alias remkae make
alias weahter weather
alias weahter weather
alias porfa sudo
alias pcbopy pbcopy
alias aaias alias
alias aaias aalias
alias doccs docs
#alias books gbook
#alias ogit-here open `grep github.com .git/config | sed -e 's/\:/\//' -e 's/url = git@/http:\/\//' -e 's/\.git[ ]*$//'`

# things using gm which i changed to gg 20180708
alias att gg has:attachment
alias frm "gg from:\!*"
alias to "gg to:\!*"

# cu library
#alias clio "open 'http://www.columbia.edu/cgi-bin/cul/resolve?AMS3996'"
#alias clio "open 'https://library.columbia.edu/'"

alias amzn "gsearch  site:amazon.com \!*"
alias amazon "gsearch  site:worldcat.org \!*"
alias juice open /System/Library/PreferencePanes/EnergySaver.prefPane/
alias sbe 'cat /dev/null | mutt \!:1 -a \!:2 -s \!:3'
alias pdf2pdf 'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile=output.pdf '
alias outline 'grep -v ^%%% \!:1 >! /tmp/pandoc_tmp_$$ ; pandoc --number-sections /tmp/pandoc_tmp_$$ -o \!:1:r.pdf'
alias toc 'grep -v ^%%% \!:1 >! /tmp/pandoc_tmp_$$ ; pandoc --number-sections --table-of-contents /tmp/pandoc_tmp_$$ -o \!:1:r.pdf'
alias toc 'grep -v ^%%% \!:1 >! /tmp/pandoc_tmp_$$ ; pandoc -V colorlinks=true -V linkcolor=blue -V urlcolor=red -V toccolor=gray --number-sections --table-of-contents /tmp/pandoc_tmp_$$ -o \!:1:r.pdf'
alias beamer  'grep -v ^%%% \!:1 >! /tmp/pandoc_tmp_$$ ; pandoc --slide-level 2 -i -t beamer --number-sections /tmp/pandoc_tmp_$$ -o \!:1:r.pdf'
alias stash   "mkdir stash_`date +%Y-%m-%dT%Hh%Mm`;mv -i * stash_`date +%Y-%m-%dT%Hh%Mm`"
alias stash-f "mkdir stash_`date +%Y-%m-%dT%Hh%Mm`;mv -f * stash_`date +%Y-%m-%dT%Hh%Mm`"

# quotes i reference lot
alias jcm "echo '-Excuse me. I invented the term artificial intelligence. I invented it because ...we were trying to get money for a summer study in 1956...aimed at the long term goal of achieving human-level intelligence.'; open 'https://youtu.be/pyU9pm1hmYs?t=160'"
alias hamming 'pbcopy < $science/Advising/Ideas/Hamming/hamming-you-and-your-research.txt '
alias teams 'pbcopy < $science/Advising/Ideas/Teams/teams.txt '

# weird languages
# add commodore basic
alias logo open /Applications/ACSLogo.app/
alias basic cbmbasic
# weird stuff to type
alias shrug "echo '¯\_(ツ)_/¯' | pbcopy"
alias thus "echo ∴|pbcopy"
alias tm "echo '™' | pbcopy"
alias num "awk -f $mise/awk/num.awk"
alias best "echo 'The best lack all conviction, while the worst Are full of passionate intensity.'| pbcopy"


alias statsort 'stat -f "%Sm %N" -t "%Y-%m-%dT%H:%M:%S" * | sort'
alias findbig "find . -type f -size +1000000 -exec ls -lh {}\;"
alias rmold "find . -type f -mtime +100 -exec rm {} +"
alias countbig "find . -type f -size 10000 | wc -l"
alias eng 'grep -w -f /usr/share/dict/words'
alias tft "curl --silent 'http://itsthisforthat.com/api.php?text';echo"
alias fiddle "echo GG ; play -q  -n synth 1 sin 196.00; echo DD ; play -q  -n synth 1 sin 293.66; echo AA ; play -q  -n synth 1 sin 440.00; echo EE ; play -q  -n synth 1 sin 659.26"
alias fleas "play -q  -n synth 1 sin 783.99; play -q  -n synth 1 sin 523.25; play -q  -n synth 1 sin 659.25; play -q  -n synth 1 sin 880.00"
alias oldmutt "brew unlink mutt;brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/0e1d197da9d9a1d4cc321e91149a2f3431e39d8c/Formula/mutt.rb;brew link mutt"
alias vs "open /Applications/Visual\ Studio\ Code.app/"
alias py3 ~/anaconda3/bin/python3
alias gpy3 google python3
alias gpy3 g python3
alias gpy3 g +python 3+
alias gvs g +visual studio+ OR vscode

#alias nytrss "curl http://www.nytimes.com/services/xml/rss/nyt/GlobalHome.xml | grep -A 1 title"
alias nytrss "curl --silent https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml | grep -A 1 title"
#alias g0 py3 /usr/local/bin/googler
alias g0 googler
alias g1 "open https://www.google.com/imghp?sout=1"
alias linter pylint -d W0311 -d R0913 -d C0116 -d W0621 -d C0103
alias irl-text "echo 'Meeting in person preferred; if not convenient, we could meet via Google Hangouts; if also not convenient, we could talk by phone. Please do let me know!'|pbcopy"
alias gift "pbcopy < $mise/aux/gift.txt"

alias vin "vi -c 'set nonumber'"
alias oopen open
alias kdir mkdir
alias spotify open /Applications/Spotify.app/
alias uppu upup
alias rmdur rmdir
alias blue-off blueutil -p 0
alias blue-on blueutil -p 1
alias ft open https://www.ft.com/coronavirus-latest
alias spot spotify
alias oopen open
alias kdir mkdir
alias spotify open /Applications/Spotify.app/
alias docxdump "cp \!:1 /tmp/input.docx ; qlmanage -p /tmp/input.docx -o /tmp ; lynx -dump -hiddenlinks=ignore -image_links=no -minimal -nobold -nolist -pseudo_inlines -force_html /tmp/input.docx.qlpreview/Preview.html | /usr/bin/perl -pe 's/[^[:ascii:]]/+/g' "
alias docxdump-o "cp \!:1 /tmp/input.docx ; qlmanage -p /tmp/input.docx -o /tmp ; lynx -dump -hiddenlinks=ignore -image_links=no -minimal -nobold -nolist -pseudo_inlines -force_html /tmp/input.docx.qlpreview/Preview.html | /usr/bin/perl -pe 's/[^[:ascii:]]/+/g' > \!:1:r.asc "
alias port-tend "sudo port selfupdate;sudo port upgrade outdated"

# h/t @josephoenix
alias tool-crypto "sudo install_name_tool -change \!:1 /usr/local/Cellar/openssl@1.1/1.1.1h/lib/libcrypto.1.1.dylib \!:2"
alias tool-ssl    "sudo install_name_tool -change \!:1 /usr/local/Cellar/openssl@1.1/1.1.1h/lib/libssl.1.1.dylib    \!:2"
alias tables "echo (┛ಠ_ಠ)┛彡┻━┻ | pbcopy"
alias fly "open 'https://www.youtube.com/watch?v=maNe-tCqrJ8'"
alias next "shuf ~/mise/doc/strategies.txt | head -1"
alias hunters "echo 'We are not open to utilizing agency support for this or any other Data Science role at this time. Thank you for reaching out. '|pbcopy"
#alias txt open /Applications/TextEdit.app/
alias txt open /System/Applications/TextEdit.app
alias txtify "pbpaste|pbcopy"
alias prp "pbpaste|reply|pbcopy"
#alias ifind open -a safari https://www.icloud.com/#find
#alias ifind open /System/Applications/FindMy.app/
alias curse "grep -v -e '^#' ~/mise/doc/curses.txt | sed -e 's/^- //' | /opt/homebrew/bin/shuf | head -1| tr '\\' '\n'"
#alias cu-covid https://covid19.columbia.edu/content/covid-19-testing-program-fall-2021
#alias cu-covid http://secure.health.columbia.edu/
#alias cu-covid https://secure.health.columbia.edu/confirm.aspx
#alias cu-covid https://secure.health.columbia.edu/home.aspx
#alias cu-covid https://secure.health.columbia.edu/appointments_home.aspx
#alias cu-covid https://secure.health.columbia.edu/appointments_home.aspx
alias cu-covid open https://secure.health.columbia.edu/branch.aspx

alias leads lds
alias forward "echo 'Great! Could you write a forwardable intro email ( cf., e.g., https://www.entrepreneur.com/article/247692 ) to get things started?' | pbcopy"
alias dephone "open 'https://support.google.com/websearch/troubleshooter/9685456'"
alias table "echo '(╯°□°)╯︵ ┻━┻'|pbcopy"
alias wifis "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s; echo 'lower (more negative) value indicates a weaker signal and a higher (less negative) value indicates a stronger signal'"
alias d20 "shuf -i 1-20 -n 1"
alias pst "env TZ=':America/Los_Angeles' date"

alias canceling "echo 'I am fine with canceling this meeting. Thank you.'| pbcopy"


alias minors open "https://bulletin.engineering.columbia.edu/minor-applied-mathematics"
alias majors open "https://bulletin.engineering.columbia.edu/undergraduate-degree-tracks"

alias croncheck "cat /tmp/cron_test.log;grep CRON /var/log/syslog"
alias pbpy "pbpaste >! /tmp/$$.py ; wc -w /tmp/$$.py; py3  /tmp/$$.py"
alias pbtex echo i think you mean pblat
alias pbR "pbpaste >! /tmp/$$.py ; wc -w /tmp/$$.py; R -f /tmp/$$.py"
alias pblat "pbpaste >! /tmp/$$.tex ; wc -w /tmp/$$.tex; pdflatex /tmp/$$.tex; open $$.pdf"
alias pbtoc "pbpaste | ununi >! /tmp/$$.md ; toc /tmp/$$.md ; open /tmp/$$.pdf"
alias pbmpl "pbpaste >! /tmp/$$.mpl ; wc -w /tmp/$$.mpl ; maple  /tmp/$$.mpl"
alias mute 'osascript -e "set volume output muted true"'
alias hamlet open https://www.litcharts.com/shakescleare/shakespeare-translations/hamlet/act-1-scene-1
alias newer 'find . -type f -newermt "\!:1"'
alias yt-xcript yt-dlp --write-auto-sub --skip-download
alias yt-mp3 'yt-dlp -x --audio-format mp3 -o "youtube_audio.%(ext)s"'
alias yt-mp4 "yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' "
alias yt-video 'yt-dlp -o "%(title)s.%(ext)s"'
#alias sniff "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
alias plan "echo 'dream in years; plan in months; evaluate in weeks; ship daily'"
alias nato "echo 'Alfa|Bravo|Charlie|Delta|Echo|Foxtrot|Golf|Hotel|India|Juliett|Kilo|Lima|Mike|November|Oscar|Papa|Quebec|Romeo|Sierra|Tango|Uniform|Victor|Whiskey|Xray|Yankee|Zulu'|tr '|' '\n'"
alias embiggen "osascript  $mise/osa/embiggen.osa"
alias cd-f cd-parent
alias md5 "echo i think you mean shasum -a 512"
# flare: moved to aliases-private.sh (uses seiton setbrightness binary)
#alias flare 'osascript -e "tell application \"System Events\"" -e "repeat 16 times" -e "key code 144" -e "end repeat" -e "end tell"'
alias code 'open -a "Visual Studio Code" \!*'    # macOS
alias vs 'code $PWD \!*'    # macOS/Linux
alias stats "c-cu https://www-statista-com.ezproxy.cul.columbia.edu/;open https://ourworldindata.org/"
# lit, dim, blaze: moved to aliases-private.sh (uses seiton setbrightness binary)
#alias lit 'osascript -e '\''tell application "System Events" to key code 144'\'''
#alias dim 'osascript -e '\''tell application "System Events" to key code 145'\'''
#alias blaze 'osascript -e '\''tell application "System Events"'\'' -e '\''repeat 16 times'\'' -e '\''key code 144'\'' -e '\''end repeat'\'' -e '\''end tell'\'''
alias cd-parent 'cd `dirname \!:1`'
alias tim "echo https://snyder.substack.com/p/on-tyranny | pbcopy"
alias usenix "echo https://www.youtube.com/watch?v=ajGX7odA87k | pbcopy"
alias stripdf 'exiftool -all= \!:1 -o stripped.pdf; qpdf --linearize stripped.pdf \!:2'
alias dsi-dir "echo 'in 428 mudd (in the DSI (in Mudd (to the right of Blue Java (behind some glass doors))))'|pbcopy"
#alias countdown 'set seconds = `date -j -f "%Y-%m-%d" "\!:1" "+%s"`; @ days = ( $seconds - `date "+%s"` ) / 86400; echo $days days until \!:1'
alias ununi sed -f /Users/wiggins/mise/sed/ununicode.sed
alias gitlog "echo 'write a human-readable commit message of sufficient detail that future developers will understand what was changed and updated and the current state of the repo' | pbcopy"
alias gitpush "echo 'push to github with a human-readable commit message of sufficient detail that future developers will understand what was changed and updated and the current state of the repo' | pbcopy"
#alias claudepaste 'set tmpfile="/tmp/claude_`date +%Y%m%d_%H%M%S`_$$.txt" && pbpaste > $tmpfile && claude $tmpfile && rm -f $tmpfile'¶
alias pbclaude 'set tmpfile="/tmp/claude_`date +%Y%m%d_%H%M%S`_$$.txt" && pbpaste > $tmpfile && claude $tmpfile'¶
alias liar 'date >> ~/youreabsolutelyright.txt; pbpaste >> ~/youreabsolutelyright.txt; echo "====" >> ~/youreabsolutelyright.txt'
alias nolie "echo 'no fraud, no placeholder code, no mock code, no random simulated code, only real code that works perfectly for the specified task' | pbcopy"
alias hideme-start 'scutil --nc start "hide.me VPN (Wireguard)"'
alias hideme-stop 'scutil --nc stop "hide.me VPN (Wireguard)"'
alias hideme-status 'scutil --nc status "hide.me VPN (Wireguard)"'
alias hideme-check 'scutil --nc status "hide.me VPN (Wireguard)" | head -1'

umask 022

# cw-specific aliases
# source  ~/mise/sh/aliases-public.sh"
set paliases=~/mise/sh/aliases-public.sh

# deleting /usr/local/bin, demoting to cwlogin file 
# alias cset "set path = ( $path /usr/local/bin ~//Documents/Scripts/perl ~//Documents/Scripts/osa ~//Documents/Scripts/sh/csh ~//bin /opt/local/bin /usr/local/mysql/bin /opt/local/libexec/gnubin    /usr/local/sbin ~/mise/* /usr/local/Cellar/ruby/1.9.3-p194/bin /usr/local/bin )"
#alias cset "set path = ( $path ~//Documents/Scripts/perl ~//Documents/Scripts/osa ~//Documents/Scripts/sh/csh ~//bin /opt/local/bin /usr/local/mysql/bin /opt/local/libexec/gnubin    /usr/local/sbin ~/mise/*/* /usr/local/Cellar/ruby/1.9.3-p194/bin )"
# postpending 2 for macports 2020-06-08
alias cset "set path = ( $path ~//Documents/Scripts/perl ~//Documents/Scripts/osa ~//Documents/Scripts/sh/csh ~//bin /opt/local/bin /usr/local/mysql/bin /opt/local/libexec/gnubin    /usr/local/sbin ~/mise/*/* /usr/local/Cellar/ruby/1.9.3-p194/bin /opt/local/bin /opt/local/sbin )"

# set some variables
setenv EDITOR /usr/bin/vi
setenv HOMEBREW_TEMP /usr/local/Cellar
#setenv DYLD_INSERT_LIBRARIES /usr/local/lib/libvecLibFortI.dylib 
set savehist=1000

# prompt
#set prompt="%n-%m{%c1}%\!: "
#set prompt="@carr2n:'do the work'{%c1}%\!: "
#set prompt='adapt{%c1}%\!: '
#set prompt="carr2n:'do the work'{%c1}%\!: "

# from https://www.cs.umd.edu/~srhuang/teaching/code_snippets/prompt_color.tcsh.html
# set     red="%{\033[1;31m%}"
# set   green="%{\033[0;32m%}"
# set  yellow="%{\033[1;33m%}"
# set    blue="%{\033[1;34m%}"
# set magenta="%{\033[1;35m%}"
# set    cyan="%{\033[1;36m%}"
# set   white="%{\033[0;37m%}"
# set     end="%{\033[0m%}" # This is needed at the end... :(
# set prompt="${green}%P${blue}{%c}${white}%h${end}: "

#set prompt="@%P{%S%c%s}%U%h%u: "
#set ellipsis
set prompt="@%P{%S%c2%s}%U%h%u: "


# Don't overwrite existing files with the redirection character ">"
set noclobber

# actually do stuff
## set path
#% echo path
cset

### TEXSTUFF
# Add /usr/local/texlive/2011/texmf/doc/man to MANPATH, if not dynamically determined.
# set manpath = ( $manpath /usr/local/texlive/2011/texmf/doc/man )
set manpath = ( /usr/local/texlive/2011/texmf/doc/man )
# Add /usr/local/texlive/2011/texmf/doc/info to INFOPATH.
#set infopath = ( $infopath /usr/local/texlive/2011/texmf/doc/info )
set infopath = ( /usr/local/texlive/2011/texmf/doc/info )
#  Most importantly, add /usr/local/texlive/2011/bin/universal-darwin
#  to your PATH for current and future sessions.
set path = ( $path /usr/local/texlive/2011/bin/universal-darwin )
# CWADD: add /usr/texbin, mise
set path = ( $path /usr/texbin  )
# CWADD: i like it here
set path = ( $path . )
# CWADD: add some google
set path = ( $path ~/google-cloud-sdk/bin )

## learn my aliases
# learn
#% echo aliases
source $paliases

# remap capslock to esc:
# h/t https://stackoverflow.com/questions/127591/using-caps-lock-as-esc-in-mac-os-x

hidutil property --set '{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x700000039,"HIDKeyboardModifierMappingDst":0x700000029}]}' > /dev/null

# delete after jan 20 2021
#curl --silent 'https://days.to/until/us-presidential-inauguration' | grep 'until US Presidential Inauguration' | grep 'There are' | cut -d\> -f2 | cut -c1-7

# generate random curse
#echo curses...
shuf ~/mise/doc/curses.txt | head -1
#echo ...curses

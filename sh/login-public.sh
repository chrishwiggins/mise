umask 022

# cw-specific aliases
alias learn "source $cwaliases; source  ~/mise/sh/aliases-public.sh"
alias cset "set path = ( /usr/local/bin ~//Documents/Scripts/perl ~//Documents/Scripts/osa ~//Documents/Scripts/sh/csh ~//bin /opt/local/bin /usr/local/mysql/bin $path /opt/local/libexec/gnubin    /usr/local/sbin ~/mise/* /usr/local/Cellar/ruby/1.9.3-p194/bin )"

# set some variables
setenv EDITOR /usr/bin/vi
setenv HOMEBREW_TEMP /usr/local/Cellar
set savehist=1000
set prompt="%n@%m{%c1}%\!: "

# Don't overwrite existing files with the redirection character ">"
set noclobber

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
# CWADD: add /usr/texbin
set path = ( $path /usr/texbin )

# CWADD: i like it here.
set path = ( $path . )

# actually do stuff
## set path
cset
## learn my aliases
learn

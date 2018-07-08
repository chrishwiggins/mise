umask 022

# cw-specific aliases
# source  ~/mise/sh/aliases-public.sh"
set paliases=~/mise/sh/aliases-public.sh

# deleting /usr/local/bin, demoting to cwlogin file 
# alias cset "set path = ( $path /usr/local/bin ~//Documents/Scripts/perl ~//Documents/Scripts/osa ~//Documents/Scripts/sh/csh ~//bin /opt/local/bin /usr/local/mysql/bin /opt/local/libexec/gnubin    /usr/local/sbin ~/mise/* /usr/local/Cellar/ruby/1.9.3-p194/bin /usr/local/bin )"
alias cset "set path = ( $path ~//Documents/Scripts/perl ~//Documents/Scripts/osa ~//Documents/Scripts/sh/csh ~//bin /opt/local/bin /usr/local/mysql/bin /opt/local/libexec/gnubin    /usr/local/sbin ~/mise/*/* /usr/local/Cellar/ruby/1.9.3-p194/bin )"

# set some variables
setenv EDITOR /usr/bin/vi
setenv HOMEBREW_TEMP /usr/local/Cellar
#setenv DYLD_INSERT_LIBRARIES /usr/local/lib/libvecLibFortI.dylib 
set savehist=1000
set prompt="%n@%m{%c1}%\!: "

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

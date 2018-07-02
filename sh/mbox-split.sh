perl -pe 'open STDOUT, sprintf(">m%05d.mbx", ++$n) if /^From /' < $* > before-first

# Bash/Zsh completion for gmails
# Source this file: . ~/mise/bash/gmails-completion.bash

_gmails() {
    local cur prev modes flags
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    modes="send draft reply fwd trash archive open thread"
    flags="-n -q -F -e -E -Q -S -t -c -h -s -H -a -b --all --draft --count --query --config --email --list-accounts --show-account --stdout --text --just-count --help --subject --header-file --attach --bcc"

    # Complete modes if first arg or after flags
    if [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W "$flags" -- "$cur"))
    else
        # Check if a mode word already appears
        local has_mode=0
        for word in "${COMP_WORDS[@]}"; do
            case "$word" in
                send|draft|reply|fwd|trash|archive|open|thread) has_mode=1 ;;
            esac
        done
        if [[ $has_mode -eq 0 ]]; then
            COMPREPLY=($(compgen -W "$modes" -- "$cur"))
        else
            # After mode, complete files for relevant flags
            case "$prev" in
                -F|--config|-H|--header-file|-a|--attach)
                    COMPREPLY=($(compgen -f -- "$cur")) ;;
            esac
        fi
    fi
}

complete -o default -F _gmails gmails

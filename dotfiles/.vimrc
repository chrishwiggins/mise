" Switch syntax highlighting on, when the terminal has colors
" Also switch on highlighting the last used search pattern.
if &t_Co > 2 || has("gui_running")
 syntax on
 set hlsearch
endif
" causes problems on pasting:
" set smartindent
set tabstop=2
" for '>', e.g., set shiftwidth=4
set shiftwidth=2
" causes problems with makefiles:
set expandtab
filetype plugin on 
":let b:col=substitute(b:col, ',', ';', 'g') 
"use docx2txt.pl to allow VIm to view the text content of a .docx file directly.
autocmd BufReadPre *.docx set ro
autocmd BufReadPost *.docx %!docx2txt.pl 

" show line #s
set number

" from https://github.com/tpope/vim-markdown
autocmd BufNewFile,BufReadPost *.md set filetype=markdown
let g:markdown_fenced_languages = ['html', 'python', 'bash=sh']


" cwstuff
set ic 

" fzf suggests adding:
set rtp+=/usr/local/opt/fzf


" paste from rando stack page
" On pressing tab, insert 2 spaces
set expandtab
" show existing tab with 2 spaces width
set tabstop=2
set softtabstop=2
" when indenting with '>', use 2 spaces width
set shiftwidth=2

" 2024-01-02T10h55 enable spell
set spell
set spelllang=en

" 2024-01-05 shut up
:set noerrorbells
:set visualbell


" from http://vimcasts.org/episodes/soft-wrapping-text/
" command! -nargs=* Wrap set wrap linebreak nolist
set wrap linebreak nolist
" https://vim.fandom.com/wiki/Automatic_word_wrapping

" 20240115T08h00 set noic
:set noic
 
" 20231204T15h49 copilot
autocmd BufEnter *.py Copilot enable
autocmd BufEnter *.txt Copilot enable
autocmd BufEnter *.md Copilot enable
" 20231219T07h01 copilot
command! Pilot :Copilot enable
command! Unpilot :Copilot disable
command! Ideas :Copilot panel
command! Status :Copilot status  
command! Nosnoop :Copilot disable
command! Nocreep :Copilot disable


" Autostart GitHub Copilot for Python and Markdown files
autocmd BufEnter,BufRead,BufNewFile *.py :Copilot enable
autocmd BufEnter,BufRead,BufNewFile *.txt :Copilot enable
" creepy autocmd BufEnter,BufRead,BufNewFile *.md :Copilot enable
"

" 20240412T04h35 no spell for python
autocmd FileType python setlocal nospell

" make it easier to see trailing whitespace
set listchars=tab:>-,nbsp:_,trail:·,extends:>,precedes:<,eol:¶
set list

" I like to see the ruler, so I can see where I am in the file.
set ruler

" 20260217 never write DOS line endings
set fileformat=unix
set fileformats=unix,dos
autocmd BufWritePre * set fileformat=unix

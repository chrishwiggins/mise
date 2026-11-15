# curse.awk: print one random line of curses.txt (used by the `curse` alias).
# Skips '#' comment lines, strips a leading "- ", and turns each backslash
# into a newline, exactly what the old grep|sed|shuf|head|tr pipeline did
# but in one process (each fork costs ~0.1s at shell login).
# Usage: awk -f ~/mise/aux/curse.awk ~/mise/aux/curses.txt
BEGIN { srand() }
/^#/ { next }
{ sub(/^- /, ""); line[n++] = $0 }
END {
    if (n == 0) exit 1
    s = line[int(rand() * n)]
    gsub(/\\/, "\n", s)
    print s
}

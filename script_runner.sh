#!/usr/bin/env bash

COMMAND="$1"

osascript << EOF
tell application "Terminal"
    activate
end tell
tell application "System Events"
    keystroke "t" using command down
    set textToType to "cd /Users/riadizur/project/Pemilu_2024 && nohup python3 -m getData_onlocal.py ${COMMAND} db => process.log && exit;\n"
    keystroke textToType
end tell
EOF

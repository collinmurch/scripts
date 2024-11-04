#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title new uuid
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🪪

# Documentation:
# @raycast.description copy a new uuid
# @raycast.author collin murch
# @raycast.authorURL https://collinmurch.com

uuidgen | tr -d '\n' | tee >(pbcopy)

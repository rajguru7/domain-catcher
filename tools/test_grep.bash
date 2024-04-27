#!/usr/bin/env bash

grep -R -o -P "https?://[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|\/))" "$1"



# \bhttps?:\/\/[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|\/))

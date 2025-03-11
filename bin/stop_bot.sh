#!/bin/bash

prog_path=/usr/bot/pmd_food_diary_bot
cd $prog_path
source $prog_path/venv/bin/activate

pid=$(cat pid.nohup)
kill -9 $pid

echo killed $pid
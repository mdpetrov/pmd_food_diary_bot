#!/bin/bash

prog_path=/usr/bot/pmd_food_diary_bot
cd $prog_path
source $prog_path/venv/bin/activate

bin/stop_bot.sh

sleep 1

bin/start_bot.sh
#!/bin/bash

echo "Reloading daemon"
systemctl daemon-reload
echo "Restarting espn-ffb.service"
systemctl restart espn-ffb.service
echo "Restarting espn-ffb-update.timer"
systemctl restart espn-ffb-update.timer
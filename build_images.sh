#!/bin/bash

docker build --platform linux/amd64 -t zhiyong/know-more-app ./ &
pid=$!

# 等待前一个命令执行完成
wait $pid

docker push zhiyong/know-more-app:latest

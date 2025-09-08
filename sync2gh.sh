#!/usr/bin/bash
# 
# 
UPDATE_BRANCH=action
export GIT_SSH_COMMAND="ssh -o IdentitiesOnly=yes -i key/deploy_key"
# git clone -b $UPDATE_BRANCH --depth 1 git@github.com:wiwari/wra-fhy.git
# git clone -b $UPDATE_BRANCH --depth 1 https://github.com/wiwari/wra-fhy.git
# cd wra-fhy
# git config --local user.name wiwari
# git config --local user.email 89345325+wiwari@users.noreply.github.com
# python3 -m venv .venv
# source .venv/bin/activate
git checkout $UPDATE_BRANCH
git reset
git checkout -- .
git pull
date '+%Y-%m-%d %H:%M %Z' | tee -a fetchdb.log 
python3 fetchdb.py --update
python3 fetchdb.py --stalist > data/active_stations.json
if [[ -n $(git status --porcelain data | grep "^ M ") ]]; then
    git add data/
    git add fetchdb.log
    git commit -m "fetch FHY at $(date '+%Y-%m-%d %H:%M')"
    git push origin $UPDATE_BRANCH
    echo "updates have been committed."
else
    echo "No updates to commit."
fi

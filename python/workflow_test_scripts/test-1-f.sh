## Test 1 - False scenario - Branch out from Development
## Make sure that development and production don't look at the same commit at the time of running this script
## Outcome: created branch is deleted by create_branch.yml

git checkout development
git pull --all
touch file.md
git add .
git log --oneline
git commit -m 'Make file.md - test-1'
git push origin development
git log --oneline
git checkout -b test-1
git push origin test-1
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# create_branch.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 1 ]
then echo "test-1: SUCCESS"
else echo "test-1: FAILURE"
fi

## Result: fatal: couldn't find remote ref test-1
#clean-up
git checkout production
git branch -D test-1

git checkout development
git pull --all
git reset --hard HEAD~1
git push -f origin development
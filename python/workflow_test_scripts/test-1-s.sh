## Test 1 - Successful scenario - Branch out from Production
## Outcome: created branch is valid

git checkout production
git pull --all
git checkout -b test-1
git push origin test-1
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# create_branch.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 1 ]
then echo "test-1: FAILURE"
else echo "test-1: SUCCESS"
fi

## Result: fatal: couldn't find remote ref test-1
#clean-up
git checkout production
git branch -D test-1
git push --delete origin test-1
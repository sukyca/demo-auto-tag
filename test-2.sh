## Test 2 - Open Pull Request
## Outcome: open pull request is created and checks have passed

git checkout production &> /dev/null
git pull --all &> /dev/null
git branch -D test-2 &> /dev/null
git push origin --delete test-2 &> /dev/null
git checkout -b test-2 &> /dev/null
git push origin test-2 &> /dev/null
gh pr create -B development -H test-2 --fill &> /dev/null
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status &> /dev/null
if [ $? = 0 ]
then echo "test-2: SUCCESS"
else echo "test-2: FAILURE"
fi
git checkout production
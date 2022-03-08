#test delete workflow - Successful scenario - user deletes branch that doesn't have any tags

git checkout production
git pull --all
git checkout -b test-4
touch file.md
git add .
git commit -m 'Make file.md - test-4'
git push origin test-4

git checkout production
git branch -D test-4
git push origin --delete test-4
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
gh run watch $RUN_ID --exit-status

if [ $? = 1 ]
then 
    echo "test-4: Delete workflow recreated the branch - Workflow is not working properly"
    echo "test-4: FAILURE"
    exit 1
else
    echo "test-4: Delete workflow deleted the branch - Workflow is working properly"
    echo "test-4: SUCCESS"
    exit 0
fi

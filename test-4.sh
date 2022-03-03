#test delete workflow

git checkout production
git pull --all
git checkout -b test-4
echo -e '\n' >> README.md
git add .
git commit -m "test-4"
git push origin test-4

gh pr create -B development -H test-4 --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-4: OPEN-PR (development) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status

    if [ $? = 0 ]
    then 
        echo "test-4: CLOSE-PR (development) SUCCESS"
    else
        echo "test-4: CLOSE-PR (development) FAIL"
        exit 1
    fi
else
    echo "test-4: OPEN-PR (development) FAILURE"
    exit 1
fi
git checkout production
git branch -D test-4
git push origin --delete test-4
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
gh run watch $RUN_ID --exit-status

if [ $? = 1 ]
then 
    echo "test-4: Delete workflow recreated branch - Workflow is working properly"
else
    echo "test-4: Delete workflow deleted branch - Workflow is not working properly"
    exit 1
fi
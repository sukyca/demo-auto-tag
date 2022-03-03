# test delete workflow 

# valid test 1-> create test-delete-workflow-branch, create a pull request to development
# allow merge to development, try to delete test-delete-workflow-branch - if test-delete-workflow-branch gets
# recreated then test is successfull

# valid test 2 -> create pull request to production
# allow merge to production, after merge is complete try to delete test-delete-workflow-branch
# if test-delete-workflow-branch is deleted the test is successfull

git checkout production
git pull --all
git branch -D test-delete-workflow-branch
git push origin --delete test-delete-workflow-branch
git checkout -b test-delete-workflow-branch
echo -e '\n' >> README.md
git add .
git commit -m "test-delete-workflow-branch"
git push origin test-delete-workflow-branch

gh pr create -B development -H test-delete-workflow-branch --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-delete-workflow-branch: OPEN-PR (development) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status

    if [ $? = 0 ]
    then 
        echo "test-delete-workflow-branch: CLOSE-PR (development) SUCCESS"
    else
        echo "test-delete-workflow-branch: CLOSE-PR (development) FAIL"
        exit 1
    fi
else
    echo "test-delete-workflow-branch: OPEN-PR (development) FAILURE"
    exit 1
fi

git branch -D test-delete-workflow-branch
git push origin --delete test-delete-workflow-branch
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
gh run watch $RUN_ID --exit-status

if [ $? = 1 ]
then 
    echo "test-delete-workflow-branch: Delete workflow recreated branch - Workflow is working properly"
else
    echo "test-delete-workflow-branch: Delete workflow deleted branch - Workflow is not working properly"
    exit 1
fi

gh pr create -B production -H test-delete-workflow-branch --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-delete-workflow-branch: OPEN-PR (production) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status

    if [ $? = 0 ]
    then 
        echo "test-delete-workflow-branch: CLOSE-PR (production) SUCCESS"
    else
        echo "test-delete-workflow-branch: CLOSE-PR (production) FAIL"
        exit 1
    fi
else
    echo "test-delete-workflow-branch: OPEN-PR (production) FAILURE"
    exit 1
fi

git branch -D test-delete-workflow-branch
git push origin --delete test-delete-workflow-branch
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-delete-workflow-branch: Delete workflow deleted branch - Workflow is working properly"
else
    echo "test-delete-workflow-branch: Delete workflow recreated branch - Workflow is not working properly"
    exit 1
fi
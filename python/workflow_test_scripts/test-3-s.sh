# test pr_closed - Successful scenario - pr_closed workflow deletes branches and tags in the end

git checkout production
git pull --all
git checkout -b test-3
touch file.md
git add .
git commit -m 'Make file.md - test-3'
git push origin test-3

gh pr create -B development -H test-3 --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-3: OPEN-PR (development) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status

    if [ $? = 0 ]
    then 
        echo "test-3: CLOSE-PR (development) SUCCESS"
    else
        echo "test-3: CLOSE-PR (development) FAIL"
        exit 1
    fi
else
    echo "test-3: OPEN-PR (development) FAILURE"
    exit 1
fi

gh pr create -B production -H test-3 --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-3: OPEN-PR (production) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status

    if [ $? = 0 ]
    then 
        echo "test-3: CLOSE-PR (production) SUCCESS"
        echo "test-3: SUCCESS"
    else
        echo "test-3: CLOSE-PR (production) FAIL"
        echo "test-3: FAILURE"
        exit 1
    fi
else
    echo "test-3: OPEN-PR (production) FAILURE"
    exit 1
fi

sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-3: Delete workflow deleted branch - pr_closed workflow is working properly"
    echo "test-3: SUCCESS"
else
    echo "test-3: Delete workflow recreated branch - pr_closed workflow is not working properly"
    echo "test-3: FAILURE"
    exit 1
fi

echo "cleaning up..."
git checkout production
git pull --all
git reset --hard HEAD~1
git push -f origin production

git branch -D test-3

git checkout development
git pull --all
git reset --hard HEAD~1
git push -f origin development

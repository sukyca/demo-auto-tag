## Test 2 - Successful scenario - Open Pull Request 
## Outcome: open pull request is created and checks have passed

git checkout production
git pull --all
git checkout -b test-2
touch file.md
git add .
git commit -m 'Make file.md - test-2'
git push origin test-2

gh pr create -B development -H test-2 --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-2: OPEN-PR (development) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status

    if [ $? = 0 ]
    then 
        echo "test-2: CLOSE-PR (development) SUCCESS"
    else 
        echo "test-2: CLOSE-PR (development) FAILURE"
        exit 1
    fi
else 
    echo "test-2: OPEN-PR (development) FAILURE"
    echo "test-2: FAILURE"
    exit 1
fi

git checkout production

gh pr create -B production -H test-2 --fill
PR_ID=$(gh pr list --limit 1 --json number | tr -dc '0-9')
sleep 10
RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
# open_workflow.yml starts - wait for check completion
gh run watch $RUN_ID --exit-status

if [ $? = 0 ]
then 
    echo "test-2: OPEN-PR (production) SUCCESS"
    gh pr merge $PR_ID --squash
    sleep 10
    RUN_ID=$(gh run list --limit 1 --json databaseId | tr -dc '0-9')
    # close_workflow.yml starts - wait for check completion
    gh run watch $RUN_ID --exit-status
    if [ $? = 0 ]
    then 
        echo "test-2: CLOSE-PR (production) SUCCESS"
    else 
        echo "test-2: CLOSE-PR (production) FAILURE"
        exit 1
    fi
else
    echo "test-2: OPEN-PR (production) FAILURE"
    echo "test-2: FAILURE"
    exit 1
fi

#clean-up
echo "cleaning up..."
echo "test-2: SUCCESS"
git checkout production
git pull --all
git reset --hard HEAD~1
git push -f origin production

git checkout development
git pull --all
git reset --hard HEAD~1
git push -f origin development

git branch -D test-2
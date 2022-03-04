# test pr_closed 

# valid test 1-> create test-3, create a pull request to development
# allow merge to development, try to delete test-3 - if test-3 gets
# recreated then test is successfull

# valid test 2 -> create pull request to production
# allow merge to production, after merge is complete try to delete test-3
# if test-3 is deleted the test is successfull

git checkout production
git pull --all
git checkout -b test-3
echo -e '\n' >> README.md
git add .
git commit -m "test-3"
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
    else
        echo "test-3: CLOSE-PR (production) FAIL"
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
else
    echo "test-3: Delete workflow recreated branch - pr_closed workflow is not working properly"
    exit 1
fi

git branch -D test-3
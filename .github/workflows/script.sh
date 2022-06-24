#!/usr/bin/env bash

. "utils.sh"

RUNNING_WORKFLOW=$(check_command "gh run list --json databaseId --repo sukyca/snowflake-test-repo")

echo "$RUNNING_WORKFLOW"
#!/usr/bin/env bash
echo "Im here"
check_command(){
    command=$1
    $command

    if [[ $? = 1 ]];
    then
        retry_num=1
        while [ $retry_num -lt 4 ];
        do
            echo ""
            echo "Attempting to reconnect...$retry_num"
            ((retry_num++))
            $command
            echo "exit code = $?"
            sleep 5
        done
    fi
}
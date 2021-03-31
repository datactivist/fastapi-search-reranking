. api-config.config     # Read config file

Help()
{
   # Display Help
   echo "Start reranking API service using api-config.config configuration."
   echo
   echo "Syntax: start_service.sh [-d|-s|-h]"
   echo "options:"
   echo "d     Run the docker image on a container with the same name"
   echo "s     Run the docker image in silent mode (when using -d option)"
   echo "h     Show this help panel"
   echo
}

flag_start_docker=false
flag_silence_docker=false

while [ -n "$1" ]; do # while loop starts

	case "$1" in

    -d) flag_start_docker=true ;;

	-s) flag_silence_docker=true ;;

    -h) Help 
        exit;;

	*) echo "Option $1 not recognized, use option -h to see available options" 
       exit;; # In case you typed a different option other than a,b,c

	esac

	shift

done


start_docker()
{
    if $flag_start_docker; then
        if $flag_silence_docker; then
            echo "silent mode"
        else
            echo "starting docker"
        fi
    else
        echo "Not starting docker"
    fi
    echo ""
}

start_local_mode()
{
    cd app
    uvicorn main:app
}

if [ $deployment_method == "local" ]; then
    start_local_mode
elif [ $deployment_method == "docker" ]; then
    sudo docker build -t $docker_name:$docker_version .
    start_docker
else
    echo "'$deployment_method' is not a valid value for deployment_method in config.config"
fi

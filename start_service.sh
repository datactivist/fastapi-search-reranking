. api-config.config     # Read config file

Help()
{
   # Display Help
   echo "Start reranking API service using api-config.config configuration."
   echo
   echo "Syntax: start_service.sh [-d|-s|-r|-h]"
   echo "options:"
   echo "d     Run the docker image on a container with the same name"
   echo "s     Run the docker image in silent mode (when using -d option)"
   echo "r     Run the API in reload mode (development)"
   echo "h     Show this help panel"
   echo
}

flag_start_docker=false
flag_silence_docker=false
flag_reload=false

while [ -n "$1" ]; do # while loop starts

	case "$1" in

    -d) flag_start_docker=true ;;

	-s) flag_silence_docker=true ;;

    -r) flag_reload=true ;;

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
        sudo docker stop $reranking_docker_name
        sudo docker rm $reranking_docker_name
        if $flag_silence_docker; then
            sudo docker run -d --name $reranking_docker_name -h $API_host_name -p $API_port:80 $reranking_docker_name:$reranking_docker_version
        else
            sudo docker run --name $reranking_docker_name -h $API_host_name -p $API_port:80 $reranking_docker_name:$reranking_docker_version
        fi
    else
        echo "Not starting docker"
    fi
    echo ""
}

start_local_mode()
{
    cd app

    if $flag_reload; then
        uvicorn main:app --host $API_host_name --port $API_port --reload
    else
        uvicorn main:app --host $API_host_name --port $API_port
    fi

}

if [ $deployment_method == "local" ]; then
    start_local_mode
elif [ $deployment_method == "docker" ]; then
    sudo docker build -t $reranking_docker_name:$reranking_docker_version .
    start_docker
else
    echo "'$deployment_method' is not a valid value for deployment_method in config.config"
fi

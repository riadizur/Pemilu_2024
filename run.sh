for i in $(cat script_list.txt); do
  sh script_runner.sh $i
done

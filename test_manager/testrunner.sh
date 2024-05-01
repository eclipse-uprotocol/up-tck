echo Enter the feature file name
read fname
echo Enter Language Under Test [python/java]
read language
echo Enter Transport Under Test [socket]
python3 -m behave --define uE1=%language% --define transport=%socket% -i "${fname}" --format html --outfile reports/"${fname}_$(date +%Y%m%d_%H%M%S).html"
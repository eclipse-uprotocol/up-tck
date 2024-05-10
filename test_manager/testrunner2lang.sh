echo Enter the feature file name
read fname
echo Enter Language1 Under Test [python/java]
read language1
echo Enter Language2 Under Test [python/java]
read language2

python3 -m behave --define uE1=%language1% --define uE2=%language2%  -i "${fname}" --format html --outfile reports/"${fname}_$(date +%Y%m%d_%H%M%S).html"
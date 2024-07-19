echo Enter the feature file name
read fname
echo Enter Language1 Under Test [python/java/rust/cpp]
read language1
echo Enter Transport1 Under Test [socket/zenoh/someip]
read transport1
echo Enter Language2 Under Test [python/java/rust/cpp/_blank_]
read language2
echo Enter Transport2 Under Test [socket/zenoh/someip]
read transport2
python3 -m behave --define uE1="${language1}" --define uE2="${language2}" --define transport1="${transport1}" --define transport2="${transport2}" -i "${fname}" --format html --outfile reports/"${fname}_$(date +%Y%m%d_%H%M%S).html"
echo Enter the feature file name
read fname
python -m behave -i "${fname}" --format html --outfile reports/"${fname}_$(date +%Y%m%d_%H%M%S).html"
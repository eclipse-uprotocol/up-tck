#python -m behave -i updatedoor_method_latest_4vehicle.feature -f behave_html_formatter:HTMLFormatter -o reports/updatedoor_method_latest_4vehicle.html --junit
echo Enter the feature file name
read fname
python -m behave -i "${fname}" --format html --outfile reports/"${fname}_$(date +%Y%m%d_%H%M%S).html"

#behave --no-capture
#behave
#behave -i publish -f json.pretty -o reports/behave_output.json
#curl -H "Content-Type: application/json" -H "Authorization:Bearer NDYxMDAwOTI2Mjg2OoUyye2Eo5T6umy6+/KCU2i/kCiy" -X POST --data @behave_output.json https://jira.ultracruise.gm.com/rest/raven/1.0/import/execution/behave
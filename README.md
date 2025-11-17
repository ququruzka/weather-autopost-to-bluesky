# weather-autopost-to-bluesky
This scipt make an autopost weather status to bluesky at 10:00 and 20:00 Running ind Docker. 
### Preparing
Get API key here: https://openweathermap.org/. Set recently got API key as ```OWM_API_KEY``` in ```.env``` file.
File ```city.list.json.gz``` should be extracted in current directory. Find your desired city and add to ```.env``` file for ```CITY_ID``` variable. (Permanent location: https://bulk.openweathermap.org/sample/city.list.json.gz).
  

### Build and run
For creating the new image execute:
```docker-compose build```
It will create image with the current nearby Dockerfile.
For ruuning container in detached mode execute:
```docker-compose up -d```
Weather for desired city will be posted at time defined in ```crontab.txt```

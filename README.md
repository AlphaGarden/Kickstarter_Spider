#### How to spawn daily Kickstarter spider

Go to the `<your path>/Kickstarter_Spider/DailyKickstater/` 

Type the following script on `git bash` to have the spider run periodically. 

``` bash
while true;
do scrapy crawl dailykickstarter;
sleep 24h;
done
```
## Project Name:  news_scraper

A Progressive Online News article scraper. 

Currently I've build it for scraping [Telegraph](https://www.telegraphindia.com/) news articles and it stores articles in json structured format.

An e.g.
```json5
{
    "https://www.telegraphindia.com/": [
        {
            "link": "india/kids-can-carry-higher-covid-loads-than-adults/cid/1789640",
            "headline": "kids can carry higher covid loads than adults",
            "text": "children may serve as silent carriers of the new coronavirus infection, showing no symptoms but possessing viral loads even higher than adults hospitalised with severe coronavirus disease, new research released on thursday has suggested. the study by doctors at the massachusetts general hospital in the us has revealed that children may be a potential source of the infection, capable of spreading the virus that causes covid-19 even though they may have mild or no symptoms. the study, published in the journal of paediatrics ...",
            "time": "1597991010"
        },
        { 
            "link": "india/bande-mataram-the-song/cid/1788606",
            "headline": "bande mataram!",
            "text": "the story goes that sick and tired of hearing god save the queen at all official events and functions, 19th century writer bankimchandra chattopadhyay decided to pen the lyrics of bande...",
            "time": "1597991010"
        }
    ] 
}
```
I guess it's future proof as it doesn't pickup elements from DOM through class name(html) unnecessarily.

~ Bisakh.



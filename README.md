# busbuddy

`busbuddy` is the working name for a project to provide improved bus tracking in the UK, making use of [Bus Open Data Service](https://data.bus-data.dft.gov.uk) (BODS) data.

## Why?

There are of course many bus apps at the moment making use of BODS data or provided by the companies themselves but, looking at the example from my local company, one omission appears to be the ability to track your bus in its incoming, preceding journey.

Commonly buses inter-work between different routes, especially in large towns a nd cities. A bus might, during the course of the day, work on routes 10, 13 and 14, for example. This inter-working is not always predictable from inspecting the timetables and the exact patterns might vary throughout the day, but should be consistent day-to-day. What might be nice, if you are joining the bus in a large town and city, is to be able to track your vehicle as it arrives in the city, even if it's on a completely different route. 

BODS data (a combination of timetable and SIRI data) should allow us to do this.

## What?

At the moment this repository just contains experimental tools for setting up a journeys database and figuring out workings from SIRI live data (see below), nonetheless the aim is to produce a series of server-side tools for processing the data, and an end-user app.

## Issues and solutions

Key to the development of such a system is what's called the *block number*. Each vehicle should, in theory, operate a certain, predictable sequence of journeys (not necessarily on the same route) during the course of the day. The block number describes this sequence of journeys. In theory it should be included in the timetable data but in my experience it is missing, or can be inaccurate (doesn't accord with on-the-ground observations).

However, the SIRI (live bus running info) data appears to more reliably contain the block number for the current day, at least for my local operator. What we can thus do is monitor the SIRI data continuously through the course of a day and populate the timetables database with the information (for the current day). At the end of the day we record all the journeys with a given block number. We can then analyse this data over multiple days to see if it is consistent.

## Thanks

Many thanks to Ciaran McCormick for providing these libraries for working with BODS data:
- [python-bods-client](https://github.com/ciaranmccormick/python-bods-client) for working with live SIRI data via the API;
- [pytxc](https://github.com/ciaranmccormick/pytxc) for working with TransXChange timetable data.

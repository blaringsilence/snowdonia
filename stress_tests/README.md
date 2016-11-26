# Stress/Load Tests

## Tools
Per the [challenge](CHALLENGE.md), this app was tested against 1000 concurrent users (at max). This was done locally, while the app ran on my machine, and while deployed [on heroku](http://snowdonia-transport.herokuapp.com), using [Locust](http://locust.io), to simulate the user (vehicle) behavior described.

It's worth noting that before using Locust, I tested the app for resiliance with 1K concurrent users for 15 seconds using [Loader.io](http://loader.io), but this test sent the same request over and over, so it only served as a general indicator while in development. The report, however, can be found [here](http://bit.ly/2glUmbK).

## Behavior
In the [locustfile](stress_tests/locustfile.py), Locust simulates a vehicle by:
- Assigning a UUID4, a type (train, tram, taxi, or bus), and a number within that type (for example, the first bus is bus-1, the second is bus-2, etc) to display in the test results instead of the UUID for easier filtering.
- This vehicle emits every 20s. Emissions consist of generated lat, long values (random point within 50km of town center), a random heading angle, and a timestamp that conforms to the API format, as well as the common attributes for the vehicle (UUID, type).

## Limitations
### Workers
The test I ran locally, I ran while the app was run by gunicorn using 10 workers. Heroku, on my tier, limits that (if we exceed the number of workers available per the tier specs, performance is actually worse).

### Database
Heroku limits this app to 10K rows, and for a total of `n` requests/emissions, the number of rows is `NUMBER_OF_UNIQUE_VEHICLES + n`, which limits testing the deployed app.

## Results
### Locally
Stress test was run with 1000 concurrent users (max) hatched at 50 users/sec, for the duration of 3021 total requests. The results were as follows:
- **Number of failures**: **0**
- **Median response time**: 42ms
- **Average response time**: 61ms
- **Max response time**: 296ms

The .csv results can be found in [local_test.csv](stress_tests/local_test.csv), which is searchable on github.

### On Heroku
The same test was run with 1000 concurrent users (max) hatched at 50 users/sec, for the duration of 3309 total requests. The results were as follows:
- **Number of failures**: **0**
- **Median response time**: 1800ms
- **Average response time**: 1987ms
- **Max response time**: 26213ms

The .csv results and the distribution of the response times can be found in [deployed_test.csv](stress_tests/deployed_test.csv) and [deployed_test_dist.csv](stress_tests/deployed_test_dist.csv) respectively, also searchable on github.

### Conclusion
The aim while developing and structuring this app was to get 0 failures at max concurrent users (1000), which was achieved as indicated by those tests. However, there is a significant difference in response times between the testing done on the deployed app and that done locally - some responses exceeded the 20s gap between requests that a vehicle sends - which leads me to think better response times can be achieved by:
- Overcoming the Heroku limitations on number of workers per app (easily done through a different tier).
- Having the API return an immediate response without commiting to the database first by having a background task queue, using something like [Celery](http://flask.pocoo.org/docs/0.11/patterns/celery/), for example.

## Test It Yourself
### Without installing/configuring the app (can only test the deployed version)
1. Install locust
  
  ```bash
    $ pip install locustio
  ```
  (For python3 support, make sure you're getting [v0.8a2](https://pypi.python.org/pypi/locustio/0.8a2))
2. Head to [stress_tests\](stress_tests) and run:

  ```bash
    $ locust
  ```
3. Go to localhost:8089 and configure the max number of concurrent users, as well as number of users hatched per second. This will test against the deployed heroku app. Please keep the database limitations (mentioned above) in mind while testing (I clear the database after my tests, so you should expect it to be cleared by the time you run your tests).

### With the app installed/configured (local OR deployed version can be tested)
#### Local test:
1. Run the app with gunicorn
  
  ```bash
    $ gunicorn snowdonia:app -w 10
  ```
2. Head to [stress_tests\](stress_tests) and run:

  ```bash
    $ locust --host=http://127.0.0.1:8000 # if you haven't configured gunicorn to use another port
  ```
3. Go to localhost:8089 and configure the max number of concurrent users, as well as number of users hatched per second.
#### On deployed app:
1. From [stress_tests\](stress_tests) run:

  ```bash
    $ locust
  ```
2. Go to localhost:8089 and configure the max number of concurrent users, as well as number of users hatched per second. This will test against the deployed heroku app. Please keep the database limitations (mentioned above) in mind while testing (I clear the database after my tests, so you should expect it to be cleared by the time you run your tests).

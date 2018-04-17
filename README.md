# API client for healthcare cost ranges

### What does this do?
Queries [guroo.com's](https://www.guroo.com/#!) API to retrieve cost ranges for a "care bundle" or grouping of related procedures.
The costs are tied to a location, which can be set as desired.

### Why did you build this?
Guroo has a great service, which is powered by work done by the [Health Care Cost Institute (HCCI)](http://www.healthcostinstitute.org/).
I wanted to use the cost data from the service for my own research, so I reverse-engineered their API format and built a simple client for it.

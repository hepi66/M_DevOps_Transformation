# DORA Metrics & Operational Excellence

This document outlines the performance metrics we use to monitor and improve our DevOps capabilities throughout the M-DevOps-Transformation project lifecycle.

## Core DORA Metrics
We focus on the four key metrics to ensure high-velocity and high-stability delivery:

* **Deployment Frequency:** Measuring the frequency of successful releases to production.
* **Lead Time for Changes:** Tracking the time from code commit to code running in production.
* **Change Failure Rate:** Monitoring the percentage of deployments causing failure in production.
* **Time to Restore Service:** Measuring the time required to recover from a production failure.

## Tracking & Integration
To align with our project goals, we track these metrics through:

- **GitHub Projects:** Custom fields for `Iteration` (Sprint tracking) and `Lead Time (h)` are integrated into our board.
- **Pipeline Integration:** Starting with Epic 2, CI/CD pipeline telemetry will be captured to provide raw data for these metrics.
- **Continuous Improvement:** Every sprint review includes a check on how our engineering changes impact these core metrics.

## Methodology
- **Data-Driven Decisions:** Metrics are used to identify bottlenecks in our CI/CD pipeline, not to evaluate individual performance.
- **Transparency:** Metric dashboards will be made visible to the team once the CI/CD pipeline (Epic 2) is established.
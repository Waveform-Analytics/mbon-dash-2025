# Big picture thoughts

25 Sept 2025

Now that we have done quite extensive exploration it is time to step back and to remember (or refine) our goals, and the question(s) we are trying to answer. 

**The question(s)**: 

- Can we use acoustic indices to help us to understand biological complexity using the May River dataset? 
- If so, is it something that we could reasonably expect to be able to extrapolate to other marine ecosystems? 

- **Who is our audience?**: 

Environmental managers interested in monitoring biological diversity in a specific area

## Our datasets

- Environmental (temperature, depth)
- Manual detections (various fish, bottlenose dolphins, and anthropogenic sound sources; from expert analysis of acoustic recordings)
- RMS SPL (low, high, and broadband; computed from acoustic recordings)
- Acoustic indices (~60 covering a variety of feature types like amplitude, frequency, complexity, etc)

## What we have done so far

We have a pipeline set up that does a variety of data prep and analysis steps:

- load, clean, and align the datasets
- extract temporal features 
- explore correlations between indices and each other (to help identify very similar indices)
- explore correlations between indices and fish data
- compute feature importance using mutual information and the Boruta method
- defined targets: individual species and vessels as well as community metrics like summed fish intensity, # unique species, activity levels in percentiles (e.g. 75th, 90th, *any* activity)
- defined features: temperature, depth, rms spl, and acoustic indices
- ran simple ML models: random forest, decision tree, logistic regression
- developed a probability surface to help identify when biological activity is expected to happen based on the environment, indices, and known biological patterns (from manual detections)

## Where to focus to answer our questions

- focus on community metrics like summed fish intensity, # unique species
- which features are important? drill down a bit more to more carefully identify correlations, remove mathematically similar indices to avoid redundancy, and determine whether any of the indices have similarity / are correlated with any of the biological community metrics.

## Possible additional focus? (or maybe future work)

-  explore the use of a generalized additive model or a generalized linear mixed model in a way that integrates the probability surface into a predictive framework.

## What is left?

- Refine the focus - don't over-complicate things
- put together a paper outline that addresses the core questions for our expected audience. Maintain a targeted scope (we will not include our entire exploratory path - this will be a more "curated" journey so our message is as clear as possible. 
- based on our refined focus and paper plan, decide on the flow and set of interactive images that would best guide people through our findings so that they can understand the implications for their own work (including strengths, limitations, and future work)

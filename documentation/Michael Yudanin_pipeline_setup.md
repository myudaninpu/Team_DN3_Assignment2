# Assignment 2, Pipeline setup

1. Created BigQuery dataset
   Dataset Information:
      Dataset ID: store_sales_team_DN3
      Description: Team DN3 Store Sales Analysis
      Location: US
      Created: 2025-07-26 19:29:36.695000+00:00

2. Created the pipeline programmatically
   Log:   
     Starting Dataflow pipeline...
     Command: python beam_pipeline.py mgmt599-myudanin-lab2 my-assignment2-bucket kaggle-store-sales store_sales_team_DN3 us-central1
     Starting pipeline with parameters:
     Project ID: mgmt599-myudanin-lab2
     Source: gs://my-assignment2-bucket/kaggle-store-sales/
     Dataset: mgmt599-myudanin-lab2.store_sales_team_DN3
     Region: us-central1
     [...]
     Pipeline submitted!

3. Verified data load
   For sales data:
     row_count	earliest_date	latest_date
     3000888	2013-01-01	2017-08-15
   For store info:
     store_count
     54


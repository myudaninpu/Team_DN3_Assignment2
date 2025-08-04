#Assignment 2, Building a model

1. Prepared data in a new table 'store_daily_sales'

2. Split the data into two tables:
   - store_daily_sales_train for training
   - store_daily_sales_test for testing

3. Created a Linear Regression model 'store_daily_sales'

4. Evaluated the modelon the training data with the following results:
     mean_absolute_error: 5523.953300136308
     mean_squared_error: 63291820.87050185
     mean_squared_log_error: 7.325518606744274
     median_absolute_error: 3817.9119115115386
     r2_score: 0.3527671042060667
     explained_variance: 0.35278416760644915

5. The results were poor, as the explained variance was barely above 35% and the mean absolute error was high.

6. Improved the model by adding engineered features: 
   - month
   - day-of-week
   - day-of-month
   - week-of-year
   - sales_lag_1 (sales from 1 day ago)
   - sales_lag_7 (sales from 7 days ago)
   - sales_7day_avg
   - sales_vs_cluster_avg
   - one-hot encoding for type (A, B, C, D, E)

   into two new tables:
   - _store_daily_sales_train for training
   - _store_daily_sales_test for testing

7. Trained the new model on the engineered training data table

8. Evaluated the new model with the following results:
     mean_absolute_error: 1839.2901499122625
     mean_squared_error: 9935392.681032853
     mean_squared_log_error: 1.4256680387363287
     median_absolute_error: 1165.5605082571183
     r2_score: 0.8986678156713597
     explained_variance: 0.8986842046068393

     The evaluation showed marked improvement with almost 90% of the variance explained and a much lower MAE.

9. Ran predictions on the engineered test data table with the following results:
    Total Predictions: 756
    Mean Absolute Error (MAE): $2,591.18
    Root Mean Squared Error (RMSE): $3,839.66
    Mean Absolute Percentage Error (MAPE): 18.77%
    Correlation: 0.9113
    R-squared: 0.8253
    Mean Bias: $-278.42
    Accuracy within 10%: 36.4%
    Accuracy within 20%: 62.6%


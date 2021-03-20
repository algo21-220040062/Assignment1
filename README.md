# Assignment1
@Han-wen-Zhang  
_This repo of assignment is a part of MFE5210 algo-trading in CUHKSZ._  
_And the ddl is 3/20/2021 23：59._  

## 0. File reference
Here the pdf is a research report in "style rotation" from founder securities. And my assignment theme will be factor investing. 

## 0.5. Main purpose
Construct a multi-factor backtesting system to test the style rotation factor to explore the style rotation.

## 1. Style rotation factor construction
### momentum: 
Choose 中证800 as the stock pool, every month calculate the portfolio return of long the small market cap and short the big market cap. If the return is positive, we get a signal on Small-cap stocks.
### volume:
Every month choose the first 5 days and the last 5 days to calculate the trading volume of 沪深300 divide by trading volume of 中证800， if the value of factor is less at the end of month then get a signal on Small-cap stocks.

## 2. Single-factor test
Calculate and normalize the factor signal. And test IC/IR, t-stats value, calculate the factor return frequency.
![20210320154927](https://user-images.githubusercontent.com/78670024/111863026-e596df80-8993-11eb-8eed-5146fe0828bf.png)
![20210320155116](https://user-images.githubusercontent.com/78670024/111863063-255dc700-8994-11eb-8668-7effddadcbb8.png)
![20210320155327](https://user-images.githubusercontent.com/78670024/111863117-6fdf4380-8994-11eb-9ee4-0264c186d978.png)
![图片2](https://user-images.githubusercontent.com/78670024/111863127-9604e380-8994-11eb-820f-2765d4ace689.png)

## 3. Backtest and calculate the return
divide the stock to 5 groups and do backtest each group.
![图片3](https://user-images.githubusercontent.com/78670024/111863141-af0d9480-8994-11eb-8dcd-d378247df6cd.png)  
The color from purple to blue means the factor value from high to low. 

## 4. Summary
My conclusion is that for A share stocks, there exist obvious style rotation. When the small market cap stock return becomes bigger, the market style is changing to Small-cap. But the trading volume is not acting like so, big-cap stock will always hold more market trading volume and when want to adjust the trading strategy using the volume it is not so useful.

# House Rocket Insights Project
This repository contains all files regarding the house rocket insight project made by myself.

This project is fictitonal, but built upon real data made available in Kaggle. The data reflects property sales in the city of Seattle between 2014 and 2015, and we will use the sale value imagining that this is a portfolio of properties available for sale and the purchase price will be the sale value. **The result of the analysis is uplodead online at a application hosted on Heroku Cloud.**

[Interactive dashboard link](https://house-rocket-insights-andre.herokuapp.com/)

[Project planning](https://chiseled-jam-e35.notion.site/00-Insights-Project-17fbd63df9fe439fa5ced70c4670c5ca) 

![N|Solid](https://www.homes.com/images/national-state/hero-for-sale.jpeg)

### The company
House Rocket is a fictional company that trades properties in US for a small price and offer them for sale at a higher price.

### Business problem
Find properties that are good deals, a good deal being one that is bought at a low price and resold at a high price .

### The Business Matter

- **What properties should House Rocket buy and for what price?**
- **When to sell the properties and for what price?**

Raised business hypotheses that can help generate insights into the purchase price:

1. Properties that have water front feature are 20% more expensive, on average, than those without a view
2. Properties with a construction date less than 1980 are 55% cheaper on average
3. Properties without basements have 40% more lot area than those without basements
4. YoY (Year over Year) price growth is 10%.
5. Properties with 3 bathrooms or more have a MoM (Month over Month) growth of 15% in price
6. Properties with 1 bedroom are 30% cheaper on average compared to properties with 2 or more
7. Total properties available for purchase grew 15% YoY
8. The standard deviation of the price of properties that have more than 2 bedrooms is 40% lower than the others
9. Properties that have undergone renovation are 50% in better condition compared to properties that have not been renovated
10. Renovated properties from 1980 onwards are 50% in better condition compared to all other properties (renovated or not)

### Business Assumptions
- We have a database with sold properties in Seattle/WA - USA between may 2014 and may 2015
- We will work with all properties in the database (around 21k)
- Altough the database is about sold properties, we will imagine that this is a portfolio of available properties for purchase and imagine a scenario where we have to recommend which ones are the best for purchase only with exploratory data analysis.

### Solution Planning
- To define if a property should be bought we grouped the data by zipcode and took the median price. For each property, we divided the price by the zipcode median price and took a price index, where if the price index < 1, the property should be bought. The lower the index, the best is the business opportunity.
- Also it was proven that properties with waterfront view are way expensive, so properties with a price index < 1 and with this feature must be purchased with priority.
- To define when a property should be sold we grouped data by zipcode and for each zipcode we grouped by season where it was bought (fall, winter, spring and summer). We counted the amount of properties sold for each zipcode in each season and the season with most properties sold is the one recommended.
- To set price we also grouped data for zipcode and season and took the median price for each one of them.  If the price is lower than the zipcode median price and season median price, than it should be sold by the price + 30%. If the price is higher than both, the sell price recommended is price + 10% and if the price is higher than one, and lower than other (zipcode and season median price) the sell price is price + 20%.

### Financial Expectations 

The portfolio have a potential to generate aroud **$1.2B** in profit if all properties are bought. Imagining that this is hard to get, if we imagine 1% of them bought (aprox 210 properties), the profit could reach **$12M**.

### Insights
- Properties with a waterfont view are 200% more expensive on average. Getting one of these properties for a low price represents good business

- Properties built before 1980 are 14% cheaper on average. There is no big price disparity if you use this cut-off as a comparison

- Properties without a basement have 22% more lot area. If we look for properties with larger lot areas, we can look at these without basements

- YoY property price grew 0.7%

- One-bedroom properties are 70% cheaper compared to properties with 2 or more bedrooms

- The amount of properties available for purchase fell 113% YoY (2014 to 2015)

- The standard deviation of properties with two or more bedrooms is 96% higher compared to properties with two or fewer

- The property having been renovated does not impact their condition. The condition is basically the same comparing these two categories


# How to misinform with official data and why Greece should pay closer attention to Net Migration. 

5 minutes read
*Comparing apples to oranges and elephants to cats is a frequent "misstep" in data analysis.*

## Greece made it to the top of the list of countries with the highest Negative Net Migration in 2023.

In the past weeks, several variations of the same social media post pointed out that 159 thousand people left Greece in 2023.  
Accordingly, *Greece is ranked 11th in the world*, in terms of Negative Net Migration.  
Negative Net Migration means more people are leaving a country than entering it.
High numbers of people leaving implies adverse socio-economic conditions, political instability and uncertainty.  
In the most extreme cases, this is a result of war or war-like situations.   
On the other hand, according to [Eurostat](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Migration_and_migrant_population_statistics):
> "Migration is influenced by a combination of economic, environmental, political and social factors: either in a migrant's country of origin (push factors) or in the country of destination (pull factors).  
> Historically, the relative economic prosperity and political stability of the EU are thought to have exerted a considerable pull effect on immigrants."

Being a Greek citizen, I was intrigued by the news and decided to fact-check it.  
The data used are official estimates and the source of the data is the [United Nations Population Prospects 2024](https://population.un.org/wpp/), published on July 11.   
The origin of all posts on the topic is, to the best of my knowledge, a [post](https://www.visualcapitalist.com/mapped-the-countries-losing-people-to-emigration-2023/) by [visualcapitalist](https://www.visualcapitalist.com/) which most of the time creates informative, pleasing infographics, and has been a source of inspiration.  
But, there are several major issues with the way that information has been presented.  

Since the data was valid, out of professional and academic interest, I decided to dive deeper into it.   
Actually, this is a handy example of new content for this year's [Python Course](https://github.com/argythana/uoa_py_course) at the University of Athens, to demonstrate how to look for insights into complex multidimensional phenomena at the lecture on [Exploratory Data Analysis](https://github.com/argythana/uoa_py_course/tree/main/lectures_07_12_pandas_scikit/lecture_09_EDA_plots).

In short, the results are a bit more worrying.  
The data show that *Greece ranks number one* in the whole world, in terms of Negative Net Migration, as a percentage of the population, excluding war-torn areas and small nation states.    

![Top 20 countries in Negative Migration](https://github.com/argythana/uoa_py_course/blob/main/lectures_07_12_pandas_scikit/lecture_09_EDA_plots/top20_in_negative_migration_2023.png)  

Please read below for a more detailed analysis on the methodology and the data. To Do Your Own Research, please take a look at the [Notebook in GitHub](https://github.com/argythana/uoa_py_course/blob/main/lectures_07_12_pandas_scikit/lecture_09_EDA_plots/lecture_07f_wpp_eda.ipynb).

## Why it matters

Negative Net Migration, in combination with the low birth rates, may lead to a gradual decline in the population of Greece in the near future.  
Starting with the seminal *Harrod-Domar* model, population growth is a key factor for economic growth.  
The centrality of population growth in economic development is also highlighted by the Solow model, the Cobb-Daglas production function, the endogenous growth models, and the recent literature on the "demographic dividend".     
In simple terms, the number of people that are productive and contribute to an economy multiplied by productivity defines what a country can produce and consume, defined as GDP (Gross Domestic Product).   
The economic growth can therefore be achieved by increasing the number of the working population, increasing productivity, or both.  
This is where the composition and the demographic characteristics of migration flows are of paramount importance for the economic development of a country.   
Which means Greece should increase it effort to mitigate the "brain drain" phenomenon.  
Greece has an extra reason to be alert, because achieving sustainable economic growth is directly tight to its ability to service the public debt.  
A separate analysis is needed to understand the reasons behind this trend, but it is clear that Greek policymakers should pay closer attention to the issue.  
Having all this in mind, we can better assess the set of measures that were recently announced by the Greek government, but this is also a topic for another post.  


## Methodology and Data

### 1) Relative size matters.
The absolute number of people leaving a country is misleading, unless we take into account the total population of the country.
For example, Philippines is ranked 10th in the world, with 164 thousand people leaving the country in 2023.
This suggests that Philippines exhibits higher negative migration than Greece. But, accounting for the population of the Philippines, more than 115 million, it is easy to understand that the volume relative to Greece is ten times lower.  
To make valid comparisons, besides absolute numbers, one should also present the data as a percentage of the population.

## 2) Greece is not a war zone.
The second major issue is that the data includes countries which currently are or have been in a state of war during the past years.
Ukraine and Sudan are unfortunately under prolonged and severe war conditions that highly affect civilian life, infrastructure and the general political and economic conditions. 
It makes little sense to compare the Net migration of a country in war conditions with the rest of the world.

In fact, according to the official UN estimates, if we exclude war-torn areas and very small nation states, **Greece is number one** in terms of Negative Net Migration.
It is estimated that 1.55% of the population left Greece in 2023.
The top 20 countries, in conditions of peace, in terms of Negative Net Migration in 2023, as a percentage of the population, are presented in the following [table](github).


### 3) Numbers do add up. 
The third major issue is that the data refer just to a single point in time (2023) not providing any context or trend analysis.
For example, the fact that 300 thousand people left Ukraine in 2023, misinforms the reader by missing the fact that 5.7 million people left Ukraine in 2022. 
Similarly, 

### 4) Regulatory and institutional context matter the most.
Perhaps the most important issue is that data do not provide context concerning the regulatory and institutional foundations that provide the basis for the development of the observed patterns.
Greece has been a member of the Schengen Area since 2000, allowing free movement of people within the EU and the Schengen Area, making it easy for people to leave the country and even easier for skilled professionals.
On the other hand, Greece is located in a "crossroad" of three continents and has been a destination for refugees and immigrants during the past decades.
An effective tightening of border controls during the recent years in Greece, may have reduced significantly the number of people entering the country, but not the number of people leaving the country.
Before making any conclusions, one should always consider the context and the regulatory framework that governs the data, while at the same examine the trend over time.

Using the official UN data, a more informative and accurate view the following tables and plots provide a more informative and accurate view of the Net migration in Greece in comparison to the rest of the world.
Data are presented as a percentage of the population, the countries in war conditions are excluded, and the trend for the last 10 years is presented.

### 5) Estimations are not always accurate and the official data differ 
On a positive note, the data are estimates, and may be subject to revisions, since they have some discrepancies with the official data provided by Eurostat.
To avoid another common mistake in data analysis, very small nation states with a population less than 100 thousand are excluded.  

The data show that while Greece is not a war zone, there most be adverse socio-economic conditions that drive people to leave the country.

What really got me intrigued was the population peak that comes earlier than expected, and the steady decline in the population of Europe.
Not to forget, I find the assumptions for Europe slightly optimistic.
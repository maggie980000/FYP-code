
# Network, Covariates, or Both: A study on dynamic network data with covariates
This is the repo for my Final Year Thesis at NUS. 

I believe in the power of film as an art form with a profound social impact. In my thesis, I aim to investigate the types of films people enjoy in contemporary China, the size of various movie interest groups, and the trends in their preferences. As a data science student and film enthusiast, I am committed to supporting the often marginalized film art community by leveraging my technical skills and unique data narratives.


**Thesis Objectives:**
- Identify clusters or segments of users in a social media network and interpret the resulting segmentation.
- Compare the segments identified from different data sources, i.e. network, covariates, or both.



## Data Collection and Description
In this thesis, we collect user movie rating data from [Douban, a movie rating website](https://movie.douban.com/) spanning April 2023 to September 2023 and construct a dynamic user network that incorporates user attributes or covariates. 
- In the network, each node represents a Douban user. Two users are connected if they rated at least two of the same movies.
- In the user-covariate matrix, covariates capture the personal details of the users, such as the actors and directorsin the movies they’ve rated. Specifically, the value of director, actor, genre and country covariate for a user equals the sum of rating scores (scale from 1 to 5) of all movies associated with a specific covariate rated by a user.

A toy dataset is illustrated in [Figure 1](https://github.com/user-attachments/assets/c3396368-00aa-47e2-9a95-9cfcbe52c516).
The Python parser for automated covariate generation from orignal user data scrapped from the website can be found in [generate_cov](https://github.com/maggie980000/FYP-code/tree/main/generate_cov) folder.


*Figure 1: Toy  dataset.*
![image](https://github.com/user-attachments/assets/c3396368-00aa-47e2-9a95-9cfcbe52c516)




## Data Analysis Process and Key Findings

1. We begin by conducting user segmentation or clustering based on their static **covariates** including actors and directors. Our interpretation of the segmentation results suggest that movie interests represented by covariate segments are production **country or region-centered**.
  - The Python implementation of one spectral method can be found in [static_covariates](https://github.com/maggie980000/FYP-code/tree/main/static_covariates) folder.
2. We also identify covariate segments that are growing or shrinking, as well as movie interests with varying persistence levels.
  - The Python implementation can be found in [dynamic_covariates](https://github.com/maggie980000/FYP-code/tree/main/dynamic_covariates) folder.
3. Additionally, user segmentation on static **network** reveals segments that represent different **movie genre interests** among users.
4. Finally, the segments identified based on static network with covariates reflect movie interests shaped by preferences for both movie genre and production country, which unveil more meaningful and coherent interests compared to those obtained using network or covariate data only.


### Comparison between user segments identified from different static data sources
We use covariates beyond actors and directors such as genres and countries to validate the underlying factors shaping the segments identified from different static data sources, i.e. network, covariates, or both. Inspired by this [paper](https://github.com/maggie980000/FYP-code/blob/main/references/2018-AOAS-text_with_graph_facebook.pdf), in [Figure 2](https://github.com/user-attachments/assets/786c4a16-2bc9-4a16-b0ff-69aea15806cb), we provide <data-driven evidence for the region and genre-centered structures of 3 distinct segmentation>.




*Figure 2: User segment's interest score toward movie production country and genre. The size of the circle at each entry represents the relative interest that each segment has on a specific country or genre, a larger circle indicates greater interest.*
<sub><sup>*More precisely, this interest score is measured by averaging the cluster members' ratings on one country or genre covariate, adjusted for the total ratings received by this covariate. For the detailed calculations, one can refer to the [thesis](https://github.com/maggie980000/FYP-code/blob/main/Thesis_Bao_Jiaqi_A0211257N_Final-1.pdf) or the [slides](https://github.com/maggie980000/FYP-code/blob/main/Thesis_Slides%20(1).pdf).*</sup></sub>
![image](https://github.com/user-attachments/assets/786c4a16-2bc9-4a16-b0ff-69aea15806cb)

**Observed Differences:**
First, we observe that a covariate segment tends to concentrate on a specific country, such as Hong Kong for the red covariate segment and the UK for the purple covariate segment. However, these two segments are not densely connected in the network. Instead, the network suggests the presence of 3 new genre-centered segments. When incorporating covariates in the network, these 6 network segments are roughly all identified. But the red segment reveals a stronger focus in Hong Kong that is not evident in the red segment estimated using network data only.

**Possible Explanations:**
We attempt to provide possible explanations for the country-centered segmentation structure in covariates and movie genre-centered segmentation structure in network. For networks, connections are primarily formed based on trending movies, and when users decide which popular movie to watch, they are likely to ignore the country of production and choose based on their favorite genres. For covariates, actors are likely to be involved in movies with various genres, making it challenging for covariate segmentation to separate movie genres. However, the production countries of the movies in which an actor appears tends to remain consistent, leading covariate segmentation to detect users’ preferred production countries.



## Methodology 

The detailed methods adopted for segmentation and more evaluation and visualization results can be refered to the [thesis](https://github.com/maggie980000/FYP-code/blob/main/Thesis_Bao_Jiaqi_A0211257N_Final-1.pdf) and the [slides](https://github.com/maggie980000/FYP-code/blob/main/Thesis_Slides%20(1).pdf).
Note that I only updated my Python implementations for methods that are relatively more complex and computationally-intensive in this repo.



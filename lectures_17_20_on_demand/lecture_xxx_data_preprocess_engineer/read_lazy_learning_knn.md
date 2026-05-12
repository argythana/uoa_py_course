# Lazy learning and KNN — Q&A reference

**Provenance.** This content was originally cell 0 (a 9.3 KB markdown block) of `lectures_07_13_pandas_plots_scikit/lecture_10_knn_classifier/lec_10b_study_knn_use_AI.ipynb`, recovered from `git show HEAD:<path>` on 2026-05-12 after that notebook was retired as part of the Lecture 10 refactor. The Q&A pairs were produced by Bing Chat on 2023-05-30; the answers and the cited URLs are the chatbot's, not the maintainer's. Kept here as an on-demand reading reference; verify any factual claim before quoting in class.

---

## What is a lazy-learning algorithm?

In machine learning, a lazy learning algorithm is a learning method in which generalization of the training data is delayed until a query is made to the system. This is in contrast to eager learning, where the system tries to generalize the training data before receiving queries. The primary motivation for employing lazy learning is that the data set is continuously updated with new entries. Because of this continuous update, any "training data" would be rendered obsolete in a relatively short time. Some examples of lazy learning algorithms include k-nearest neighbors (kNN), Case-Based Reasoning (CBR), and Locally Weighted Learning (LWL).

*Sources (Bing, 2023-05-30):*

- [Lazy learning — Wikipedia](https://en.wikipedia.org/wiki/Lazy_learning)
- [Lazy vs. Eager Learning — Baeldung](https://www.baeldung.com/cs/lazy-vs-eager-learning)
- [Lazy Learning vs. Eager Learning — Analytics Vidhya](https://www.analyticsvidhya.com/blog/2023/02/lazy-learning-vs-eager-learning-algorithms-in-machine-learning/)
- [What is lazy learning? — AI For Anyone](https://www.aiforanyone.org/glossary/lazy-learning)

## What are some advantages of lazy learning?

Lazy learning offers several advantages. One of the main advantages of employing a lazy learning method is that the target function will be approximated locally, such as in the k-nearest neighbor algorithm. Because the target function is approximated locally for each query to the system, lazy learning systems can simultaneously solve multiple problems and deal successfully with changes in the problem domain. Lazy learning algorithms can also adapt quickly to new or changing data since the learning process happens at prediction time. They can incorporate new instances without requiring complete retraining of the model.

*Sources (Bing, 2023-05-30):*

- [Lazy learning — Wikipedia](https://en.wikipedia.org/wiki/Lazy_learning)
- [What is Lazy Learning? — DataCamp](https://www.datacamp.com/blog/what-is-lazy-learning)
- [What is lazy learning? — AI For Anyone](https://www.aiforanyone.org/glossary/lazy-learning)

## What are some disadvantages of lazy learning?

There are several disadvantages to lazy learning. One theoretical disadvantage is the large space requirement to store the entire training dataset. However, in practice, this is not an issue because of advances in hardware and the relatively small number of attributes that need to be stored. Another disadvantage is that lazy learning methods are usually slower to evaluate. Since lazy learning algorithms search through data to find the query object's neighborhood, they can be slower at making predictions.

*Sources (Bing, 2023-05-30):*

- [Lazy learning — Wikipedia](https://en.wikipedia.org/wiki/Lazy_learning)
- [Lazy vs. Eager Learning — Baeldung](https://www.baeldung.com/cs/lazy-vs-eager-learning)
- [Lazy learning — Engati](https://www.engati.com/glossary/lazy-learning)

## How does KNN work?

The k-nearest neighbors algorithm (k-NN) is a non-parametric, supervised learning classifier that uses proximity to make classifications or predictions about the grouping of an individual data point. It is used for both classification and regression problems. In k-NN classification, an object is classified by a plurality vote of its neighbors, with the object being assigned to the class most common among its k nearest neighbors (k is a positive integer, typically small). If k = 1, then the object is simply assigned to the class of that single nearest neighbor.

*Sources (Bing, 2023-05-30):*

- [What is the k-nearest neighbors algorithm? — IBM](https://www.ibm.com/topics/knn)
- [k-nearest neighbors algorithm — Wikipedia](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm)
- [K-Nearest Neighbor(KNN) Algorithm — GeeksforGeeks](https://www.geeksforgeeks.org/k-nearest-neighbours/)

## What are some advantages of k-NN?

The k-NN algorithm has several advantages. One advantage is that it is a non-parametric method, meaning that it makes no assumptions about the underlying data distribution. This can be particularly useful when dealing with complex data distributions. Another advantage is that it is a lazy learner, meaning that it stores the entire training dataset and learns from it only at the time of making real-time predictions. This makes the k-NN algorithm much faster at training than other algorithms that require an explicit training phase. Additionally, k-NN only requires a `k` value and a distance metric, which is low when compared to other machine learning algorithms.

*Sources (Bing, 2023-05-30):*

- [Advantages and Disadvantages of KNN Classifier — i2tutorials](https://www.i2tutorials.com/advantages-and-disadvantages-of-knn-classifier/)
- [What is the k-nearest neighbors algorithm? — IBM](https://www.ibm.com/topics/knn)
- [Benefits of k-NN Algorithms — Tutorials Point](https://www.tutorialspoint.com/what-are-the-benefits-of-k-nn-algorithms)
- [For what type of problems nearest neighbor performs better — Cross Validated](https://stats.stackexchange.com/questions/44518/for-what-type-of-problems-nearest-neighbor-performs-better)

## What are some disadvantages of k-NN?

The k-NN algorithm has several disadvantages. One disadvantage is that it does not work well with large datasets. In large datasets, the cost of calculating the distance between the new point and each existing point is huge, which degrades the performance of the algorithm. Another disadvantage is that it does not work well with high-dimensional data. With a large number of dimensions, it becomes difficult for the algorithm to calculate meaningful distances in each dimension. Additionally, k-NN is sensitive to noise in the dataset and requires feature scaling before being applied to any dataset.

*Sources (Bing, 2023-05-30):*

- [Advantages and Disadvantages of KNN Classifier — i2tutorials](https://www.i2tutorials.com/advantages-and-disadvantages-of-knn-classifier/)
- [Pros and Cons of K-Nearest Neighbors — From The GENESIS](https://www.fromthegenesis.com/pros-and-cons-of-k-nearest-neighbors/)
- [K-Nearest Neighbor(KNN) Algorithm — GeeksforGeeks](https://www.geeksforgeeks.org/k-nearest-neighbours/)
- [The Introduction of KNN Algorithm — Great Learning](https://www.mygreatlearning.com/blog/knn-algorithm-introduction/)

## How can I optimally select the number of neighbours in KNN?

The optimal number of neighbors (`k`) in k-NN can vary depending on the specific problem and dataset. One way to select the optimal value of `k` is to use cross-validation. In cross-validation, the training data is split into several subsets and the model is trained on some of these subsets and evaluated on the remaining subsets. This process is repeated for different values of `k` and the value that results in the best performance on the validation sets is chosen as the optimal value.

Another approach is to use a grid search, where a range of values for `k` are tested and the value that results in the best performance on a validation set is chosen as the optimal value.

It is important to note that the choice of `k` can have a big impact on the performance of the k-NN algorithm. A small value of `k` can result in a model that is sensitive to noise and overfits the data, while a large value of `k` can result in a model that is too general and underfits the data.

> See `lectures_07_13_pandas_plots_scikit/lecture_10_knn_classifier/reading_material/lec_10a_knn_classification.ipynb` §B4 for the train-vs-test-accuracy curve approach actually used in the course. Cross-validation and `GridSearchCV` are deferred to Lecture 13.

## How does k-NN work for regression problems?

The k-NN algorithm can also be used for regression problems. In k-NN regression, the output is the property value for the object. This value is the average of the values of its `k` nearest neighbors. The algorithm works by taking a given point and evaluating its `k` neighbors to find similarities. The idea is built from the fact that similar data points will be closer in space than points that are very different from each other.

*Sources (Bing, 2023-05-30):*

- [Regression Example with K-Nearest Neighbors in Python — DataTechNotes](https://www.datatechnotes.com/2019/04/regression-example-with-k-nearest.html)
- [KNN Regression Model in Python — Towards Data Science](https://towardsdatascience.com/knn-regression-model-in-python-9868f21c9fa2)
- [The Basics: KNN for classification and regression — Towards Data Science](https://towardsdatascience.com/the-basics-knn-for-classification-and-regression-c1e8a6c955)
- [KNN Algorithm Guide to Using K-Nearest Neighbor for Regression — Analytics Vidhya](https://www.analyticsvidhya.com/blog/2018/08/k-nearest-neighbor-introduction-regression-python/)
- [K-Nearest Neighbor Regression Example in R — DataTechNotes](https://www.datatechnotes.com/2020/10/knn-regresion-example-in-r.html)

---

## Caveats for future re-use

- **The sources are 2023-vintage.** Several of the linked blog posts may have moved, been paywalled, or be otherwise stale by the time anyone reads this. Verify each link before quoting.
- **The answers are Bing's, not the maintainer's.** Treat each paragraph as a starting point for your own teaching prose, not as authoritative. The Wikipedia and IBM references are the most trustworthy of the cited sources.
- **The current Lecture 10 already covers the load-bearing parts** — lazy learning is named in `lec_10a` cell 0; failure modes are walked through in `lec_10b_knn_assumptions_caveats.ipynb`; AI-fluency on KNN lives in `read_agents_knn_workflows.md`. Use this file as a deeper reading for students who want the Q&A breakdown, not as a replacement for those notebooks.

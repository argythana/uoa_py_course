# Απαντήσεις: scaling στο train/test split, scaling μέσα σε CV, Naive Bayes & KNN

> Όλες οι παρακάτω απαντήσεις είναι επαληθευμένες έναντι των επίσημων scikit-learn docs και άλλων πηγών.
> Οι παραπομπές βρίσκονται στο τέλος του εγγράφου ([§ Πηγές](#πηγές--references)).

---

## 1. Scaling στο απλό train/test split

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
```

**Ναι, ο κώδικας είναι απολύτως σωστός.** Είναι ακριβώς το pattern που τα ίδια τα scikit-learn docs συστήνουν για να αποφεύγεται το data leakage [<sup>[pitfalls]</sup>](#ref-pitfalls) [<sup>[scaler]</sup>](#ref-scaler).

- `fit_transform(X_train)` → ο scaler «μαθαίνει» τη μέση τιμή `μ` και την τυπική απόκλιση `σ` **μόνο από τα training data**, και ταυτόχρονα τα μετασχηματίζει.
- `transform(X_test)` → εφαρμόζει τις **ίδιες** `μ`, `σ` (αυτές που έμαθε από το train) στο test set. **Δεν** τις ξανα-υπολογίζει.

Από την επίσημη σελίδα *Common pitfalls and recommended practices* του sklearn [<sup>[pitfalls]</sup>](#ref-pitfalls):

> «[*Never include test data when using the fit and fit_transform methods. […] This can be achieved by using fit_transform on the train subset and transform on the test subset.*](https://scikit-learn.org/stable/common_pitfalls.html#how-to-avoid-data-leakage)»

Τα λάθη που η μορφή `fit_transform` / `transform` σε αποτρέπει να κάνεις:

- ❌ `scaler.fit_transform(X_test)` → data leakage· το test «κοιτά τον εαυτό του» και τα μέτρα αξιολόγησης γίνονται αισιόδοξα.
- ❌ `scaler.fit(X)` πριν το split → data leakage· το train «είδε» στατιστικά του test.

---

## 2. Scaling μέσα σε cross-validation με Pipeline

```python
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42))
])

for k in k_values:
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, X, y, cv=skf, scoring='f1')
    k_scores.append(scores.mean())
```

**Ναι, ο κώδικας είναι σωστός — το scaling γίνεται με τον σωστό τρόπο σε ΚΑΘΕ fold, χωρίς data leakage.** Τα ίδια τα scikit-learn docs χαρακτηρίζουν αυτό ακριβώς το pattern ως «*the great way to prevent data leakage*» [<sup>[pitfalls]</sup>](#ref-pitfalls):

> «*The scikit-learn pipeline is a great way to prevent data leakage as it ensures that the appropriate method is performed on the correct data subset. The pipeline is ideal for use in cross-validation and hyper-parameter tuning functions.*»

Τι συμβαίνει «κάτω από το καπό» σε κάθε fold [<sup>[pipeline]</sup>](#ref-pipeline):

1. Ο `cross_val_score` διαχωρίζει τα δεδομένα σε **train fold** και **validation fold**.
2. Καλεί `pipeline.fit(X_train_fold, y_train_fold)`. Αυτό τρέχει διαδοχικά:
   - `StandardScaler.fit_transform(X_train_fold)` — μαθαίνει `μ`, `σ` μόνο από τα δεδομένα εκπαίδευσης του fold.
   - `LogisticRegression.fit(X_train_fold_scaled, y_train_fold)`.
3. Καλεί `pipeline.predict(X_val_fold)`. Αυτό τρέχει διαδοχικά:
   - `StandardScaler.transform(X_val_fold)` — εφαρμόζει τα `μ`, `σ` του **train fold** στο validation fold.
   - `LogisticRegression.predict(...)`.

**Άρα στην ερώτησή σου: ναι, το test/validation fold *όντως* scale-άρεται — απλά με τα στατιστικά του train fold, όχι του validation fold.** Είναι ακριβώς ισοδύναμο με τη διπολική `fit_transform` / `transform` της ενότητας 1, εφαρμοσμένη αυτόματα `k` φορές (μία ανά fold). Καμία διαρροή.

### Γιατί δεν αρκεί ένα προ-scaled `X`

Αν έκανες:

```python
X_scaled = scaler.fit_transform(X)        # ❌ ΛΑΘΟΣ
scores = cross_val_score(model, X_scaled, y, cv=skf, scoring='f1')
```

ο scaler θα είχε δει **όλο** το dataset, άρα τα `μ`, `σ` που εφαρμόζονται στο train fold θα είχαν «μυριστεί» πληροφορία και από το validation fold. Είναι data leakage — διακριτικό, αλλά υπαρκτό. Το ίδιο pattern (Pipeline μέσα στη CV) είναι ο σωστός τρόπος και με `GridSearchCV` / `RandomizedSearchCV` [<sup>[pipeline]</sup>](#ref-pipeline).

---

## 3. Naive Bayes & KNN — scaling, πολυσυγγραμμικότητα, one-hot

Εδώ χρειάζεται λεπτή διάκριση γιατί οι δύο αλγόριθμοι **δεν συμπεριφέρονται το ίδιο**. Η αντίληψη ότι «και οι δύο χρειάζονται scaling, και οι δύο επηρεάζονται από πολυσυγγραμμικότητα, και στους δύο πρέπει να αφαιρέσεις μία στήλη» είναι **μερικώς λάθος**.

### 3.1 KNN (`KNeighborsClassifier` / `KNeighborsRegressor`)

| Θέμα | Απάντηση | Γιατί |
|---|---|---|
| **Scaling** | **Ναι, υποχρεωτικά** [<sup>[preprocessing]</sup>](#ref-preprocessing) | Ο KNN μετράει αποστάσεις (Euclidean by default). Στήλη με τιμές 0–100.000 (π.χ. εισόδημα) θα κυριαρχήσει εντελώς πάνω σε στήλη 0–1. Η σελίδα *Preprocessing data* του sklearn αναφέρει ρητά: *«if a feature has a variance that is orders of magnitude larger than others, it might dominate the objective function»*. |
| **Πολυσυγγραμμικότητα** | **Όχι** με την αυστηρή έννοια — αλλά οι συσχετισμένες στήλες **διαστρεβλώνουν τη γεωμετρία της απόστασης**. | Ο KNN δεν έχει συντελεστές που να γίνουν ασταθείς (όπως στη γραμμική παλινδρόμηση), οπότε η κλασική «πολυσυγγραμμικότητα» δεν εφαρμόζεται. Όμως στην Ευκλείδεια απόσταση κάθε στήλη συνεισφέρει αθροιστικά: αν δύο στήλες είναι ουσιαστικά «ίδιο σήμα», αυτό το σήμα μετράει διπλά στην απόσταση και υπερ-σταθμίζεται. Η Hastie & Tibshirani [<sup>[hastie-tibshirani]</sup>](#ref-hastie-tibshirani) δείχνουν ότι ο standard 1-NN κανόνας *«suffers from bias in high dimensions»* και προτείνουν locally adaptive Mahalanobis-style μετρική (sphering των δεδομένων). Η συνηθισμένη αντιμετώπιση στη βιβλιογραφία είναι **PCA πριν το KNN** ή χρήση **Mahalanobis distance** που «λευκαίνει» τις συσχετίσεις [<sup>[knn-wiki]</sup>](#ref-knn-wiki). |
| **One-hot: αφαίρεση μιας στήλης (`drop_first`);** | Όχι αυστηρά απαραίτητη | Δεν υπάρχει dummy variable trap (ο KNN δεν λύνει γραμμικό σύστημα με intercept). |

### 3.2 Naive Bayes

| Θέμα | Απάντηση | Γιατί |
|---|---|---|
| **Scaling** | **Όχι** [<sup>[naive-bayes]</sup>](#ref-naive-bayes) | • `GaussianNB`: η likelihood `P(x_i \| y) = (1/√(2πσ²_y)) · exp(-(x_i - μ_y)²/(2σ²_y))` υπολογίζεται **ανά feature και ανά κλάση** [<sup>[naive-bayes]</sup>](#ref-naive-bayes). Κάθε `μ_y, σ_y` εξάγεται από τη στήλη της και εφαρμόζεται μόνο σ' αυτήν, οπότε οποιαδήποτε αναβάθμιση κλίμακας απορροφάται στο fit.<br>• `MultinomialNB` / `BernoulliNB`: δουλεύουν σε counts ή binary· `StandardScaler` παράγει αρνητικές τιμές που η `MultinomialNB` δεν δέχεται καν (raise `ValueError: Negative values in data passed to MultinomialNB`) [<sup>[multinomial]</sup>](#ref-multinomial). Αν χρειαστείς scaling εδώ, χρησιμοποίησε `MinMaxScaler` ή απλώς μη scale-άρεις. |
| **Πολυσυγγραμμικότητα** | Παραβιάζει την υπόθεση ανεξαρτησίας — **αλλά** στην πράξη ο NB είναι αξιοσημείωτα ανθεκτικός | Το «naive» στην ονομασία αναφέρεται στην υπόθεση ότι όλα τα features είναι **υπό συνθήκη ανεξάρτητα δοθείσας της κλάσης** [<sup>[naive-bayes]</sup>](#ref-naive-bayes). Όταν αυτή παραβιάζεται, οι **πιθανότητες** που επιστρέφει ο NB γίνονται κακώς βαθμονομημένες (overconfident) — τα ίδια τα sklearn docs το αναφέρουν: *«[NB] is known to be a bad estimator, so the probability outputs from `predict_proba` are not to be taken too seriously»* [<sup>[naive-bayes]</sup>](#ref-naive-bayes). Οι **κατατάξεις** όμως μένουν συχνά σωστές. Το θεωρητικό υπόβαθρο για αυτή τη «έκπληξη» οφείλεται στους Domingos & Pazzani (1997), που έδειξαν ότι η περιοχή βελτιστότητας του NB υπό zero-one loss είναι πολύ μεγαλύτερη από αυτήν υπό squared loss [<sup>[domingos]</sup>](#ref-domingos). |
| **One-hot: αφαίρεση μιας στήλης;** | Όχι απαραίτητη | Δεν υπάρχει dummy variable trap. |

### 3.3 «Drop one column» στο one-hot — όχι μονόλιθος κανόνας

Η σχέση μεταξύ `OneHotEncoder(drop='first')` και του μοντέλου είναι λεπτή. Παραθέτω αυτούσιο τι λένε τα sklearn docs [<sup>[onehot]</sup>](#ref-onehot):

> «*This is useful in situations where perfectly collinear features cause problems, such as when feeding the resulting data into an **unregularized** linear regression model. **However, dropping one category breaks the symmetry of the original representation and can therefore induce a bias** in downstream models, for instance for **penalized linear classification or regression models**.*»

Η ίδια παρατήρηση είναι παλιά στη στατιστική βιβλιογραφία. Οι Gertheiss & Tutz, *Annals of Applied Statistics* 2010 [<sup>[gertheiss-tutz]</sup>](#ref-gertheiss-tutz) γράφουν ρητά: *«the shrinkage effect depends on the coding scheme that is used and the choice of the reference category. […] the estimated model is not invariant against irrelevant permutations of class labels»* (p. 2152). Δηλαδή για κάθε regularized γραμμικό μοντέλο (Ridge / Lasso / regularized logistic), το ποια κατηγορία θα αφαιρέσεις *αλλάζει* το αποτέλεσμα — και η επιλογή είναι αυθαίρετη.

Αυτό δίνει έναν πιο ακριβή πρακτικό κανόνα από το παραδοσιακό «πάντα αφαίρεσε μία στήλη»:

| Μοντέλο | Drop one column; |
|---|---|
| Unregularized linear/logistic regression (με intercept) | **Ναι** — αλλιώς dummy variable trap (perfect collinearity) |
| **Regularized** linear/logistic (Ridge, Lasso, ElasticNet, regularized LogReg) | **Όχι** — η drop εισάγει bias γιατί η implicit baseline κατηγορία τιμωρείται ασύμμετρα από τη regularization [<sup>[onehot]</sup>](#ref-onehot) |
| KNN, Naive Bayes, SVM, Decision Trees, Random Forest, XGBoost | Δεν είναι απαραίτητο. Σπαταλά μια διάσταση χωρίς να βλάπτει· κάποιοι το κρατούν για consistency. |

### 3.4 Συγκριτικός πίνακας με τα γνωστά μοντέλα του μαθήματος

| Μοντέλο | Scaling; | Πολυσυγγραμμικότητα; | Drop one column σε one-hot; |
|---|---|---|---|
| Linear / Logistic Regression (unregularized) | Όχι αυστηρά | **Ναι** (αστάθεια συντελεστών) | **Ναι** |
| Linear / Logistic Regression (Ridge/Lasso/ElasticNet) | **Ναι** (απαραίτητο, αλλιώς η ποινή είναι άνιση) | Λιγότερο σοβαρή (η regularization σταθεροποιεί) | **Όχι** [<sup>[onehot]</sup>](#ref-onehot) [<sup>[gertheiss-tutz]</sup>](#ref-gertheiss-tutz) |
| **KNN** | **Ναι, υποχρεωτικά** [<sup>[preprocessing]</sup>](#ref-preprocessing) | Όχι αλγοριθμικά — αλλά συσχέτιση φουσκώνει τη συνεισφορά στην απόσταση [<sup>[hastie-tibshirani]</sup>](#ref-hastie-tibshirani) | Όχι |
| **Naive Bayes** (Gaussian / Multinomial / Bernoulli) | **Όχι** [<sup>[naive-bayes]</sup>](#ref-naive-bayes) | Παραβιάζει την υπόθεση ανεξαρτησίας· τα scores είναι κακώς calibrated αλλά οι κατατάξεις συχνά σωστές [<sup>[domingos]</sup>](#ref-domingos) | Όχι |
| SVM (RBF, polynomial) | **Ναι, υποχρεωτικά** [<sup>[svm]</sup>](#ref-svm) | Λιγότερο ευαίσθητο | Όχι |
| Decision Tree / Random Forest / XGBoost | Όχι [<sup>[trees]</sup>](#ref-trees) | Όχι (splits, όχι γραμμικό σύστημα) | Όχι |

---

## TL;DR

1. ✅ `fit_transform` στο train + `transform` στο test → **σωστό** [<sup>[pitfalls]</sup>](#ref-pitfalls).
2. ✅ `Pipeline([scaler, model])` μέσα στο `cross_val_score` → **σωστό** [<sup>[pitfalls]</sup>](#ref-pitfalls). Το validation fold scale-άρεται κανονικά, αλλά με τα `μ`, `σ` του train fold του ίδιου fold — οπότε δεν υπάρχει data leakage.
3. ⚠️ **KNN**: ναι σε scaling [<sup>[preprocessing]</sup>](#ref-preprocessing)· για πολυσυγγραμμικότητα ισχύει η πιο ακριβής διατύπωση «η συσχέτιση διαστρεβλώνει την Ευκλείδεια απόσταση» αντί για «πολυσυγγραμμικότητα»· drop column **όχι αναγκαίο**. **Naive Bayes**: **δεν** χρειάζεται scaling [<sup>[naive-bayes]</sup>](#ref-naive-bayes)· η πολυσυγγραμμικότητα παραβιάζει την υπόθεση ανεξαρτησίας, αλλά οι κατατάξεις μένουν συχνά σωστές [<sup>[domingos]</sup>](#ref-domingos)· drop column **όχι αναγκαίο**.
4. ⚠️ Το «drop one column» σε one-hot είναι αναγκαίο **μόνο για Non
-regularized γραμμικά μοντέλα με intercept**. Για Ridge / Lasso / regularized logistic regression είναι **κακή ιδέα** — εισάγει bias [<sup>[onehot]</sup>](#ref-onehot).

---

## Πηγές / References

<a id="ref-pitfalls"></a>**[pitfalls]** scikit-learn — *Common pitfalls and recommended practices* (data leakage, scaler fit on train only, Pipeline inside cross-validation). <https://scikit-learn.org/stable/common_pitfalls.html>

<a id="ref-scaler"></a>**[scaler]** scikit-learn — `sklearn.preprocessing.StandardScaler`. <https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html>

<a id="ref-pipeline"></a>**[pipeline]** scikit-learn — `sklearn.pipeline.Pipeline`. <https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html>· βλ. και τη συνοδευτική παράγραφο για χρήση μέσα σε `cross_val_score` / `GridSearchCV` στο [<sup>[pitfalls]</sup>](#ref-pitfalls).

<a id="ref-preprocessing"></a>**[preprocessing]** scikit-learn — *Preprocessing data* user guide. <https://scikit-learn.org/stable/modules/preprocessing.html>

<a id="ref-knn-wiki"></a>**[knn-wiki]** *k-nearest neighbors algorithm* — Wikipedia (ενότητα για διανυσματικές αποστάσεις & Mahalanobis). <https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm>· βλ. επίσης Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning* (2nd ed., 2009), Chapter 13 — Prototype Methods and Nearest-Neighbors.

<a id="ref-naive-bayes"></a>**[naive-bayes]** scikit-learn — *1.9 Naive Bayes* user guide (περιλαμβάνει τους τύπους για `GaussianNB`, την ανεξαρτησία, και το σχόλιο ότι ο NB είναι «*decent classifier, but bad estimator*»). <https://scikit-learn.org/stable/modules/naive_bayes.html>

<a id="ref-multinomial"></a>**[multinomial]** scikit-learn — `sklearn.naive_bayes.MultinomialNB`. <https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html>

<a id="ref-domingos"></a>**[domingos]** Domingos, P. & Pazzani, M. (1997). *On the Optimality of the Simple Bayesian Classifier under Zero-One Loss*. **Machine Learning** 29(2-3): 103–130. DOI: [10.1023/A:1007413511361](https://doi.org/10.1023/A:1007413511361). Ηλεκτρονική έκδοση: <https://link.springer.com/article/10.1023/A:1007413511361>.

<a id="ref-onehot"></a>**[onehot]** scikit-learn — `sklearn.preprocessing.OneHotEncoder` (παράμετρος `drop`, με ρητή προειδοποίηση για bias σε penalized linear models). <https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html>

<a id="ref-svm"></a>**[svm]** scikit-learn — *1.4 Support Vector Machines* user guide (*«SVM algorithms are not scale invariant, so it is highly recommended to scale your data»*). <https://scikit-learn.org/stable/modules/svm.html>

<a id="ref-trees"></a>**[trees]** scikit-learn — *1.10 Decision Trees* user guide (*«Requires little data preparation. Other techniques often require data normalization»*). <https://scikit-learn.org/stable/modules/tree.html>

<a id="ref-hastie-tibshirani"></a>**[hastie-tibshirani]** Hastie, T. & Tibshirani, R. (1996). *Discriminant Adaptive Nearest Neighbor Classification*. **IEEE Transactions on Pattern Analysis and Machine Intelligence** 18(6): 607–616. DOI: [10.1109/34.506411](https://doi.org/10.1109/34.506411). Open PDF: <https://hastie.su.domains/Papers/dann_IEEE.pdf>.

<a id="ref-gertheiss-tutz"></a>**[gertheiss-tutz]** Gertheiss, J. & Tutz, G. (2010). *Sparse Modeling of Categorial Explanatory Variables*. **The Annals of Applied Statistics** 4(4): 2150–2180. DOI: [10.1214/10-AOAS355](https://doi.org/10.1214/10-AOAS355). Open PDF (Project Euclid): <https://projecteuclid.org/journals/annals-of-applied-statistics/volume-4/issue-4/Sparse-modeling-of-categorial-explanatory-variables/10.1214/10-AOAS355.full>.

---

# Naive Bayes
The Naive Bayes classifier implementation with support of Gaussian NB, multinomial NB and Bernoulli NB.

The implementation is in the file `naive_bayes.py`. It's functionality is shown on some aritficial digits data from `sklearn.datasets`.

The example of the invocation of the program are:

`python naive_bayes.py --classes=3 --naive_bayes_type=bernoulli`

`python naive_bayes.py --classes=3 --naive_bayes_type=multinomial`

`python naive_bayes.py --classes=3 --naive_bayes_type=gaussian`

`python naive_bayes.py --classes=10 --naive_bayes_type=gaussian --alpha=10 --seed=41`

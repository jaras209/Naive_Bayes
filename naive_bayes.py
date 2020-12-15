#!/usr/bin/env python3
import argparse

import numpy as np
import scipy.stats

import sklearn.datasets
import sklearn.model_selection

parser = argparse.ArgumentParser()
# These arguments will be set appropriately by ReCodEx, even if you change them.
parser.add_argument("--alpha", default=0.1, type=float, help="Smoothing parameter for Bernoulli and Multinomial NB")
parser.add_argument("--naive_bayes_type", default="gaussian", type=str, help="NB type to use")
parser.add_argument("--classes", default=10, type=int, help="Number of classes")
parser.add_argument("--recodex", default=False, action="store_true", help="Running in ReCodEx")
parser.add_argument("--seed", default=42, type=int, help="Random seed")
parser.add_argument("--test_size", default=0.5, type=lambda x: int(x) if x.isdigit() else float(x),
                    help="Test set size")


# If you add more arguments, ReCodEx will keep them with your default values.

def main(args):
    # Use the digits dataset.
    data, target = sklearn.datasets.load_digits(n_class=args.classes, return_X_y=True)

    # Split the dataset into a train set and a test set.
    train_data, test_data, train_target, test_target = sklearn.model_selection.train_test_split(
        data, target, test_size=args.test_size, random_state=args.seed)

    # Fit the naive Bayes classifier on the train data.
    #
    # The `args.naive_bayes_type` can be one of:
    # - "gaussian": Fit Gaussian NB, by estimating mean and variance of the input
    #   features. For variance estimation use
    #     1/N * \sum_x (x - mean)^2
    #   and additionally increase all estimated variances by `args.alpha`.
    #
    #   During prediction, compute probability density function of a Gaussian
    #   distribution using `scipy.stats.norm`, which offers `pdf` and `logpdf`
    #   methods, among others.
    #
    # - "multinomial": Multinomial NB with smoothing factor `args.alpha`.
    #
    # - "bernoulli": Bernoulli NB with smoothing factor `args.alpha`.
    #   Do not forget that Bernoulli NB works with binary data, so consider
    #   all non-zero features as ones during both estimation and prediction.
    if args.naive_bayes_type == 'gaussian':
        print("Gauss")
        means = np.zeros(shape=(args.classes, train_data.shape[1]))
        variances = np.zeros(shape=(args.classes, train_data.shape[1]))
        prior = np.zeros(shape=args.classes)
        for c in range(args.classes):
            mask = train_target == c
            c_train_data = train_data[mask]
            mean = np.mean(c_train_data, axis=0)
            variance = np.sqrt(np.mean((c_train_data - mean) ** 2, axis=0) + args.alpha)
            means[c] = mean
            variances[c] = variance
            prior[c] = c_train_data.shape[0] / train_data.shape[0]

        test_predictions = np.zeros_like(test_target)
        for i, x in enumerate(test_data):
            probabilities = prior * np.prod(scipy.stats.norm.pdf(x, loc=means, scale=variances), axis=1)
            test_predictions[i] = np.argmax(probabilities)

    elif args.naive_bayes_type == 'multinomial':
        features_sums = np.zeros(shape=(args.classes, train_data.shape[1]))
        prior = np.zeros(shape=args.classes)
        for c in range(args.classes):
            mask = train_target == c
            c_train_data = train_data[mask]
            features_sum = np.sum(c_train_data, axis=0)
            features_sums[c] = features_sum
            prior[c] = c_train_data.shape[0] / train_data.shape[0]

        probabilities = (features_sums + args.alpha) / np.sum(features_sums + args.alpha, axis=1, keepdims=True)
        weights = np.log(probabilities)
        bias = np.log(prior)

        test_predictions = np.zeros_like(test_target)
        for i, x in enumerate(test_data):
            probabilities = x @ weights.T + bias
            test_predictions[i] = np.argmax(probabilities)

    else:
        train_data[train_data != 0] = 1
        likelihoods = np.zeros(shape=(args.classes, train_data.shape[1]))
        prior = np.zeros(shape=args.classes)
        for c in range(args.classes):
            mask = train_target == c
            c_train_data = train_data[mask]
            features_sum = np.sum(c_train_data, axis=0)
            likelihoods[c] = (features_sum + args.alpha) / (c_train_data.shape[0] + 2 * args.alpha)
            prior[c] = c_train_data.shape[0] / train_data.shape[0]

        weights_1 = np.log(likelihoods / (1 - likelihoods))
        weights_2 = np.log(1 - likelihoods)
        bias = np.log(prior)

        test_predictions = np.zeros_like(test_target)
        test_data[test_data != 0] = 1
        ones = np.ones(shape=test_data.shape[1])
        for i, x in enumerate(test_data):
            probabilities = x @ weights_1.T + ones @ weights_2.T + bias
            test_predictions[i] = np.argmax(probabilities)

    test_accuracy = sklearn.metrics.accuracy_score(test_target, test_predictions)
    return test_accuracy


if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    test_accuracy = main(args)

    print("Test accuracy {:.2f}%".format(100 * test_accuracy))

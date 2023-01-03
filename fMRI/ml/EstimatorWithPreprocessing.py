from sklearn.base import BaseEstimator

class EstimatorWithPreprocessor(BaseEstimator):

    def __init__(self, 
    estimator_class=None,
    preprocessor_class=None,
    estimator = None,
    preprocessor = None,
    estimator_params={},
    preprocessor_params={},
    ):
        if estimator_class is not None and estimator is not None:
            raise ValueError("You can't specify both an estimator class and an estimator instance")
        if preprocessor_class is not None and preprocessor is not None:
            raise ValueError("You can't specify both a preprocessor class and a preprocessor instance")

        if estimator_class is not None:
            self.estimator = estimator_class(**estimator_params)
        elif estimator is not None:
            self.estimator = estimator
        else:
            raise ValueError("You must specify either an estimator class or an estimator instance")
    
        if preprocessor_class is not None:
            self.preprocessor = preprocessor_class(**preprocessor_params)
        elif preprocessor is not None:
            self.preprocessor = preprocessor
        else:
            raise ValueError("You must specify either a preprocessor class or a preprocessor instance")


    def fit(self, y, X, groups):
        """
        Fit the model to the data.

        Parameters
        ----------
        y : array-like, shape (n_samples,)
            The target values.
        X : array-like, shape (n_samples, n_features)
            The input data.
        groups : array-like, shape (n_samples,)
            The group labels.
        """
        self.preprocessor.fit(X=X, y=y)
        X_pp = self.preprocessor.transform(X)
        
        self.estimator.fit(X=X_pp, y=y, groups=groups)
        

    def score(self, X, y):
        """
        Score the model on the data.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The input data.
        y : array-like, shape (n_samples,)
            The target values.

        Returns
        -------
        score : float
            The model's score on the data.
        """
        X_pp = self.preprocessor.transform(X)
        # Score the model on the data here
        return(self.estimator.score(X_pp, y))

    def predict(self, X):
        """
        Make predictions on the data.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The input data.

        Returns
        -------
        predictions : array-like, shape (n_samples,)
            The model's predictions on the data.
        """
        X_pp = self.preprocessor.transform(X)
        # Make predictions on the data here
        return(self.estimator.score(X_pp))
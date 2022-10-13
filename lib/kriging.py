from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from typing import List, Tuple


class Precipitation:
    """Interpolates percipitation data of weather stations using kriging, also known as Gaussian process regression.
    Under suitable assumptions on the priors, kriging gives the best linear unbiased prediction (BLUP) at unsampled locations.
    """

    def fit(self, X: List[List[float]], y: List[float]):
        """Fits the model on the data provided.

        Args:
            X (List[List[float]]): List of lon, lat positions
            y (List[float]): List of precipitation in 0.1 mm per hour for corresponding position in X

        Returns:
            None

        """
        kernel = ConstantKernel(1, (1e-3, 1e3)) * RBF([0.065, 0.065], (1e-5, 1e2))  # type: ignore
        self.gpr = GaussianProcessRegressor(kernel=kernel, random_state=0).fit(X, y)

    def predict(self, X: List[List[float]]):
        """Predicts the precipitation on the specified location(s)

        Args:
            X (List[List[float]]): List of [lon, lat] position(s) you want the estimated precipitation

        Returns:
            Tuple[List[List[float]], List[float]): for each location in X the precipitation (0.1 mm) and the stabdard deviation is returned
        """
        return self.gpr.predict(X, return_std=True)

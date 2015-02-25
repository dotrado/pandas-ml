#!/usr/bin/env python

import numpy as np
import pandas as pd
import pandas.compat as compat

import sklearn.datasets as datasets
import sklearn.ensemble as ensemble

import expandas as expd
import expandas.util.testing as tm


class TestEnsemble(tm.TestCase):

    def test_objectmapper(self):
        df = expd.ModelFrame([])
        self.assertIs(df.ensemble.AdaBoostClassifier, ensemble.AdaBoostClassifier)
        self.assertIs(df.ensemble.AdaBoostRegressor, ensemble.AdaBoostRegressor)
        self.assertIs(df.ensemble.BaggingClassifier, ensemble.BaggingClassifier)
        self.assertIs(df.ensemble.BaggingRegressor, ensemble.BaggingRegressor)
        self.assertIs(df.ensemble.ExtraTreesClassifier, ensemble.ExtraTreesClassifier)
        self.assertIs(df.ensemble.ExtraTreesRegressor, ensemble.ExtraTreesRegressor)
        self.assertIs(df.ensemble.GradientBoostingClassifier, ensemble.GradientBoostingClassifier)
        self.assertIs(df.ensemble.GradientBoostingRegressor, ensemble.GradientBoostingRegressor)
        self.assertIs(df.ensemble.RandomForestClassifier, ensemble.RandomForestClassifier)
        self.assertIs(df.ensemble.RandomTreesEmbedding, ensemble.RandomTreesEmbedding)
        self.assertIs(df.ensemble.RandomForestRegressor, ensemble.RandomForestRegressor)

    def test_Regressions(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        models = ['AdaBoostRegressor', 'BaggingRegressor', 'RandomForestRegressor']
        for model in models:
            mod1 = getattr(df.ensemble, model)(random_state=self.random_state)
            mod2 = getattr(ensemble, model)(random_state=self.random_state)

            df.fit(mod1)
            mod2.fit(iris.data, iris.target)

            result = df.predict(mod1)
            expected = mod2.predict(iris.data)

            self.assertTrue(isinstance(result, pd.Series))
            self.assert_numpy_array_almost_equal(result.values, expected)

    def test_Classifications(self):
        iris = datasets.load_iris()
        df = expd.ModelFrame(iris)

        models = ['AdaBoostClassifier', 'BaggingClassifier', 'RandomForestClassifier']
        for model in models:
            mod1 = getattr(df.ensemble, model)(random_state=self.random_state)
            mod2 = getattr(ensemble, model)(random_state=self.random_state)

            df.fit(mod1)
            mod2.fit(iris.data, iris.target)

            result = df.predict(mod1)
            expected = mod2.predict(iris.data)

            self.assertTrue(isinstance(result, pd.Series))
            self.assert_numpy_array_almost_equal(result.values, expected)

    def test_partial_dependence(self):
        samples = [[0, 0, 2], [1, 0, 0]]
        labels = [0, 1]

        df = expd.ModelFrame(samples, target=labels)
        gb1 = df.ensemble.GradientBoostingClassifier(random_state=self.random_state)
        df.fit(gb1)
        result = df.ensemble.partial_dependence.partial_dependence(gb1, [0], percentiles=(0, 1),
                                                                   grid_resolution=2)

        gb2 = ensemble.GradientBoostingClassifier(random_state=self.random_state)
        gb2.fit(samples, labels)
        expected = ensemble.partial_dependence.partial_dependence(gb2, [0], X=samples, percentiles=(0, 1),
                                                                  grid_resolution=2)

        self.assertEqual(len(result), 2)
        self.assert_numpy_array_almost_equal(result[0], expected[0])
        self.assert_numpy_array_almost_equal(result[1], expected[1])

    def test_plot_partial_dependence(self):
        df = expd.ModelFrame(datasets.load_iris())
        clf = df.ensemble.GradientBoostingRegressor(n_estimators=10)
        df.fit(clf)
        """
        # ToDo: Check how to perform plotting test on travis, locally passed.
        fig, axes = df.ensemble.partial_dependence.plot_partial_dependence(clf, [0, (0, 1)])

        import matplotlib
        self.assertTrue(isinstance(fig, matplotlib.figure.Figure))
        self.assertTrue(len(axes), 2)
        self.assertTrue(isinstance(axes[0], matplotlib.axes.Axes))
        """


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)
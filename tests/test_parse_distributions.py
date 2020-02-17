# Copyright 2020 MIT Probabilistic Computing Project.
# See LICENSE.txt

from math import log

import pytest

from spn.spn import NumericalDistribution
from spn.spn import PartialSumSPN
from spn.spn import ProductSPN
from spn.spn import SumSPN

from spn.numerical import Gamma
from spn.numerical import Norm
from spn.transforms import Identity

from spn.math_util import allclose

X = Identity('X')
Y = Identity('Y')
Z = Identity('Z')

def test_mul_leaf():
    for y in [0.3 * Norm(X), Norm(X) * 0.3]:
        assert isinstance(y, PartialSumSPN)
        assert len(y.weights) == 1
        assert allclose(float(sum(y.weights)), 0.3)

def test_sum_leaf():
    # Cannot sum leaves without weights.
    with pytest.raises(TypeError):
        Norm(X) | Gamma(X, a=1)
    # Cannot sum a leaf with a partial sum.
    with pytest.raises(TypeError):
        0.3*Norm(X) | Gamma(X, a=1)
    # Cannot sum a leaf with a partial sum.
    with pytest.raises(TypeError):
        Norm(X) | 0.3*Gamma(X, a=1)
    # Wrong symbol.
    with pytest.raises(ValueError):
        0.4*Norm(X) | 0.6*Gamma(Y, a=1)
    # Sum exceeds one.
    with pytest.raises(ValueError):
        0.4*Norm(X) | 0.7*Gamma(X, a=1)

    y = 0.4*Norm(X) | 0.3*Gamma(X, a=1)
    assert isinstance(y, PartialSumSPN)
    assert len(y.weights) == 2
    assert allclose(float(y.weights[0]), 0.4)
    assert allclose(float(y.weights[1]), 0.3)

    y = 0.4*Norm(X) | 0.6*Gamma(X, a=1)
    assert isinstance(y, SumSPN)
    assert len(y.weights) == 2
    assert allclose(float(y.weights[0]), log(0.4))
    assert allclose(float(y.weights[1]), log(0.6))
    # Sum exceeds one.
    with pytest.raises(TypeError):
        y | 0.7 * Norm(X)

    y = 0.4*Norm(X) | 0.3*Gamma(X, a=1) | 0.1*Norm(X)
    assert isinstance(y, PartialSumSPN)
    assert len(y.weights) == 3
    assert allclose(float(y.weights[0]), 0.4)
    assert allclose(float(y.weights[1]), 0.3)
    assert allclose(float(y.weights[2]), 0.1)

    y = 0.4*Norm(X) | 0.3*Gamma(X, a=1) | 0.3*Norm(X)
    assert isinstance(y, SumSPN)
    assert len(y.weights) == 3
    assert allclose(float(y.weights[0]), log(0.4))
    assert allclose(float(y.weights[1]), log(0.3))
    assert allclose(float(y.weights[2]), log(0.3))

    with pytest.raises(TypeError):
        (0.3)*(0.3*Norm(X))
    with pytest.raises(TypeError):
        (0.3*Norm(X)) * (0.3)
    with pytest.raises(TypeError):
        0.3*(0.3*Norm(X) | 0.5*Norm(X))

    w = 0.3*(0.4*Norm(X) | 0.6*Norm(X))
    assert isinstance(w, PartialSumSPN)

def test_product_leaf():
    with pytest.raises(TypeError):
        0.3*Gamma(X, a=1) & Norm(X)
    with pytest.raises(TypeError):
        Norm(X) & 0.3*Gamma(X, a=1)
    with pytest.raises(ValueError):
        Norm(X) & Gamma(X, a=1)

    y = Norm(X) & Gamma(Y, a=1) & Norm(Z)
    assert isinstance(y, ProductSPN)
    assert len(y.children) == 3
    assert y.get_symbols() == frozenset([X, Y, Z])

def test_sum_of_sums():
    w = 0.3*(0.4*Norm(X) | 0.6*Norm(X)) | 0.7*(0.1*Norm(X) | 0.9*Norm(X))
    assert isinstance(w, SumSPN)
    assert len(w.children) == 2
    assert allclose(float(w.weights[0]), log(0.3))
    assert allclose(float(w.weights[1]), log(0.7))
    assert allclose(float(w.children[0].weights[0]), log(0.4))
    assert allclose(float(w.children[0].weights[1]), log(0.6))
    assert allclose(float(w.children[1].weights[0]), log(0.1))
    assert allclose(float(w.children[1].weights[1]), log(0.9))

    w = 0.3*(0.4*Norm(X) | 0.6*Norm(X)) | 0.2*(0.1*Norm(X) | 0.9*Norm(X))
    assert isinstance(w, PartialSumSPN)
    assert allclose(float(w.weights[0]), 0.3)
    assert allclose(float(w.weights[1]), 0.2)

    a = w | 0.5*(Gamma(X, a=1))
    assert isinstance(a, SumSPN)
    assert isinstance(a.children[0], SumSPN)
    assert isinstance(a.children[1], SumSPN)
    assert isinstance(a.children[2], NumericalDistribution)

    # Wrong symbol.
    with pytest.raises(ValueError):
        z = w | 0.4*(Gamma(Y, a=1))

def test_or_and():
    with pytest.raises(ValueError):
        (0.3*Norm(X) | 0.7*Gamma(Y, a=1)) & Norm(Z)
    a = (0.3*Norm(X) | 0.7*Gamma(X, a=1)) & Norm(Z)
    assert isinstance(a, ProductSPN)
    assert isinstance(a.children[0], SumSPN)
    assert isinstance(a.children[1], NumericalDistribution)

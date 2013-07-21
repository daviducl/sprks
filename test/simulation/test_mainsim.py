from sim.simulation import *
import numpy
from numpy import genfromtxt
from models.pw_policy import pw_policy_model


class TestPolicyConstructor:
    """
    Tests whether calling the __init__(self, policies) constructor has same effect as calling __init__(self) and loading
     policies explicitly.
    """

    def setup_method(self, method):
        policy_set = {'plen': 12, 'psets': 4, 'pdict': 1, 'phist': 3, 'prenew': 3, 'pattempts': 1, 'pautorecover': 0}
        self.multi_policy = simulation()
        self.multi_policy.set_multi_policy(policy_set)

        self.impl_policy = simulation(policy_set)

    def test_calc_risk_prob(self):
        assert self.impl_policy.calc_risk_prob() == self.multi_policy.calc_risk_prob()

    def test_calc_risk_impact(self):
        assert self.impl_policy.calc_risk_impact() == self.multi_policy.calc_risk_impact()

    def test_calc_prod_cost(self):
        assert self.impl_policy.calc_prod_cost() == self.multi_policy.calc_prod_cost()

    def test_default_in_range(self):
        """ The default values need to be valid, as per possible ranges
        """
        for key in pw_policy_model.ranges.iterkeys():
            assert pw_policy_model.default[key] in pw_policy_model.ranges[key]

class TestSetPolicy:
    """
    Tests whether loading multiple policies in dict is same as loading each policy separately.
    """

    def setup_method(self, method):
        policy_set = {'plen': 12, 'psets': 4, 'pdict': 1, 'phist': 3, 'prenew': 3, 'pattempts': 1, 'pautorecover': 0}
        self.multi_policy = simulation()
        self.multi_policy.set_multi_policy(policy_set)

        self.policy = simulation()
        self.policy.set_policy('plen', 12)
        self.policy.set_policy('psets', 4)
        self.policy.set_policy('pdict', 1)
        self.policy.set_policy('phist', 3)
        self.policy.set_policy('prenew', 3)
        self.policy.set_policy('pattempts', 1)
        self.policy.set_policy('pautorecover', 0)

    def test_calc_risk_prob(self):
        assert self.policy.calc_risk_prob() == self.multi_policy.calc_risk_prob()

    def test_calc_risk_impact(self):
        assert self.policy.calc_risk_impact() == self.multi_policy.calc_risk_impact()

    def test_calc_prod_cost(self):
        assert self.policy.calc_prod_cost() == self.multi_policy.calc_prod_cost()


class TestMaxSec:
    """
    Tests the values for maximum security.
    """
class TestEstimators:
    def test_sklearn_tree(self):
        """Doesn't work because tool converts data in constructor
        """
        result = self.tool.predict(self.train_data)
        delta = numpy.max(numpy.abs(result - self.train_result))
        assert delta < self.eps

    def setup_method(self, method):
        self.policy = simulation()
        self.policy.set_policy('plen', 12)
        self.policy.set_policy('psets', 4)
        self.policy.set_policy('pdict', 1)
        self.policy.set_policy('phist', 3)
        self.policy.set_policy('prenew', 3)
        self.policy.set_policy('pattempts', 1)
        self.policy.set_policy('pautorecover', 0)

    def test_calc_risk_prob(self):
        pass
        # OBSOLETE
        # assert (self.policy.calc_risk_prob() <= 1) and (self.policy.calc_risk_prob() >= 0)

    def test_calc_risk_impact(self):
        pass
        # OBSOLETE
        # assert self.policy.calc_risk_impact() == 1

    def test_calc_prod_cost(self):
        pass
        # OBSOLETE
        # assert (self.policy.calc_prod_cost() >= 0) and (self.policy.calc_prod_cost() <= 100)


class TestMinSec:
    """
    Tests the values for minimum security.
    """

    def setup_method(self, method):
        self.policy = simulation()
        self.policy.set_policy('plen', 0)
        self.policy.set_policy('psets', 1)
        self.policy.set_policy('pdict', 0)
        self.policy.set_policy('phist', 0)
        self.policy.set_policy('prenew', 0)
        self.policy.set_policy('pattempts', 0)
        self.policy.set_policy('pautorecover', 1)

    def test_calc_risk_prob(self):
        assert (self.policy.calc_risk_prob() <= 1) and (self.policy.calc_risk_prob() >= 0)

    def test_calc_risk_impact(self):
        assert self.policy.calc_risk_impact() == 1

    def test_calc_prod_cost(self):
        assert (self.policy.calc_prod_cost() >= 0) and (self.policy.calc_prod_cost() <= 1)

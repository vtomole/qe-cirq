import numpy as np
import pytest
from cirq import depolarize
from openfermion.ops import QubitOperator
from qecirq.simulator import CirqSimulator
from zquantum.core.circuits import CNOT, Circuit, H, X
from zquantum.core.interfaces.backend_test import (
    QuantumSimulatorGatesTest,
    QuantumSimulatorTests,
)


@pytest.fixture()
def backend():
    return CirqSimulator()


@pytest.fixture()
def wf_simulator():
    return CirqSimulator()


@pytest.fixture()
def sampling_simulator():
    return CirqSimulator()


class TestCirqSimulator(QuantumSimulatorTests):
    def test_setup_basic_simulators(self):
        simulator = CirqSimulator()
        assert isinstance(simulator, CirqSimulator)
        assert simulator.noise_model is None

    def test_run_circuit_and_measure(self):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        simulator = CirqSimulator()
        measurements = simulator.run_circuit_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0)

    def test_measuring_inactive_qubits(self):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)], n_qubits=4)
        simulator = CirqSimulator()
        measurements = simulator.run_circuit_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0, 0)

    def test_run_circuitset_and_measure(self):
        # Given
        simulator = CirqSimulator()
        circuit = Circuit([X(0), CNOT(1, 2)])
        n_circuits = 5
        n_samples = 100
        # When
        measurements_set = simulator.run_circuitset_and_measure(
            [circuit] * n_circuits, n_samples=[100] * n_circuits
        )
        # Then
        assert len(measurements_set) == n_circuits
        for measurements in measurements_set:
            assert len(measurements.bitstrings) == n_samples
            for measurement in measurements.bitstrings:
                assert measurement == (1, 0, 0)

    def test_get_wavefunction(self):
        # Given
        simulator = CirqSimulator()
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])

        # When
        wavefunction = simulator.get_wavefunction(circuit)
        # Then
        assert isinstance(wavefunction.amplitudes, np.ndarray)
        assert len(wavefunction.amplitudes) == 8
        assert np.isclose(
            wavefunction.amplitudes[0], (1 / np.sqrt(2) + 0j), atol=10e-15
        )
        assert np.isclose(
            wavefunction.amplitudes[7], (1 / np.sqrt(2) + 0j), atol=10e-15
        )

    def test_get_exact_expectation_values(self):
        # Given
        simulator = CirqSimulator()
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        qubit_operator = QubitOperator("2[] - [Z0 Z1] + [X0 X2]")
        target_values = np.array([2.0, -1.0, 0.0])

        # When

        expectation_values = simulator.get_exact_expectation_values(
            circuit, qubit_operator
        )
        # Then
        np.testing.assert_array_almost_equal(expectation_values.values, target_values)

    def test_get_noisy_exact_expectation_values(self):
        # Given
        noise = 0.0002
        noise_model = depolarize(p=noise)
        simulator = CirqSimulator(noise_model=noise_model)
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        qubit_operator = QubitOperator("-[Z0 Z1] + [X0 X2]")
        target_values = np.array([-0.9986673775881747, 0.0])

        expectation_values = simulator.get_exact_noisy_expectation_values(
            circuit, qubit_operator
        )
        np.testing.assert_almost_equal(expectation_values.values[0], target_values[0])
        np.testing.assert_almost_equal(expectation_values.values[1], target_values[1])

    def test_run_circuit_and_measure_seed(self):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        simulator1 = CirqSimulator(seed=12)
        simulator2 = CirqSimulator(seed=12)

        # When
        measurements1 = simulator1.run_circuit_and_measure(circuit, n_samples=1000)
        measurements2 = simulator2.run_circuit_and_measure(circuit, n_samples=1000)

        # Then
        for (meas1, meas2) in zip(measurements1.bitstrings, measurements2.bitstrings):
            assert meas1 == meas2

    def test_get_wavefunction_seed(self):
        # Given
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        simulator1 = CirqSimulator(seed=542)
        simulator2 = CirqSimulator(seed=542)

        # When
        wavefunction1 = simulator1.get_wavefunction(circuit)
        wavefunction2 = simulator2.get_wavefunction(circuit)

        # Then
        for (ampl1, ampl2) in zip(wavefunction1.amplitudes, wavefunction2.amplitudes):
            assert ampl1 == ampl2


class TestCirqSimulatorGates(QuantumSimulatorGatesTest):
    pass

# data_containers.py

import numpy as np

import sc_qubits.settings as config
import sc_qubits.utils.constants as constants
import sc_qubits.utils.plotting as plot

from sc_qubits.utils.constants import FileType
from sc_qubits.utils.spectrum_utils import convert_esys_to_ndarray
from sc_qubits.utils.file_write import filewrite_csvdata, filewrite_h5data


# —WaveFunction class———————————————————————————————————————————————————————————————————————————————————————————————————

class WaveFunction(object):
    """Container for wave function amplitudes defined for a specific basis. Optionally, a corresponding
    energy is saved as well.

    Parameters
    ----------
    basis_labels: ndarray
        labels of basis states; for example, in position basis: values of position variable
    amplitudes: ndarray
        wave function amplitudes for each basis label value
    energy: float, optional
        energy of the wave function
    """

    def __init__(self, basis_labels, amplitudes, energy=None):
        self.basis_labels = basis_labels
        self.amplitudes = amplitudes
        self.energy = energy


# —WaveFunctionOnGrid class—————————————————————————————————————————————————————————————————————————————————————————————

class WaveFunctionOnGrid(object):
    """Container for wave function amplitudes defined on a coordinate grid (arbitrary dimensions).
    Optionally, a corresponding eigenenergy is saved as well.

    Parameters
    ----------
    gridspec: GridSpec object
        grid specifications for the stored wave function
    amplitudes: ndarray
        wave function amplitudes on each grid point
    energy: float, optional
        energy corresponding to the wave function
    """

    def __init__(self, gridspec, amplitudes, energy=None):
        self.gridspec = gridspec
        self.amplitudes = amplitudes
        self.energy = energy


# —SpectrumData class———————————————————————————————————————————————————————————————————————————————————————————————————

class SpectrumData(object):
    """Container holding energy and state data as a function of a particular parameter that is varied.
    Also stores all other system parameters used for generating the set, and provides method for writing
    data to file.

    Parameters
    ----------
    param_name: str
        name of parameter being varies
    param_vals: ndarray
        parameter values for which spectrum data are stored
    energy_table: ndarray
        energy eigenvalues stored for each `param_vals` point
    system_params: dict(str)
        info about system parameters
    state_table: ndarray, optional
        eigenstate data stored for each `param_vals` point, either as pure ndarray or ndarray of qutip.qobj
    matrixelem_table: ndarray, optional
        matrix element data stored for each `param_vals` point
    """

    def __init__(self, param_name, param_vals, energy_table, system_params, state_table=None, matrixelem_table=None):
        self.param_name = param_name
        self.param_vals = param_vals
        self.energy_table = energy_table
        self.state_table = state_table
        self.matrixelem_table = matrixelem_table
        self.system_params = system_params

    def plot_evals_vs_paramvals(self, xrange=None, yrange=None, fig_ax=None, **kwargs):
        """Plots eigenvalues of as a function of one parameter, as stored in SpectrumData object.

        Parameters
        ----------
        xrange: tuple(float, float), optional
             (Default value = None)
        yrange: tuple(float, float), optional
             (Default value = None)
        fig_ax: Figure, Axes, optional
             (Default value = None)
        **kwargs: optional
            keyword arguments passed on to axes.plot()

        Returns
        -------
        Figure, Axes
        """
        return plot.evals_vs_paramvals(self, xlim=xrange, ylim=yrange, fig_ax=fig_ax, **kwargs)

    def filewrite(self, filename):
        """Write data of eigenenergies, eigenstates, and matrix elements to file with specified filename.

        Parameters
        ----------
        filename: str
            path and name of output file (file suffix appended automatically)
        """

        if isinstance(self.state_table, list):
            state_table_numpy = np.asarray([convert_esys_to_ndarray(esys_qutip) for esys_qutip in self.state_table])
        elif isinstance(self.state_table, np.ndarray):
            state_table_numpy = self.state_table
        else:
            raise TypeError('state_table argument to SpectrumData is neither a pure ndarray, nor a list of eigenstates'
                            'obtained via qutip.')

        if config.file_format is FileType.csv:
            filewrite_csvdata(filename + '_' + self.param_name, self.param_vals)
            filewrite_csvdata(filename + '_energies', self.energy_table)
            if self.state_table:
                filewrite_csvdata(filename + '_states', state_table_numpy)
            if self.matrixelem_table:
                filewrite_csvdata(filename + '_melem', self.matrixelem_table)
            with open(filename + constants.PARAMETER_FILESUFFIX, 'w') as target_file:
                target_file.write(self.system_params)
        elif config.file_format is FileType.h5:
            filewrite_h5data(filename, [self.param_vals, self.energy_table, state_table_numpy, self.matrixelem_table],
                             [self.param_name, "spectrum energies", "states", "mat_elem"], self.system_params)
        return None
# Copyright (C) 2011 Atsushi Togo
# All rights reserved.
#
# This file is part of phonopy.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# * Neither the name of the phonopy project nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys
import numpy as np
from phonopy.phonon.tetrahedron_mesh import TetrahedronMesh
from phonopy.structure.tetrahedron_method import TetrahedronMethod


def get_pdos_indices(symmetry):
    mapping = symmetry.get_map_atoms()
    return [list(np.where(mapping == i)[0])
            for i in symmetry.get_independent_atoms()]


def write_total_dos(frequency_points,
                    total_dos,
                    comment=None,
                    filename="total_dos.dat"):
    with open(filename, 'w') as fp:
        if comment is not None:
            fp.write("# %s\n" % comment)

        for freq, dos in zip(frequency_points, total_dos):
            fp.write("%20.10f%20.10f\n" % (freq, dos))


def write_partial_dos(frequency_points,
                      partial_dos,
                      comment=None,
                      filename="partial_dos.dat"):
    with open(filename, 'w') as fp:
        if comment is not None:
            fp.write("# %s\n" % comment)

        for freq, pdos in zip(frequency_points, partial_dos.T):
            fp.write("%20.10f" % freq)
            fp.write(("%20.10f" * len(pdos)) % tuple(pdos))
            fp.write("\n")


def plot_total_dos(ax,
                   frequency_points,
                   total_dos,
                   freq_Debye=None,
                   Debye_fit_coef=None,
                   xlabel=None,
                   ylabel=None,
                   draw_grid=True,
                   flip_xy=False):
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_tick_params(which='both', direction='in')
    ax.yaxis.set_tick_params(which='both', direction='in')

    if freq_Debye is not None:
        freq_pitch = frequency_points[1] - frequency_points[0]
        num_points = int(freq_Debye / freq_pitch)
        freqs = np.linspace(0, freq_Debye, num_points + 1)

    if flip_xy:
        ax.plot(total_dos, frequency_points, 'r-', linewidth=1)
        if freq_Debye:
            ax.plot(np.append(Debye_fit_coef * freqs**2, 0),
                    np.append(freqs, freq_Debye), 'b-', linewidth=1)
    else:
        ax.plot(frequency_points, total_dos, 'r-', linewidth=1)
        if freq_Debye:
            ax.plot(np.append(freqs, freq_Debye),
                    np.append(Debye_fit_coef * freqs**2, 0), 'b-', linewidth=1)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.grid(draw_grid)


def plot_partial_dos(ax,
                     frequency_points,
                     partial_dos,
                     total_dos_bool=True,
                     indices=None,
                     legend=None,
                     xlabel=None,
                     ylabel=None,
                     draw_grid=True,
                     flip_xy=False):
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_tick_params(which='both', direction='in')
    ax.yaxis.set_tick_params(which='both', direction='in')

    plots = []
    natoms = len(partial_dos)

    if indices is None:
        indices = list(np.arange(natoms))

    if total_dos_bool:
        total_dos = 0
    pdos_ind = 0
    for set_for_sum in indices:
        pdos_sum = np.zeros_like(frequency_points)
        for i in set_for_sum:
            if i > natoms - 1:
                print("Index number \'%d\' is specified," % (i + 1))
                print("but it is not allowed to be larger than the number of "
                      "atoms.")
                raise ValueError
            if i < 0:
                print("Index number \'%d\' is specified, but it must be "
                      "positive." % (i + 1))
                raise ValueError
            pdos_sum += partial_dos[i]
        if total_dos_bool:
            total_dos += pdos_sum
        if flip_xy:
            if legend is not None:
                plots.append(ax.plot(pdos_sum, frequency_points, label=legend[pdos_ind]))#, linewidth=1))
            else:
                plots.append(ax.plot(pdos_sum, frequency_points))#, linewidth=1))
        else:
            if legend is not None:
                plots.append(ax.plot(frequency_points, pdos_sum, label=legend[pdos_ind]))#, linewidth=1))
            else:
                plots.append(ax.plot(frequency_points, pdos_sum))#, linewidth=1))
        pdos_ind += 1
    if total_dos_bool:
        if flip_xy:
            plots.append(ax.fill_between(total_dos, frequency_points, color='k', alpha=0.3))
        else:
            plots.append(ax.fill_betweenx(total_dos, frequency_points, color='k', alpha=0.3))

    if legend is not None:
        ax.legend()

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.axvline(0, c='k', linewidth=0.5)
    ax.axhline(0, c='k', linewidth=0.5)
    ax.grid(draw_grid)

def get_pdos(
    ax,
    partial_dos,
    indices=None,
    ):
    natoms = len(partial_dos)

    if indices is None:
        indices = list(np.arange(natoms))

    pdos_list = []
    for set_for_sum in indices:
        pdos_sum = 0
        for i in set_for_sum:
            if i > natoms - 1:
                print("Index number \'%d\' is specified," % (i + 1))
                print("but it is not allowed to be larger than the number of "
                      "atoms.")
                raise ValueError
            if i < 0:
                print("Index number \'%d\' is specified, but it must be "
                      "positive." % (i + 1))
                raise ValueError
            pdos_sum += partial_dos[i]
        pdos_list.append(pdos_sum)
    return pdos_list

class NormalDistribution(object):
    def __init__(self, sigma):
        self._sigma = sigma

    def calc(self, x):
        return 1.0 / np.sqrt(2 * np.pi) / self._sigma * \
            np.exp(-x**2 / 2.0 / self._sigma**2)


class CauchyDistribution(object):
    def __init__(self, gamma):
        self._gamma = gamma

    def calc(self, x):
        return self._gamma / np.pi / (x**2 + self._gamma**2)


def run_tetrahedron_method_dos(mesh,
                               frequency_points,
                               frequencies,
                               grid_address,
                               grid_mapping_table,
                               relative_grid_address,
                               coef=None):  # for each grid point
    try:
        import phonopy._phonopy as phonoc
    except ImportError:
        import sys
        print("Phonopy C-extension has to be built properly.")
        sys.exit(1)

    if coef is None:
        _coef = np.ones((frequencies.shape[0], 1, frequencies.shape[1]),
                        dtype='double')
    else:
        _coef = np.array(coef, dtype='double', order='C')
    arr_shape = frequencies.shape + (len(frequency_points), _coef.shape[1])
    dos = np.zeros(arr_shape, dtype=np.float64)

    phonoc.tetrahedron_method_dos(dos,
                                  mesh,
                                  frequency_points,
                                  frequencies,
                                  _coef,
                                  grid_address,
                                  grid_mapping_table,
                                  relative_grid_address)
    if coef is None:
        return dos[:, :, :, 0].sum(axis=0).sum(axis=0) / np.prod(mesh)
    else:
        return dos.sum(axis=0).sum(axis=0) / np.prod(mesh)


class Dos(object):
    def __init__(self, mesh_object, sigma=None, use_tetrahedron_method=False):
        self._mesh_object = mesh_object
        self._frequencies = mesh_object.frequencies
        self._weights = mesh_object.weights
        if use_tetrahedron_method and sigma is None:
            self._tetrahedron_mesh = TetrahedronMesh(
                mesh_object.dynamical_matrix.primitive,
                self._frequencies,
                mesh_object.mesh_numbers,
                mesh_object.grid_address,
                mesh_object.grid_mapping_table,
                mesh_object.ir_grid_points)
        else:
            self._tetrahedron_mesh = None

        self._frequency_points = None
        self._sigma = sigma
        self.set_draw_area()
        self.set_smearing_function('Normal')

    @property
    def frequency_points(self):
        return self._frequency_points

    def set_smearing_function(self, function_name):
        """
        function_name ==
        'Normal': smearing is done by normal distribution.
        'Cauchy': smearing is done by Cauchy distribution.
        """
        if function_name == 'Cauchy':
            self._smearing_function = CauchyDistribution(self._sigma)
        else:
            self._smearing_function = NormalDistribution(self._sigma)

    def set_sigma(self, sigma):
        self._sigma = sigma

    def set_draw_area(self,
                      freq_min=None,
                      freq_max=None,
                      freq_pitch=None):

        f_min = self._frequencies.min()
        f_max = self._frequencies.max()

        if self._sigma is None:
            self._sigma = (f_max - f_min) / 100.0

        if freq_min is None:
            f_min -= self._sigma * 10
        else:
            f_min = freq_min

        if freq_max is None:
            f_max += self._sigma * 10
        else:
            f_max = freq_max

        if freq_pitch is None:
            f_delta = (f_max - f_min) / 200.0
        else:
            f_delta = freq_pitch
        self._frequency_points = np.arange(f_min,
                                           f_max + f_delta * 0.1,
                                           f_delta)


class TotalDos(Dos):
    def __init__(self, mesh_object, sigma=None, use_tetrahedron_method=False):
        Dos.__init__(self,
                     mesh_object,
                     sigma=sigma,
                     use_tetrahedron_method=use_tetrahedron_method)
        self._dos = None
        self._freq_Debye = None
        self._Debye_fit_coef = None
        self._openmp_thm = True

    def run(self):
        if self._tetrahedron_mesh is None:
            self._dos = np.array([self._get_density_of_states_at_freq(f)
                                  for f in self._frequency_points])
        else:
            if self._openmp_thm:
                self._run_tetrahedron_method_dos()
            else:
                self._dos = np.zeros_like(self._frequency_points)
                thm = self._tetrahedron_mesh
                thm.set(value='I', frequency_points=self._frequency_points)
                for i, iw in enumerate(thm):
                    self._dos += np.sum(iw * self._weights[i], axis=1)

    @property
    def dos(self):
        return self._dos

    def get_dos(self):
        """
        Return freqs and total dos
        """
        return self._frequency_points, self._dos

    def get_Debye_frequency(self):
        return self._freq_Debye

    def set_Debye_frequency(self, num_atoms, freq_max_fit=None):
        try:
            from scipy.optimize import curve_fit
        except ImportError:
            print("You need to install python-scipy.")
            sys.exit(1)

        def Debye_dos(freq, a):
            return a * freq**2

        freq_min = self._frequency_points.min()
        freq_max = self._frequency_points.max()

        if freq_max_fit is None:
            N_fit = int(len(self._frequency_points) / 4.0)  # Hard coded
        else:
            N_fit = int(freq_max_fit / (freq_max - freq_min) *
                        len(self._frequency_points))
        popt, pcov = curve_fit(Debye_dos,
                               self._frequency_points[0:N_fit],
                               self._dos[0:N_fit])
        a2 = popt[0]
        self._freq_Debye = (3 * 3 * num_atoms / a2)**(1.0 / 3)
        self._Debye_fit_coef = a2

    def plot(self,
             ax,
             xlabel=None,
             ylabel=None,
             draw_grid=True,
             flip_xy=False):
        if flip_xy:
            _xlabel = 'Density of states'
            _ylabel = 'Frequency'
        else:
            _xlabel = 'Frequency'
            _ylabel = 'Density of states'

        if xlabel is not None:
            _xlabel = xlabel
        if ylabel is not None:
            _ylabel = ylabel

        plot_total_dos(ax,
                       self._frequency_points,
                       self._dos,
                       freq_Debye=self._freq_Debye,
                       Debye_fit_coef=self._Debye_fit_coef,
                       xlabel=_xlabel,
                       ylabel=_ylabel,
                       draw_grid=draw_grid,
                       flip_xy=flip_xy)

    def write(self, filename="total_dos.dat"):
        if self._tetrahedron_mesh is None:
            comment = "Sigma = %f" % self._sigma
        else:
            comment = "Tetrahedron method"

        write_total_dos(self._frequency_points,
                        self._dos,
                        comment=comment,
                        filename=filename)

    def _run_tetrahedron_method_dos(self):
        mesh_numbers = self._mesh_object.mesh_numbers
        cell = self._mesh_object.dynamical_matrix.primitive
        reciprocal_lattice = np.linalg.inv(cell.get_cell())
        tm = TetrahedronMethod(reciprocal_lattice, mesh=mesh_numbers)
        self._dos = run_tetrahedron_method_dos(
            mesh_numbers,
            self._frequency_points,
            self._frequencies,
            self._mesh_object.grid_address,
            self._mesh_object.grid_mapping_table,
            tm.get_tetrahedra())

    def _get_density_of_states_at_freq(self, f):
        return np.sum(np.dot(
            self._weights, self._smearing_function.calc(self._frequencies - f))
        ) / np.sum(self._weights)


class PartialDos(Dos):
    def __init__(self,
                 mesh_object,
                 sigma=None,
                 use_tetrahedron_method=False,
                 direction=None,
                 xyz_projection=False):
        Dos.__init__(self,
                     mesh_object,
                     sigma=sigma,
                     use_tetrahedron_method=use_tetrahedron_method)
        self._eigenvectors = self._mesh_object.eigenvectors
        self._partial_dos = None

        if xyz_projection:
            self._eigvecs2 = np.abs(self._eigenvectors) ** 2
        else:
            num_atom = self._frequencies.shape[1] // 3
            i_x = np.arange(num_atom, dtype='int') * 3
            i_y = np.arange(num_atom, dtype='int') * 3 + 1
            i_z = np.arange(num_atom, dtype='int') * 3 + 2
            if direction is None:
                self._eigvecs2 = np.abs(self._eigenvectors[:, i_x, :]) ** 2
                self._eigvecs2 += np.abs(self._eigenvectors[:, i_y, :]) ** 2
                self._eigvecs2 += np.abs(self._eigenvectors[:, i_z, :]) ** 2
            else:
                d = np.array(direction, dtype='double')
                d /= np.linalg.norm(direction)
                proj_eigvecs = self._eigenvectors[:, i_x, :] * d[0]
                proj_eigvecs += self._eigenvectors[:, i_y, :] * d[1]
                proj_eigvecs += self._eigenvectors[:, i_z, :] * d[2]
                self._eigvecs2 = np.abs(proj_eigvecs) ** 2

        self._openmp_thm = True

    @property
    def partial_dos(self):
        return self._partial_dos

    @property
    def projected_dos(self):
        return self._partial_dos

    def run(self):
        if self._tetrahedron_mesh is None:
            self._run_smearing_method()
        else:
            ## Disabled due to memory issue
            # if self._openmp_thm:
                # self._run_tetrahedron_method_dos()
            # else:
            self._run_tetrahedron_method()

    def get_partial_dos(self):
        """
        frequency_points: Sampling frequencies
        partial_dos: [atom_index, frequency_points_index]
        """
        return self._frequency_points, self._partial_dos

    def plot(self,
             ax,
             indices=None,
             legend=None,
             total_dos_bool=True,
             xlabel=None,
             ylabel=None,
             draw_grid=True,
             flip_xy=False):

        if flip_xy:
            _xlabel = 'Partial density of states'
            _ylabel = 'Frequency'
        else:
            _xlabel = 'Frequency'
            _ylabel = 'Partial density of states'

        if xlabel is not None:
            _xlabel = xlabel
        if ylabel is not None:
            _ylabel = ylabel

        plot_partial_dos(ax,
                         self._frequency_points,
                         self._partial_dos,
                         total_dos_bool,
                         indices=indices,
                         legend=legend,
                         xlabel=_xlabel,
                         ylabel=_ylabel,
                         draw_grid=draw_grid,
                         flip_xy=flip_xy)

    def write(self, filename="partial_dos.dat"):
        if self._tetrahedron_mesh is None:
            comment = "Sigma = %f" % self._sigma
        else:
            comment = "Tetrahedron method"

        write_partial_dos(self._frequency_points,
                          self._partial_dos,
                          comment=comment,
                          filename=filename)

    def _run_smearing_method(self):
        num_pdos = self._eigvecs2.shape[1]
        num_freqs = len(self._frequency_points)
        self._partial_dos = np.zeros((num_pdos, num_freqs), dtype='double')
        weights = self._weights / float(np.sum(self._weights))
        for i, freq in enumerate(self._frequency_points):
            amplitudes = self._smearing_function.calc(self._frequencies - freq)
            for j in range(self._partial_dos.shape[0]):
                self._partial_dos[j, i] = np.dot(
                    weights, self._eigvecs2[:, j, :] * amplitudes).sum()

    def _run_tetrahedron_method(self):
        num_pdos = self._eigvecs2.shape[1]
        num_freqs = len(self._frequency_points)
        self._partial_dos = np.zeros((num_pdos, num_freqs), dtype='double')
        thm = self._tetrahedron_mesh
        thm.set(value='I', frequency_points=self._frequency_points)
        for i, iw in enumerate(thm):
            w = self._weights[i]
            self._partial_dos += np.dot(iw * w, self._eigvecs2[i].T).T

    def _run_tetrahedron_method_dos(self):
        mesh_numbers = self._mesh_object.mesh_numbers
        cell = self._mesh_object.dynamical_matrix.primitive
        reciprocal_lattice = np.linalg.inv(cell.get_cell())
        tm = TetrahedronMethod(reciprocal_lattice, mesh=mesh_numbers)
        pdos = run_tetrahedron_method_dos(
            mesh_numbers,
            self._frequency_points,
            self._frequencies,
            self._mesh_object.grid_address,
            self._mesh_object.grid_mapping_table,
            tm.get_tetrahedra(),
            coef=self._eigvecs2)
        self._partial_dos = pdos.T

# Copyright (C) 2024 David Cattermole
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
The main component of the user interface for the image cache
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets
import mmSolver.ui.Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.tools.imagecache.ui.ui_imagecache_layout as ui_imagecache_layout
import mmSolver.tools.imagecache.lib as lib


LOG = mmSolver.logger.get_logger()


# Memory Conversion
_BYTES_TO_KILOBYTES = 1024  # int(pow(2, 10))
_BYTES_TO_MEGABYTES = 1048576  # int(pow(2, 20))
_BYTES_TO_GIGABYTES = 1073741824  # int(pow(2, 30))
_KILOBYTES_TO_MEGABYTES = 1024  # int(pow(2, 10))
_KILOBYTES_TO_GIGABYTES = 1048576  # int(pow(2, 20))


def memoryTotalUpdateUi(
    label,
    size_bytes,
):
    gigabytes = 0.0
    if size_bytes > 0:
        gigabytes = size_bytes / _BYTES_TO_GIGABYTES
    text = '<b>{:0,.2f} GB</b>'.format(gigabytes)
    label.setText(text)


def memoryUsedUpdateUi(label, used_size_bytes, total_size_bytes):
    used_gigabytes = 0.0
    if used_size_bytes > 0:
        used_gigabytes = used_size_bytes / _BYTES_TO_GIGABYTES

    used_percent = 0.0
    if used_size_bytes > 0 and total_size_bytes > 0:
        used_percent = (used_size_bytes / total_size_bytes) * 100.0
    text = '<b>{:0,.2f} GB ({:3.1f}%)</b>'.format(used_gigabytes, used_percent)
    label.setText(text)


def cacheItemCountUpdateUi(
    label,
    value,
):
    text = '<b>{:,}</b>'.format(value)
    label.setText(text)


def cacheCapacityUpdateUi(
    label,
    size_bytes,
):
    gigabytes = 0.0
    if size_bytes > 0:
        gigabytes = size_bytes / _BYTES_TO_GIGABYTES
    text = '<b>{:0,.2f} GB</b>'.format(gigabytes)
    label.setText(text)


def cacheUsedUpdateUi(label, used_size_bytes, capacity_size_bytes):
    used_gigabytes = 0.0
    if used_size_bytes > 0:
        used_gigabytes = used_size_bytes / _BYTES_TO_GIGABYTES

    used_percent = 0.0
    if used_size_bytes > 0 and capacity_size_bytes > 0:
        used_percent = (used_size_bytes / capacity_size_bytes) * 100.0
    text = '<b>{:0,.2f} GB ({:3.1f}%)</b>'.format(used_gigabytes, used_percent)
    label.setText(text)


class ImageCacheLayout(QtWidgets.QWidget, ui_imagecache_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(ImageCacheLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Update timer.
        self.update_timer = QtCore.QTimer()
        seconds = 0.5
        milliseconds = int(seconds * 1000)
        self.update_timer.setInterval(milliseconds)
        self.update_timer.timeout.connect(self.updateUiValues)
        self.update_timer.start()

        # Populate the UI with data
        self.populateUi()

    def updateUiValues(self):
        LOG.debug('updateUiValues...')

        gpu_cache_item_count = lib.get_gpu_cache_item_count()
        cpu_cache_item_count = lib.get_cpu_cache_item_count()
        gpu_cache_used = lib.get_gpu_cache_used_bytes()
        cpu_cache_used = lib.get_cpu_cache_used_bytes()
        gpu_cache_capacity = lib.get_gpu_cache_capacity_bytes()
        cpu_cache_capacity = lib.get_cpu_cache_capacity_bytes()
        gpu_memory_total = lib.get_gpu_memory_total_bytes()
        cpu_memory_total = lib.get_cpu_memory_total_bytes()
        gpu_memory_used = lib.get_gpu_memory_used_bytes()
        cpu_memory_used = lib.get_cpu_memory_used_bytes()

        memoryTotalUpdateUi(self.gpuMemoryTotalValue_label, gpu_memory_total)
        memoryTotalUpdateUi(self.cpuMemoryTotalValue_label, cpu_memory_total)

        memoryUsedUpdateUi(
            self.gpuMemoryUsedValue_label, gpu_memory_used, gpu_memory_total
        )
        memoryUsedUpdateUi(
            self.cpuMemoryUsedValue_label, cpu_memory_used, cpu_memory_total
        )

        cacheItemCountUpdateUi(self.gpuCacheItemCountValue_label, gpu_cache_item_count)
        cacheItemCountUpdateUi(self.cpuCacheItemCountValue_label, cpu_cache_item_count)

        cacheCapacityUpdateUi(self.gpuCacheCapacityValue_label, gpu_cache_capacity)
        cacheCapacityUpdateUi(self.cpuCacheCapacityValue_label, cpu_cache_capacity)

        cacheUsedUpdateUi(
            self.cpuCacheUsedValue_label, cpu_cache_used, cpu_cache_capacity
        )
        cacheUsedUpdateUi(
            self.gpuCacheUsedValue_label, gpu_cache_used, gpu_cache_capacity
        )
        return

    def reset_options(self):
        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        self.updateUiValues()

        # name = const.CONFIG_WIDTH_KEY
        # value = configmaya.get_scene_option(name, default=const.DEFAULT_WIDTH)
        # LOG.debug('key=%r value=%r', name, value)
        # self.width_horizontalSlider.setValue(value)
        # self.width_spinBox.setValue(value)

        # self.gpuCacheCapacityGigaBytes_label
        # self.gpuCacheCapacity_horizontalSlider
        # self.gpuCacheCapacity_doubleSpinBox
        return

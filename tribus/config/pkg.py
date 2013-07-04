#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ==============================================================================
# PAQUETE: canaima-semilla
# ARCHIVO: scripts/c-s.sh
# DESCRIPCIÓN: Script principal. Se encarga de invocar a los demás módulos y
#              funciones según los parámetros proporcionados.
# USO: ./c-s.sh [MÓDULO] [PARÁMETROS] [...]
# COPYRIGHT:
#       (C) 2010-2012 Luis Alejandro Martínez Faneyth <luis@huntingbears.com.ve>
#       (C) 2012 Niv Sardi <xaiki@debian.org>
# LICENCIA: GPL-3
# ==============================================================================
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# COPYING file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# CODE IS POETRY

from tribus.common.utils import get_path, cat_file
from tribus.common.config import (readconfig, get_dependencies, get_repositories,
                                  get_classifiers)
from tribus.config.base import CONFDIR, DOCDIR

platforms = ('Any',),
keywords = ('backup', 'archive', 'atom', 'rss', 'blog', 'weblog'),
f_readme = get_path([DOCDIR, 'README'])
f_classifiers = get_path([CONFDIR, 'data', 'python-classifiers.list'])
f_dependencies = get_path([CONFDIR, 'data', 'python-dependencies.list'])
f_exclude_sources = get_path([CONFDIR, 'data', 'exclude-sources.list'])
f_exclude_packages = get_path([CONFDIR, 'data', 'exclude-packages.list'])
f_exclude_patterns = get_path([CONFDIR, 'data', 'exclude-patterns.list'])
f_data_patterns = get_path([CONFDIR, 'data', 'include-data-patterns.list'])

exclude_sources = readconfig(filename=f_exclude_sources, conffile=False)
exclude_packages = readconfig(filename=f_exclude_packages, conffile=False)
exclude_patterns = readconfig(filename=f_exclude_patterns, conffile=False)
include_data_patterns = readconfig(filename=f_data_patterns, conffile=False)

long_description = cat_file(f=f_readme)
classifiers = get_classifiers(f=f_classifiers)
install_requires = get_dependencies(f=f_dependencies)
dependency_links = get_repositories(f=f_dependencies)

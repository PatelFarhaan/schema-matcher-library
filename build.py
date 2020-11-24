#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin('pypi:pybuilder_pytest')
use_plugin('pypi:pybuilder_pytest_coverage')
use_plugin("python.flake8")
use_plugin("python.distutils")
use_plugin("python.install_dependencies")

name = "smtools"
default_task = ["install_dependencies", "publish"]


@init
def set_properties(project):
    project.get_property("pytest_extra_args").append("--cov-report")
    project.get_property("pytest_extra_args").append("xml:cov.xml")
    project.depends_on("pandas")
    project.depends_on("nltk")
    project.depends_on("py_stringmatching")
    project.depends_on("pyspark")

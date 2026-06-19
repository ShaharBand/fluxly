from fluxly.node import NodeExecution

from .output import LoadOutput


class LoadExecution(NodeExecution):
    output: LoadOutput = LoadOutput()

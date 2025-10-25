from fluxly.node import NodeExecution

from .output import AlphaNodeOutput


class AlphaNodeExecution(NodeExecution):
    output: AlphaNodeOutput = AlphaNodeOutput()

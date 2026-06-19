from fluxly.node import NodeExecution

from .output import TransformOutput


class TransformExecution(NodeExecution):
    output: TransformOutput = TransformOutput()

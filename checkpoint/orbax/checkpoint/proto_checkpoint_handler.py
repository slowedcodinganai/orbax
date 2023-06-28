# Copyright 2023 The Orbax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ProtoCheckpointHandler class.

Implementation of CheckpointHandler interface.
"""

from typing import Any, Optional, Type

from etils import epath
from google.protobuf import message
from google.protobuf import text_format
import jax
from orbax.checkpoint import checkpoint_handler
from orbax.checkpoint import utils


class ProtoCheckpointHandler(checkpoint_handler.CheckpointHandler):
  """Serializes/deserializes protocol buffers."""

  def __init__(self, filename: str):
    """Initializes ProtoCheckpointHandler.

    Args:
      filename: file name given to the written file.
    """
    self._filename = filename

  def save(self, directory: epath.Path, item: message.Message):
    """Saves the given proto.

    Args:
      directory: save location directory.
      item: the proto to serialize.
    """
    if jax.process_index() == 0:
      path = directory / self._filename
      path.write_text(text_format.MessageToString(item))
    utils.sync_global_devices("ProtoCheckpointHandler:save")

  def restore(
      self, directory: epath.Path, item: Optional[Type[message.Message]] = None
  ):
    """Restores the proto from directory.

    Args:
      directory: restore location directory.
      item: the proto class

    Returns:
      The deserialized proto read from `directory` if item is not None
    """
    if item is None:
      raise ValueError(
          "Must provide `item` in order to deserialize proto to the correct"
          " type."
      )
    path = directory / self._filename
    return text_format.Parse(path.read_text(), item())

  def structure(self, directory: epath.Path) -> Any:
    """Unimplemented. See parent class."""
    return NotImplementedError

# Copyright (c) 2024 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

if __name__ == '__main__':
    text_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "vec2mesh.txt")

    with open(text_path, encoding="utf-8") as t_file:
        qpe = {}
        for line in t_file:
            if line[0] == "#":
                continue
            parts = line.split()
            v = int(parts[1])
            x = int(parts[4][1])
            y = int(parts[4][3])
            p = int(parts[6])
            qpe[v] = (x, y, p)
        print(qpe)

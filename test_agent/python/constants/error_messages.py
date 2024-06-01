"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

from enum import Enum


class UAttributeBuilderErrors(Enum):
    @staticmethod
    def not_given(field_name: str):
        return f"ERROR: \"{field_name}\" field must exist"
    
    @staticmethod
    def bad_data_value(field_name: str):
        if field_name == "priority":
            return f"ERROR: \"{field_name}\" field must be int between [0, 7]"
        elif field_name == "commstatus":
            return f"ERROR: \"{field_name}\" field must be int between [0, 16]"
        else:
            return f"ERROR: same data type but bad value in \"{field_name}\" uAttribute field assignment"
    
    @staticmethod
    def bad_data_type(field_name: str):
        return f"ERROR: data type misalignment in \"{field_name}\" uAttribute field assignment"
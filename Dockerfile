# Copyright [2020] [Two Six Labs, LLC]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


FROM python:3.7.8-buster

#Set escalation as working directory
WORKDIR /escalation
ENV PYTHONPATH "${PYTHONPATH}:/escalation"

#install dependencies
RUN apt-get update
RUN apt-get install -y build-essential python3.7-dev libpq-dev
COPY escalation/requirements-app.txt /escalation
RUN pip install --trusted-host pypi.python.org -r requirements-app.txt

#copy data from current dir into container
COPY escalation /escalation
# imports for this script behave strangely- copy to workdir to prevent issues
COPY escalation/database/csv_to_sql.py /escalation

RUN chmod +x /escalation/boot.sh
RUN chmod +x /escalation/wizard_ui/boot_wizard_app.sh
RUN chmod +x /escalation/csv_to_sql.sh



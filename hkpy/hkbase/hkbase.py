# MIT License

# Copyright (c) 2019 IBM Hyperlinked Knowledge Graph

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Optional

import requests
from abc import abstractmethod

from . import HKRepository
from ..hklib import hkfy
from ..oops import HKBError, HKpyError
from ..utils import constants
from ..utils import response_validator

__all__ = ['HKBase']

class HKBase(object):
    """ This class establishes a communication interface with a hkbase.
    """

    def __init__(self, url: str, api_version: str='v2', auth: Optional[str]=None):
        """ Initialize an instance of HKBase class.
    
        Parameters
        ----------
        url: (str) HKBase url
        api_version: (str) HKBase api version
        auth: (Optional[str]) HKBase authentication token
        """
        
        self.url = url
        self.api_version = api_version
        self._base_uri = f'{self.url}/{self.api_version}'
        self._repository_uri = f'{self._base_uri}/repository'
        self._observer_uri = f'{self._base_uri}/observer'
        self._headers = {'Content-Type' : 'application/json'}
        auth = auth if auth else constants.AUTH_TOKEN
        self._headers['Authorization'] = f'Bearer {auth}'

    def connect_repository(self, name: str) -> HKRepository:
        """ Connect to existing hkbase's repository.

        Parameters
        ----------
        name : (str) name of the hkbase's respository

        Returns
        -------
        (HKRepository) Communication interface with a repository
        """

        if(name in self._view_repositories()):
            return HKRepository(base=self, name=name)

        raise HKpyError(message="Could not connect to repository.")

    def create_repository(self, name: str) -> HKRepository:
        """ Create a new repository in hkbase.

        Parameters
        ----------
        name : (str) name of the new hkbase's respository

        Returns
        -------
        (HKRepository) Communication interface with a repository
        """

        url = f'{self._repository_uri}/{name}/'

        try:
            response = requests.put(url=url, verify=constants.SSL_VERIFY, headers=self._headers)
            response_validator(response=response)
            return HKRepository(base=self, name=name)
        except HKBError as err:
            raise err
        except Exception as err:
            raise HKpyError(message='Repository not created.', error=err)
    
    def delete_repository(self, name: str) -> None:
        """ Delete a existing hkbase's repository.

        Parameters
        ----------
        name : (str) name of the new hkbase's respository
        """

        url = f'{self._repository_uri}/{name}/'

        try:
            response = requests.delete(url=url, verify=constants.SSL_VERIFY, headers=self._headers)
            response_validator(response=response)
        except HKBError as err:
            raise err
        except Exception as err:
            raise HKpyError(message='Repository not deleted.', error=err)

    def delete_create_repository(self, name: str) -> HKRepository:
        """ Delete an existing hkbase's repository and, then, recreate it.

        Parameters
        ----------
        name : (str) name of the new hkbase's respository

        Returns
        -------
        (HKRepository) Communication interface with a repository
        """

        try:
            return self.create_repository(name)
        except HKBError as err:
            self.delete_repository(name)
            return self.create_repository(name)
        except Exception as err:
            raise HKpyError(message='Repository not deleted or created.', error=err)

    def _view_repositories(self) -> List[str]:
        try:
            response = requests.get(url=self._repository_uri, verify=constants.SSL_VERIFY, headers=self._headers)
            _, repositories = response_validator(response=response)
            return repositories
        except HKBError as err:
            raise err
        except Exception as err:
            raise HKpyError(message='Could not retrieve existing repositories.', error=err)

    def get_repositories(self) -> List[HKRepository]:
        """ Retrieve avaiable repositories in the hkbase.

        Returns
        -------
        (List[HKRepository]) list of available repositories in the hkbase
        """

        try:
            response = requests.get(url=self._repository_uri, verify=constants.SSL_VERIFY, headers=self._headers)
            _, repositories = response_validator(response=response)
            
            return [self.connect_repository(name=repo) for repo in repositories]
        except HKBError as err:
            raise err
        except Exception as err:
            raise HKpyError(message='Could not retrieve existing repositories.', error=err)
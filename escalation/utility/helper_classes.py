"""
Copyright [2020] [Two Six Labs, LLC]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
"""


class NestedDict(dict):
    """
    Works just like a dictionary, except it interprets a list of keys as nesting coordinates
    """

    def __getitem__(self, key):
        # if key is not a tuple then access as normal
        if not isinstance(key, list):
            return super(NestedDict, self).__getitem__(key)
        d = self
        for key in key:
            d = d.get(key, {})
        return d

    def __setitem__(self, key, value):
        if not isinstance(key, list):
            # use the basic dict item setter
            super(NestedDict, self).__setitem__(key, value)
        else:
            # access the nested level of the key, then use dict's set item to set value
            d = self[key[:-1]]
            dict.__setitem__(d, key[-1], value)

#!/usr/bin/env python
# coding: utf-8
# Date: 2016-01-14 00:03:53

import getpass


def make_sure_input(prompt, hidden=False):
    while True:
        data = (
            getpass.getpass(prompt) if hidden
            else input(prompt)
        )
        if data:
            return data

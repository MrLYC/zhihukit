#!/usr/bin/env python
# coding: utf-8
# Date: 2016-01-13 22:30:26

from urllib.parse import urljoin

from requests import Session as RSession

__all__ = (
    "Session",
)


class Session(RSession):
    def __init__(self, base_url):
        super(Session, self).__init__()
        self.base_url = base_url

    def request(
        self, method, url, *args,
        relative=True, **kwarg
    ):
        if relative:
            url = urljoin(self.base_url, url)
        return super(Session, self).request(
            method, url, *args, **kwarg
        )

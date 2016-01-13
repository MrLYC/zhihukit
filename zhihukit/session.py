#!/usr/bin/env python
# coding: utf-8
# Date: 2016-01-13 22:30:26

from urllib.parse import urljoin

from requests import Session as RSession
from pyquery import PyQuery

from zhihukit.utils import make_sure_input

__all__ = (
    "Session", "ResponseSelector", "AuthFaildError",
)


class ResponseSelector(object):
    encoding = "utf-8"

    def __init__(self, async_response):
        super(ResponseSelector, self).__init__()
        self.async_response = async_response
        self._selector = None

    def __getattr__(self, attr):
        response = self.async_response.get()
        return getattr(response, attr)

    @property
    def selector(self):
        if not self._selector:  # not thread safe
            response = self.async_response.get()
            self._selector = PyQuery(
                response.content.decode(self.encoding)
            )
        return self._selector

    def __call__(self, select_str):
        return self.selector(select_str)


SESSION_DEFAULT_HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    'Connection': 'keep-alive',
}


class AuthFaildError(Exception):
    pass


class SessionAuthMixin(object):
    def login(self, user=None, passwd=None):
        index_page = self.get("/")
        if not user:
            user = make_sure_input("zhihu user: ")
        if not passwd:
            passwd = make_sure_input(
                "zhihu password: ", hidden=True
            )
        xsrf_tkn = index_page("input[name=_xsrf]").val()

        login_page = self.post(
            "/login/email",
            {
                "email": user,
                "password": passwd,
                "_xsrf": xsrf_tkn,
                "remember_me": "true",
            }
        )
        if login_page.status_code != 200:
            raise AuthFaildError(user)


class Session(RSession, SessionAuthMixin):
    def __init__(self, base_url, pool):
        super(Session, self).__init__()
        self.base_url = base_url
        self.headers = SESSION_DEFAULT_HEADERS.copy()
        self.pool = pool
        self.__base = super(Session, self)

    def request(
        self, method, url, *args,
        relative=True, **kwarg
    ):
        if relative:
            url = urljoin(self.base_url, url)

        async_response = self.pool.apply_async(
            self.__base.request,
            (method, url, *args), kwarg,
        )
        return ResponseSelector(async_response)

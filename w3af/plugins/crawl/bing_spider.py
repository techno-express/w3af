"""
bing_spider.py

Copyright 2006 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
from urllib2 import URLError

import w3af.core.controllers.output_manager as om

from w3af.core.controllers.plugins.crawl_plugin import CrawlPlugin
from w3af.core.controllers.exceptions import (w3afException, w3afRunOnce,
                                              w3afMustStopException)
from w3af.core.controllers.misc.is_private_site import is_private_site
from w3af.core.controllers.misc.decorators import runonce

from w3af.core.data.search_engines.bing import bing as bing
from w3af.core.data.options.opt_factory import opt_factory
from w3af.core.data.options.option_list import OptionList


class bing_spider(CrawlPlugin):
    """
    Search Bing to get a list of new URLs
    :author: Andres Riancho (andres.riancho@gmail.com)
    """

    def __init__(self):
        CrawlPlugin.__init__(self)

        # User variables
        self._result_limit = 300

    @runonce(exc_class=w3afRunOnce)
    def crawl(self, fuzzable_request):
        """
        :param fuzzable_request: A fuzzable_request instance that contains
                                    (among other things) the URL to test.
        """
        bing_se = bing(self._uri_opener)
        domain = fuzzable_request.get_url().get_domain()

        if is_private_site(domain):
            msg = 'There is no point in searching Bing for "site:%s".'\
                  ' Bing doesn\'t index private pages.'
            raise w3afException(msg % domain)

        try:
            results = bing_se.get_n_results('site:' + domain, self._result_limit)
        except:
            pass
        else:
            self.worker_pool.map(self.http_get_and_parse,
                                    [r.URL for r in results])

    def get_options(self):
        """
        :return: A list of option objects for this plugin.
        """
        ol = OptionList()
        d = 'Fetch the first "result_limit" results from the Google search'
        o = opt_factory('result_limit', self._result_limit, d, 'integer')
        ol.add(o)

        return ol

    def set_options(self, options_list):
        """
        This method sets all the options that are configured using the user interface
        generated by the framework using the result of get_options().

        :param OptionList: A dictionary with the options for the plugin.
        :return: No value is returned.
        """
        self._result_limit = options_list['result_limit'].get_value()

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugin finds new URL's in Bing search engine.

        One configurable parameters exist:
            - result_limit

        This plugin searches Bing for : "site:domain.com", requests all search
        results and parses them in order to find new URLs.
        """

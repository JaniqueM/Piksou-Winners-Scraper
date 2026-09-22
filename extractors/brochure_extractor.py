# Generic brochure extractor placeholder.
#
# Specific brochure retailers should have their own plugins,
# for example:
#
#     KingSaversExtractor
#     SaversExtractor
#
# This class exists for future generic brochure functionality.


from extractors.base_extractor import BaseExtractor


class BrochureExtractor(BaseExtractor):

    # Generic brochure extractors do not require
    # the website HTTP Fetcher.
    requires_fetcher = False

    def extract_products(
        self,
        response=None
    ):

        # Generic brochure extraction logic
        # can be implemented here in the future.

        return []
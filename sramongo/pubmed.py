"""Module to parse pubmed XML."""
from sramongo.xml_helpers import valid_path, parse_tree_from_dict

class Pubmed(object):
    def __init__(self, node):
        self.pubmed = {}
        locs = {
                'pubmed_id': ('PMID', 'text'),
                'title': ('Article/ArticleTitle', 'text'),
                }
        self.pubmed.update(parse_tree_from_dict(node, locs))

        self.pubmed['date_created'] = self._parse_dates(node.find('DateCreated'))
        self.pubmed['date_completed'] = self._parse_dates(node.find('DateCompleted'))
        self.pubmed['date_revised'] = self._parse_dates(node.find('DateRevised'))
        self.pubmed['citation'] = self._parse_citation(node.find('Article/Journal'))
        self.pubmed['abstract'] = self._parse_abstract(node.find('Article/Abstract'))
        self.pubmed['authors'] = self._parse_authors(node.find('Article/AuthorList'))

        # Clean up
        self._drop_empty()

    def _drop_empty(self):
        """Scans through a dictionary and removes empty lists or None elements."""

        drop_keys = []
        for k, v in self.pubmed.items():
            try:
                if (v is None) or (len(v) == 0):
                    drop_keys.append(k)
            except TypeError as err:
                # Some types (int, float) will cause an exception, if they are
                # of this type I don't really care then they are not blank so
                # skip.
                pass

        for k in drop_keys:
            del self.pubmed[k]

    @valid_path
    def _parse_dates(self, node):
        year = node.find('Year').text
        month = node.find('Month').text
        day = node.find('Day').text
        return '-'.join([year, month, day])

    @valid_path
    def _parse_citation(self, node):
        issue = node.find('ISSN').text
        volume = node.find('JournalIssue/Volume').text
        year = node.find('JournalIssue/PubDate/Year').text
        journal = node.find('ISOAbbreviation').text
        return '{v} {j} {y}'.format(i=issue, y=year, j=journal, v=volume)

    @valid_path
    def _parse_abstract(self, node):
        parts = []
        for part in node:
            parts.append(part.text)
        return '\n'.join(parts)

    @valid_path(rettype=list)
    def _parse_authors(self, node):
        authors =[]
        for author in node:
            d = {
                'first_name': author.find('ForeName').text,
                'last_name': author.find('LastName').text,
                'affiliation': author.find('AffiliationInfo/Affiliation').text,
                }
            authors.append(d)
        return authors

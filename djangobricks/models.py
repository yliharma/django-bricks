# -*- coding: utf-8 -*-
from operator import attrgetter, itemgetter

from django.template import loader

from .settings import SORTING_ASC, SORTING_DESC

# ---------------------------------------------------------------------------
# Criterion
# ---------------------------------------------------------------------------

class Criterion(object):
    """
    """
    
    def __init__(self, attr_name, list_callback=None, default_value=None):
        self.attr_name = attr_name
        self.list_callback = list_callback
        self.default_value = default_value
    
    def __repr__(self):
        """docstring for __repr__"""
        return self.attr_name
    
    def get_for_item(self, item):
        """docstring for get_for_item"""
        return getattr(item, self.attr_name, self.default_value)
    
    def get_for_item_list(self, items):
        """docstring for get_for_item_list"""
        if self.list_callback is None:
            return self.default_value
        return self.list_callback((getattr(i, self.attr_name) for i in items))
    

# ---------------------------------------------------------------------------
# Brick
# ---------------------------------------------------------------------------

class BaseBrick(object):
    """
    Classe base per un nodo.
    """
    
    template_name = '' # Deve essere una stringa
    
    def get_attr_for_criterion(self, criterion):
        raise NotImplemented
    
    def get_context(self):
        """Restituisce il contesto da passare al template per il rendering."""
        return {}
    
    def render(self):
        """Restituisce il frammento html che rappresenta il nodo."""
        template = loader.get_template(self.template_name)
        content = template.render(self.get_context())
        return content
    

class SingleBrick(BaseBrick):
    """Brick for a single object."""
    def __init__(self, item):
        self.item = item
    
    def __repr__(self):
        return repr(self.item)
    
    def get_attr_for_criterion(self, criterion):
        return criterion.get_for_item(self.item)
    

class ListBrick(BaseBrick):
    """Brick for a list of object."""
    def __init__(self, items):
        self.items = items
    
    def __repr__(self):
        return repr(self.items)
    
    def get_attr_for_criterion(self, criterion):
        return criterion.get_for_item_list(self.items)
    

# ---------------------------------------------------------------------------
# Brick Manager
# ---------------------------------------------------------------------------

class BaseBrickManager(object):
    """Classe base per la gestione di una lista di nodi.
    
    """
    
    def __init__(self, nodes, criteria=[]):
        self.nodes = nodes
        self.criteria = criteria
    
    def __getitem__(self, key):
        return self.nodes[key]
    
    def __iter__(self):
        return iter(self.sorted())
    
    def _cmp(self, left, right):
        """
        # Courtesy of:
        # http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
        """
        comparers = (
            (attrgetter('get_attr_for_criterion'), criterion, sorting_order) 
            for criterion, sorting_order in self.criteria
        )
        for fn, criterion, sorting_order in comparers:
            result = cmp(fn(left)(criterion), fn(right)(criterion))
            if result:
                return sorting_order * result
        else:
            return 0
    
    def sorted(self):
        if not hasattr(self, '_sorted'):
            self._sorted = sorted(self.nodes, cmp=self._cmp)
        return self._sorted
    

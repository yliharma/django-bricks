# -*- coding: utf-8 -*-
from operator import attrgetter, itemgetter

from django.template import loader

SORTING_ASC = 1
SORTING_DESC = -1

# ---------------------------------------------------------------------------
# Criterion
# ---------------------------------------------------------------------------

class Criterion(object):
    """A criterion works as a sorting key for a BaseWall subclass.
    
    Functionally it is a proxy to a property of a Brick, whether it is has
    a single item or a list.
    
    Params:
    - attrname: the name of the attribute to retrieve. Can be a callable that
                takes no argument.
    - callback: a function that receives an item list and returns a
                single value for the attrname.
    - default: the value to return when the item doesn't have the
               attribute or the callback is None. Can be a callable that
               takes no argument.
    """
    
    def __init__(self, attrname, callback=None, default=None):
        self.attrname = attrname
        self.callback = callback
        self.default = default
    
    def __repr__(self):
        return self.attrname
    
    def get_for_item(self, item):
        """
        Returns the value of the `attrname` for the item, or the `default`
        if the item doesn't have the attribute.
        """
        attrvalue = getattr(item, self.attrname, self.default)
        if callable(attrvalue):
            return attrvalue()
        return attrvalue
    
    def get_for_item_list(self, items):
        """
        If the criterion has a callable `callback`, passes the item list
        to it and returns the value of the `attrname` for the item list, 
        otherwise returns the `default`.
        """
        if self.callback is None or not callable(self.callback):
            return callable(self.default) and self.default() or self.default
        return self.callback((self.get_for_item(i) for i in items))
    

# ---------------------------------------------------------------------------
# Brick
# ---------------------------------------------------------------------------

class BaseBrick(object):
    """Base class for a brick.
    """
    
    template_name = None
    
    def get_attr_for_criterion(self, criterion):
        """Returns the criterion attribute for this brick."""
        raise NotImplemented
    
    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """Returns a list of bricks from the given queryset."""
        raise NotImplemented
    
    def get_context(self):
        """Context for template (TODO)."""
        return {}
    
    def render(self):
        """HTML for the brick (TODO)."""
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
    
    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        return [cls(i) for i in queryset]
    

class ListBrick(BaseBrick):
    """Brick for a list of objects."""
    def __init__(self, items):
        self.items = items
    
    def __repr__(self):
        return repr(self.items)
    
    def get_attr_for_criterion(self, criterion):
        return criterion.get_for_item_list(self.items)
    
    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        return [cls(list(queryset))]
    

# ---------------------------------------------------------------------------
# Brick Manager
# ---------------------------------------------------------------------------

class BaseWall(object):
    """Manager for a list of bricks.
    
    It orders a list of bricks using the given criteria and can be sliced or
    iterated.
    
    Sample usage:
    
    class MyBrickWall(BaseWall):
        ...
    
    bricks = SingleBrick.get_for_queryset(MyObject.objects.all())
    bricks.extend(ListBrick.get_for_queryset(MyOtherObject.objects.all())
    
    wall = MyBrickWall(bricks, criteria=(
        (Criterion('is_sticky', callback=min, SORTING_DESC),
        (Criterion('popularity', SORTING_DESC),
    ))
    
    for brick in wall:
        do_something(brick)
    
    """
    
    def __init__(self, bricks, criteria=[]):
        self.bricks = bricks
        self.criteria = criteria
    
    def __getitem__(self, key):
        return self.sorted()[key]
    
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
            self._sorted = sorted(self.bricks, cmp=self._cmp)
        return self._sorted
    

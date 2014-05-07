# -*- coding: utf-8 -*-
import copy
from operator import attrgetter

SORTING_ASC = 1
SORTING_DESC = -1

# ---------------------------------------------------------------------------
# Criterion
# ---------------------------------------------------------------------------

class Criterion(object):
    """A criterion works as a sorting key for a BaseWall subclass.
    
    It is a proxy to a value of a BaseBrick subclass, whether it is a
    SingleBrick or a ListBrick.
    
    Params:
    - attrname: the name of the attribute to retrieve from an item of a
                SingleBrick. Can be a callable that takes no argument.
    - callback: a function that receives an item list and returns a
                single value for the attrname, for example `max.
    - default: the value to return when the item doesn't have the
               attribute, the callback is None or the item list is empty.
               Can be a callable that takes no argument.
    """
    
    def __init__(self, attrname, callback=None, default=None):
        self.attrname = attrname
        self.callback = callback
        self.default = default
    
    def __repr__(self):
        return self.attrname
    
    def get_value_for_item(self, item):
        """
        Returns a value for an item or the `default` if the item doesn't have
        any attribute `attrname.
        """
        attrvalue = getattr(item, self.attrname, self.default)
        if callable(attrvalue):
            return attrvalue()
        return attrvalue
    
    def get_value_for_list(self, items=()):
        """
        Returns a single value for a list of items, filtering the values for
        each item through the `callback` function.
        If no `callback` is specified or if the item list is empty, it returns
        the `default` value.
        """
        if not isinstance(items, (list, tuple)):
            raise ValueError('List or tuple expected.')
        if items and self.callback is not None and callable(self.callback):
            # This is needed to avoid ValueError for some callback that can
            # not receive an empty list, like max()
            return self.callback((self.get_value_for_item(i) for i in items))
        return callable(self.default) and self.default() or self.default
    

# ---------------------------------------------------------------------------
# Brick
# ---------------------------------------------------------------------------

class BaseBrick(object):
    """Base class for a brick.
    
    A brick is a container for a single Django model instance or a list of
    instances. Subclasses should extend one of the two provided subclasses
    that implement those two use cases.
    
    Also, a brick knows how to render itself.
    """
    
    template_name = None
    
    def get_value_for_criterion(self, criterion):
        """Returns the criterion value for this brick."""
        raise NotImplemented
    
    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """Returns a list of bricks from the given queryset."""
        raise NotImplemented
    
    def get_context(self):
        """Returns the context to be passed on to the template."""
        return {}
    

class SingleBrick(BaseBrick):
    """Brick for a single object."""
    def __init__(self, item):
        self.item = item
    
    def __repr__(self):
        return repr(self.item)
    
    def get_value_for_criterion(self, criterion):
        return criterion.get_value_for_item(self.item)
    
    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """
        Returns an iterator over the bricks, one for each object in the
        queryset.
        """
        return (cls(i) for i in queryset)
    
    def get_context(self):
        """
        Returns the context to be passed on to the template.
        By default, it returns a dictionary instance with an 'object' key
        and the item as the value.
        Subclass should first call the super method and then update the result.
        """
        return {'object': self.item}
    

class ListBrick(BaseBrick):
    """Brick for a list of objects."""
    def __init__(self, items):
        self.items = items
    
    def __repr__(self):
        return repr(self.items)
    
    def get_value_for_criterion(self, criterion):
        return criterion.get_value_for_list(self.items)
    
    @classmethod
    def get_bricks_for_queryset(cls, queryset):
        """
        Returns a list with a single brick containing all the object in the
        queryset. Subclasses might want to override this method for a more
        sophisticated implementation.
        """
        return [cls(list(queryset))]
    
    def get_context(self):
        """
        Returns the context to be passed on to the template.
        By default, it returns a dictionary instance with an 'object_list'
        key and the items as the value.
        Subclass should first call the super method and then update the result.
        """
        return {'object_list': self.items}
    

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
    
    bricks = SingleBrick.get_bricks_for_queryset(MyObject.objects.all())
    bricks.extend(ListBrick.get_bricks_for_queryset(MyOtherObject.objects.all())
    
    wall = MyBrickWall(bricks, criteria=(
        (Criterion('pub_date', callback=max), SORTING_DESC),
        (Criterion('popularity', callback=max), SORTING_DESC),
    ))
    
    for brick in wall:
        do_something(brick)
    
    """
    
    def __init__(self, bricks, criteria=None):
        self.bricks = bricks
        self.criteria = criteria or []
        self._sorted = []
    
    def __getitem__(self, key):
        return self.sorted[key]
    
    def __iter__(self):
        return iter(self.sorted)

    def __len__(self):
        return len(self.bricks)
    
    def __getstate__(self):
        # We save the sorted bricks and delete che criteria
        # as those might not be pickable
        obj_dict = self.__dict__.copy()
        obj_dict['_sorted'] = self.sorted
        if obj_dict.has_key('criteria'):
            del obj_dict['criteria']
        return obj_dict
    
    def _cmp(self, left, right):
        """
        # Courtesy of:
        # http://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
        """
        fn = attrgetter('get_value_for_criterion')
        for criterion, sorting_order in self.criteria:
            result = cmp(fn(left)(criterion), fn(right)(criterion))
            if result:
                return sorting_order * result
        else:
            return 0

    @property
    def sorted(self):
        """
        Lazy property that returns the list of bricks sorted by the criteria.
        """
        if not self._sorted:
            self._sorted = sorted(self.bricks, cmp=self._cmp)
        return self._sorted

    def filter(self, callback, operator='AND'):
        """
        Returns a copy of the wall where the bricks have been filtered using
        the given `callback`, that should be a function or a list of functions
        accepting a brick instance and returning a boolean.
        By default, if more than a callback is given they are 'ANDed', that is,
        a brick will pass the test if every callback returns True.
        This behaviour can be changed by setting the `operator` parameter to
        'OR', in which case as soon as callback returns True the brick is 
        accepted.
        """
        assert operator in ('OR', 'AND'), "Only 'AND' or 'OR' operators are supported"
        if not isinstance(callback, (list, tuple)):
            callback = [callback]
        # The order of bricks is the same even when filtered.
        # So we let the class to sort them (if they are not already) and then
        # apply the filter.
        obj = copy.copy(self)
        func = all if operator == 'AND' else any
        obj._sorted = [i for i in self if func(c(i) for c in callback)]
        # This will keep __len__ value consistent
        obj.bricks = obj._sorted
        return obj


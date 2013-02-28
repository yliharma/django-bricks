import datetime

from django.utils import unittest
from django.db import models

from .models import *

pub_date_criterion = Criterion('pub_date', list_callback=min)
popularity_criterion = Criterion('popularity', list_callback=max)
is_sticky_criterion = Criterion('is_sticky', list_callback=None, default_value=False)


class TestBrickManager(BaseBrickManager):
    pass
    

class TestModelA(models.Model):
    name = models.CharField(max_length=8)
    popularity = models.PositiveIntegerField()
    pub_date = models.DateTimeField()
    is_sticky = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name)
    

class TestModelB(models.Model):
    name = models.CharField(max_length=8)
    pub_date = models.DateTimeField()
    popularity = models.PositiveIntegerField()
    is_sticky = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name)
    

class BrickTest(unittest.TestCase):

    # def setUp(self):
    #     self.h = TestMaatHandler(TestModel)
    # 
    # def tearDown(self):
    #     self.h = None
    
    def test_basic_sorting(self):
        """docstring for test_sorting"""
        object1 = TestModelA.objects.create(name='object1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        object2 = TestModelA.objects.create(name='object2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        object3 = TestModelA.objects.create(name='object3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        object4 = TestModelA.objects.create(name='object4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)
        object5 = TestModelA.objects.create(name='object5', popularity=1,
            pub_date=datetime.datetime(2014, 1, 1, 12, 0), is_sticky=False)
        
        bricks = [SingleBrick(i) for i in TestModelA.objects.all()]
        manager = TestBrickManager(bricks, criteria=(
            (Criterion('is_sticky', list_callback=None, default_value=False), -1),
            #(Criterion('pub_date', list_callback=min), 1),
            (Criterion('popularity', list_callback=max), 1),
        ))
        print manager.sorted()
        
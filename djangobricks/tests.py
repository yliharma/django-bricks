import datetime

from django.utils import unittest
from django.db import models

from .models import *


class TestBrickWall(BaseWall):
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
    

class TestModelC(models.Model):
    name = models.CharField(max_length=8)
    pub_date = models.DateTimeField()
    popularity = models.PositiveIntegerField()
    is_sticky = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name)
    

class BrickTest(unittest.TestCase):

    def setUp(self):
        self.bricks = []
    
    # def tearDown(self):
    #     TestModelA.objects.all().delete()
    #     for i in range(1, 5):
    #         setattr(self, 'brick%s' % i, None)
    #     self.bricks = []
    
    def _create_model_a_objects_and_bricks(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)
        
        self.brickA1 = SingleBrick(objectA1)
        self.brickA2 = SingleBrick(objectA2)
        self.brickA3 = SingleBrick(objectA3)
        self.brickA4 = SingleBrick(objectA4)
        for i in range(1, 5):
            self.bricks.append(getattr(self, 'brickA%s' % i))
    
    def _create_model_b_objects_and_bricks(self):
        objectB1 = TestModelB.objects.create(name='objectB1', popularity=10,
            pub_date=datetime.datetime(2006, 1, 1, 12, 0), is_sticky=False)
        objectB2 = TestModelB.objects.create(name='objectB2', popularity=9,
            pub_date=datetime.datetime(2007, 1, 1, 12, 0), is_sticky=False)
        objectB3 = TestModelB.objects.create(name='objectB3', popularity=8,
            pub_date=datetime.datetime(2008, 1, 1, 12, 0), is_sticky=True)
        objectB4 = TestModelB.objects.create(name='objectB4', popularity=7,
            pub_date=datetime.datetime(2009, 1, 1, 12, 0), is_sticky=False)
        
        self.brickB1 = SingleBrick(objectB1)
        self.brickB2 = SingleBrick(objectB2)
        self.brickB3 = SingleBrick(objectB3)
        self.brickB4 = SingleBrick(objectB4)
        for i in range(1, 5):
            self.bricks.append(getattr(self, 'brickB%s' % i))
    
    def _create_model_c_objects_and_bricks(self):
        objectC1 = TestModelC.objects.create(name='objectC1', popularity=20,
            pub_date=datetime.datetime(2002, 1, 1, 12, 0), is_sticky=False)
        objectC2 = TestModelC.objects.create(name='objectC2', popularity=19,
            pub_date=datetime.datetime(2003, 1, 1, 12, 0), is_sticky=False)
        objectC3 = TestModelC.objects.create(name='objectC3', popularity=18,
            pub_date=datetime.datetime(2004, 1, 1, 12, 0), is_sticky=True)
        objectC4 = TestModelC.objects.create(name='objectC4', popularity=17,
            pub_date=datetime.datetime(2005, 1, 1, 12, 0), is_sticky=False)
        
        self.brickC1 = ListBrick([objectC1, objectC2])
        self.brickC2 = ListBrick([objectC3, objectC4])
        for i in range(1, 3):
            self.bricks.append(getattr(self, 'brickC%s' % i))
    
    # Slicing and iteration
    
    def test_slicing(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks)
        self.assertEqual(wall[0], self.brickA1)
        self.assertEqual(wall[:1], [self.brickA1])
    
    def test_iteration(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks)
        i = 1
        for brick in wall:
            self.assertEqual(brick, getattr(self, 'brickA%s' % i))
            i += 1
    
    # Single keys - Single bricks- Single models
    
    def test_single_key_desc_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(wall.sorted(), expected)
    
    def test_single_key_asc_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1]
        self.assertEqual(wall.sorted(), expected)
    
    # Multi keys - Single bricks - Single Models
    
    def test_multi_key_1_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_DESC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickA3, self.brickA1, self.brickA2, self.brickA4]
        self.assertEqual(wall.sorted(), expected)
    
    def test_multi_key_2_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickA1, self.brickA2, self.brickA4, self.brickA3]
        self.assertEqual(wall.sorted(), expected)
    
    # Single keys - Single bricks - Multi models
    
    def test_single_key_desc_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB1, self.brickB2, self.brickB3, self.brickB4,
                    self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(wall.sorted(), expected)
    
    def test_single_key_asc_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1,
                    self.brickB4, self.brickB3, self.brickB2, self.brickB1]
        self.assertEqual(wall.sorted(), expected)
    
    # Multi keys - Single bricks - Multi models
    
    def test_multi_key_1_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_DESC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB3, self.brickA3, self.brickB1, self.brickB2,
                    self.brickB4, self.brickA1, self.brickA2, self.brickA4]
        self.assertEqual(wall.sorted(), expected)
    
    def test_multi_key_2_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB1, self.brickB2, self.brickB4, self.brickA1,
                    self.brickA2, self.brickA4, self.brickB3, self.brickA3]
        self.assertEqual(wall.sorted(), expected)
    
    # Single keys - Multi bricks - Single models
    
    def test_single_key_1_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=max), SORTING_DESC),
        ))
        expected = [self.brickC1, self.brickC2]
        self.assertEqual(wall.sorted(), expected)
    
    def test_single_key_2_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=min), SORTING_DESC),
        ))
        expected = [self.brickC1, self.brickC2]
        self.assertEqual(wall.sorted(), expected)
    
    def test_single_key_3_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=max), SORTING_ASC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(wall.sorted(), expected)
    
    def test_single_key_4_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=min), SORTING_ASC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(wall.sorted(), expected)
    
    # Multi keys - Multi bricks - Single models
    
    def test_multi_key_1_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('pub_date', callback=max), SORTING_DESC),
            (Criterion('popularity', callback=max), SORTING_DESC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(wall.sorted(), expected)
    
    def test_multi_key_2_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('pub_date', callback=max), SORTING_ASC),
            (Criterion('popularity', callback=min), SORTING_DESC),
        ))
        expected = [self.brickC1, self.brickC2]
        self.assertEqual(wall.sorted(), expected)
    
    # Multi keys - Mixed bricks - Multi models
    
    def test_multi_key_1_sorting_multi_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky', default=False), SORTING_DESC),
            (Criterion('pub_date', callback=max), SORTING_DESC),
        ))
        expected = [self.brickA3, self.brickB3,
                    self.brickA4, self.brickA2, self.brickA1,
                    self.brickB4, self.brickB2, self.brickB1,
                    self.brickC2, self.brickC1]
        self.assertEqual(wall.sorted(), expected)
    
    def test_multi_key_2_sorting_multi_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky', default=False), SORTING_DESC),
            (Criterion('pub_date', callback=max), SORTING_ASC),
        ))
        expected = [self.brickB3, self.brickA3,
                    self.brickC1, self.brickC2,
                    self.brickB1, self.brickB2, self.brickB4,
                    self.brickA1, self.brickA2, self.brickA4]
        self.assertEqual(wall.sorted(), expected)
    
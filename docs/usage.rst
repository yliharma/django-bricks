===========
Basic Usage
===========


Use Case Scenario
=================

To demonstrate how Bricks works, let's pretend we run a website that publishes
both news and videos on its homepage, and that it has two tabs to let the user
choose between two different sorting order: descending publication date (newest
first) and descending number of comments (most commented first).

So let's write some *very basic* Django models that we are going to use as a
base for out example:

.. code-block:: python

    from django.db import models
    
    class News(models.Model):
        title = models.CharField()
        text = models.TextField()
        pub_date = models.DateTimeField()


    class Video(models.Model):
        title = models.CharField()
        video = models.FileField()
        pub_date = models.DateTimeField()


    class Thread(models.Model):
        """A model that can be generically associated to a news or a video."""
        content_type = models.ForeignKey(ContentType)
        object_id = models.PositiveIntegerField()
        content_object = generic.GenericForeignKey('content_type', 'object_id')
        comments_count = models.PositiveIntegerField(default=0) # Denormalization


    class Comment(models.Model):
        thread = models.ForeignKey(Thread, related_name='comments')
        text = models.TextField()
        # Guess other fields


Bricks exposes three main concepts:

Brick
~~~~~
A brick is a container for an instance of a Django model or even a (presumably
small) list of instances.

Its a brick responsibility to *wrap* a queryset and returns a list of wrapped
objects, to retrieve a value from its content to be used as a sorting key and
finally to render its content.

Bricks offers two classes: :py:class:`SingleBrick <djangobricks.models.SingleBrick>`
and :py:class:`ListBrick <djangobricks.models.ListBrick>`.

Normally, subclasses will only need to override the
:py:attr:`template_name <djangobricks.models.BaseBrick.template_name>` attribute
and, in case of a :py:class:`ListBrick <djangobricks.models.ListBrick>` subclass,
the :py:meth:`get_bricks_for_queryset <djangobricks.models.ListBrick.get_bricks_for_queryset>`
class method.


Criterion
~~~~~~~~~
A criterion is a proxy for a value of the brick.

If the brick contains a single instance, then it's usually a property of the
instance itself, otherwise it's a property of the list.

You can also specify a callable instead of a model property or a default value
if, for example, the value has no meaning for a given model.

It's important to note that a criterion has no information about the actual
sorting order, so you have to pass that info along using the
:py:attr:`SORTING_ASC` and the :py:attr:`SORTING_DESC` constant.

Be sure to check the :py:class:`Criterion <djangobricks.models.Criterion>` class
reference.


Wall
~~~~
Not surprisingly, a wall is a list of bricks. Mixed with a set of criteria, it
sorts the bricks and can be iterated to get them back.


Setting up a wall
=================

To start, we should create the criteria. They are subclasses of
:py:class:`Criterion <djangobricks.models.Criterion>`:

.. code-block:: python

    import datetime

    from djangobricks.models import Criterion

    CRITERION_PUB_DATE = Criterion('pub_date', default=datetime.datetime.now)
    CRITERION_COMMENT_COUNT = Criterion('thread__comment_count', default=0)

Next, we are going to subclass :py:class:`SingleBrick <djangobricks.models.SingleBrick>`
to create a container for our objects. In this case, we can probably get away
with a single subclass, but for the sake of completeness let's create a brick
for a each model:

.. code-block:: python

    from djangobricks.models import SingleBrick

    class NewsBrick(SingleBrick):
        template_name = 'bricks/single/news.html'

    class VideoBrick(SingleBrick):
        template_name = 'bricks/single/video.html'

There is also a :py:class:`ListBrick <djangobricks.models.ListBrick>` class, but
let's stick with a simple case for now.

At this point we can create our wall by hand, but let's use the
:py:class:`BaseWallFactory <djangobricks.models.BaseWallFactory>` class instead.

.. code-block:: python

    from myapp.models import News, Video

    from djangobricks.models import BaseWallFactory

    class HomepageWallFactory(BaseWallFactory):
        def get_content(self):
            return (
                (NewsBrick, News.objects.all()),
                (VideoBrick, Video.objects.all())
            )

The :py:meth:`BaseWallFactory.get_content <djangobricks.models.BaseWallFactory.get_content>`
method returns an iterable of tuples, where the first element is a
:py:class:`BaseBrick <djangobricks.models.BaseBrick>` subclass and the second the
queryset whose elements should be rendered using that class.

We are almost there! All we have to do is to create our wall in the view:

.. code-block:: python

    from djangobricks.models import SORTING_DESC

    def index(request):
        last_content_criteria = (
            (CRITERION_PUB_DATE, SORTING_DESC),
        )
        last_content_wall = HomepageWallFactory(last_content_criteria)
        
        most_commented_criteria = (
            (CRITERION_COMMENT_COUNT, SORTING_DESC),
        )
        most_commented_content_wall = HomepageWallFactory(most_commented_criteria)
        
        context = {
            'last_content_wall': last_content_wall,
            'most_commented_content_wall: most_commented_content_wall
        }
        return render_to_response('index.html', context,
                                  context_instance=RequestContext(request)))

Render a Wall
=============

Now that we have not one but two walls, we can render them within a Django
template:

.. code-block:: html+django

    {% from bricks import render_brick %}
    
    {% for brick in last_content_wall %}
        {% render_brick brick %}
    {% endfor%}
    
    {% for brick in most_commented_content_wall %}
        {% render_brick brick %}
    {% endfor%}

Done!

We covered the basic of Bricks, but it can handle much more complex scenarios.
Be sure to check the :doc:`advanced_usage`.
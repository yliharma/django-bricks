==============
Advanced Usage
==============

Using a ListBrick
~~~~~~~~~~~~~~~~~

Now that you have run through the :doc:`basics <usage>`, let's tackle some more advanced topic.

Building up from our previous example, let's say that our designers team decided
that the list of videos and news must change. Specifically, the news have a new
layout and they have to be grouped in list of five elements each.

In this case, we are going to use the :py:class:`ListBrick <djangobricks.models.ListBrick>` class.

So let's replace our declaration of ``NewsBricks``:

.. code-block:: python

    from djangobricks.models import ListBrick

    class NewsBrick(ListBrick):
        template_name = 'bricks/list/news.html

The ``VideoBrick`` doesn't need to be changed.

By default :py:meth:`get_bricks_for_queryset <djangobricks.models.ListBrick.get_bricks_for_queryset>`
returns a list of bricks containing 5 elements each. Unless you need some more
complicated behaviour, you can simply change the number of elements by setting
the :py:attr:`chunk_size <djangobricks.models.ListBrick.chunk_size>` attribute
accordingly.

Now, as the brick does not contain a single element, is not clear what a
:py:class:`Criterion <djangobricks.models.Criterion>` should return when applied
to it. The value of the first element? The average? That is really up to you.

In this case, let's say that we want to change ``CRITERION_PUB_DATE`` to return
the max value of the list (that is, the brick will be sorted based on the newest
news it contains) and ``CRITERION_COMMENT_COUNT`` to return the average number
of comments.

To do that, we simply change the criteria declaration by adding a callback
function that accepts a list and return a value:

.. code-block:: python

    CRITERION_PUB_DATE = Criterion('pub_date', max, default=datetime.datetime.now)
    CRITERION_COMMENT_COUNT = Criterion('thread__comment_count',
                                        lambda x:sum(x)/len(x), default=0)

We don't need to change anything else.


Filtering a wall
~~~~~~~~~~~~~~~~

Our designers are relentless. They want the user to be able to filter some
content from the wall. In our simple example, we can say that they want to
hide the videos from the wall.

In this case, we can probably just build a second wall and returns it in our
view depending on user choice, but we are going to do it the Bricks way.

The :py:class:`BaseWall <djangobricks.models.BaseWall>` class provides a simple
:py:meth:`filter <djangobricks.models.BaseWall.filter>` method that accepts a
list of callables that accepts a brick instance and returns a boolean,
and a boolean operator. Each brick is then filtered against the list of
callables: all of them if the operator is ``AND`` (the default value)
or any of them if the operator is ``OR``.

In our case, we need a single callback that should return ``True`` if the brick
contains some news (remember: we want to hide the videos!) and ``False`` otherwise.

Something like this would to the trick:

.. code-block:: python

    def is_news_brick(brick):
        return brick.__class__.__name__ == 'NewsBrick'

And in our view:

.. code-block:: python

    ...
    filtered_last_content_wall = last_content_wall.filter(is_news_brick)
    ...

The advantage of this approach is speed. The creation of a wall can be an expensive
operation. Caching a wall and filtering the cached result can be faster then
building a new wall from scratch, especially if you have a more complicated setup
with a lot of filters.


Handling heterogeneous models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's say that we need to add another model to our wall, defined below:

.. code-block:: python

    from django.db import models

    class PhotoGallery(models.Model):
        title = models.CharField()
        images = models.ManyToManyField(Photo)
        public_from_date = models.DateTimeField()

As you can see, this model doesn't have a ``pub_date`` field like ``News`` and
``Video``. How can we use the ``CRITERION_PUB_DATE`` over this model?

Remember that is up to the brick to return a value for a given criterion of its
content. So let's write a brick class for our new model:

.. code-block:: python

    from djangobricks.models import SingleBrick

    class PhotoGalleryBrick(SingleBrick):
        template_name = 'bricks/single/photo_gallery.html'

        def get_value_for_criterion(self, criterion):
            if criterion.attrname == 'pub_date':
                return self.item.public_from_date
            return super(PhotoGalleryBrick, self).get_value_for_criterion(criterion)

And that's it! Unless you are sure to cover each possible criterion, it's a good
practice to return the value from super at least, as shown above.


Adding context to the template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, :py:class:`SingleBrick <djangobricks.models.SingleBrick>` will
pass the object to the context with an ``object`` key.

The :py:class:`ListBrick <djangobricks.models.ListBrick>` context contains an
``object_list`` key instead.

If you want to add extra context to render the template, you can either
override the :py:meth:`get_context <djangobricks.models.BaseBrick.get_context>`
method as show below:

.. code-block:: python

    class NewsBrick(SingleBrick):

        def get_context(self, **kwargs)
            context = super(NewsBrick, self).get_context(**kwargs)
            context['color'] = 'red'
            return context

or you can add them using directly the templatetag

.. code-block:: html+django

    {% render_brick brick color='red' %}

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pelican-similar-articles-light)
![PyPI](https://img.shields.io/pypi/v/pelican-similar-articles-light)
![PyPI - License](https://img.shields.io/pypi/l/pelican-similar-articles-light?color=brigthgreen)

# Similar articles for Pelican

A Pelican plugin to provide a support of similar articles, allowing users to
access a list of articles linked to each article by a similarity calculation
on their tags.


## Installation

    pip install pelican-similar-articles-light

    # Or locally
    python setup.py develop


## Template integration

Bare version:

```html
{% if article.similar_articles %}
    <ul>
    {% for sub_article in article.similar_articles %}
        <li><a href="{{ SITEURL }}/{{ sub_article.url }}">{{ sub_article.title }}</a></li>
    {% endfor %}
    </ul>
{% endif %}
```

With bootstrap and translations support:

```html
{% if article.similar_articles %}
<div class="alert alert-warning text-left" role="alert">
    <p><strong>{{ _("You might be interested in") ~ ' ' ~ ngettext("the following article:", "the following articles:", article.similar_articles|count) }}</strong></p>
    <ul>
    {% for sub_article in article.similar_articles %}
        <li><a href="{{ SITEURL }}/{{ sub_article.url }}" class="alert-link">{{ sub_article.title }}</a></li>
    {% endfor %}
    </ul>
</div>
{% endif %}
```


## Pelican configuration

In your `pelicanconf.py`, please add/update these lines:

```python
PLUGINS += ['pelican.plugins.similar_articles_light',]
```

You you can customize certain features of the plugin.
You will find below the default values which can be overwritten by a statement
in the`pelicanconf.py` file.

The maximum number of similar articles:

```python
SIMILAR_ARTICLES_MAX_COUNT = 2
```

The the minimal score to consider an article as similar:

```python
SIMILAR_ARTICLES_MIN_SCORE = 0.0001
```

## About the implementation

The plugin computes a similarity score based on the tags of the articles.
It consists in building a global bag of words (dictionary), and a bag of words
for each article, representing this article as an n-dimensional vector.

The terms are weighted using the [TF-IDF method](https://en.wikipedia.org/wiki/Tf%E2%80%93idf),
according to their rareness within the corpus formed by all the tags of the site.

The vector of each article is then compared to all the others via the calculation
of the [cosine simiarity](https://en.wikipedia.org/wiki/Cosine_similarity)
widely used in text mining. It consists in determining the angle formed between
2 vectors.
The maximum similarity obtained is 1 (the documents have all their important tags
in common), while the minimum is 0 (the documents have no tag in common).


## Comparison with **Similar Posts** plugin

The [Similar Posts plugin](https://github.com/pelican-plugins/similar-posts)
uses exactly the same technique, I don't think you will have any difference in the
the result obtained.
However, the dependencies used are a bit too large and somewhat oversized for
the intended purpose: a few words (tags) summarizing an article among a handful
of articles from a Pelican blog.

The implementation of Similar Articles Light is in pure Python.
**In any case, reinventing the wheel should never be a reason to sell a technology**;
therefore please consider this plugin as a proof of concept of a few dozen lines of code,
fully functional and without dependencies; so probably slightly faster to run
than *Similar Posts*.

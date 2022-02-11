![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pelican-similar-articles-light)
![PyPI](https://img.shields.io/pypi/v/pelican-similar-articles-light)
![PyPI - License](https://img.shields.io/pypi/l/pelican-similar-articles-light)

# Similar articles for Pelican

A Pelican plugin to provide a support of similar articles, allowing users to
access a list of articles linked to each article by a similarity calculation
on their tags.


## Installation

    pip install pelican-sphinxsearch

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

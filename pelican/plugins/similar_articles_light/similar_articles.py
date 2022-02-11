# A Pelican plugin to provide a support of similar articles, allowing users to
# access a list of articles linked to each article by a similarity calculation
# on their tags.

# Copyright (C) 2022 Ysard

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Pelican plugin to add a list of similar articles to each article (if possible).

The method is based on a TF-IDF and the Cosine similarity.
"""
# Standard imports
from collections import Counter, OrderedDict, defaultdict
from functools import lru_cache
import itertools as it
import operator as op
from math import log10
import logging

# Pelican imports
from pelican import signals

LOGGER = logging.getLogger(__name__)


def add_similar_articles(article_generator):
    """Add `similar_articles` attibute to each article when available

    A similarity score is used to produce a list of similar articles for the given one.

    .. seealso::
        https://fr.wikipedia.org/wiki/TF-IDF
        https://fr.wikipedia.org/wiki/Similarit%C3%A9_cosinus

    idf formula:

        idf = log10(|D| / |{dj : ti ∈ dj}|)

        - D: Number of articles in the corpus
        - |{dj : ti ∈ dj}|): Number of articles linked to the ti term

    tf formula:

        tfij = 1 if present, 0 if absent

    tf-idf formula:

        tfidfij = tfi,j * idfi

    cosine similarity formula:

        cosine = tfidfi * tfidfj / ||tfidfi|| * ||tfidfj||

        - tfidfi * tfidfj: dot product of the 2 vectors
        - ||tfidfi||: Euclidean norm of the vector

        Results:

        - 0 value for independent vectors (orthogonal)
        - 1 value for collinear vectors of positive coefficient
        The intermediate values make it possible to evaluate the degree of similarity.

    :param article_generator: Generator of articles obtained via the signal
        `article_generator_finalized`. We use it to iterate over articles and
        to get tags accross the corpus.
    """
    LOGGER.info("Similar articles computation in progress...")

    max_count = article_generator.settings.get("SIMILAR_ARTICLES_MAX_COUNT", 2)
    min_score = article_generator.settings.get("SIMILAR_ARTICLES_MIN_SCORE", 0.0001)

    # Count occurences of tags in all the articles (bag-of-words at corpus scale)
    # Iterate over articles
    # tags = Counter(
    #   tag.name
    #   for article in article_generator.articles
    #   for tag in article.metadata.get("tags", tuple())  # Some articles may not have any tags
    # )
    # Direct use 'tags' attr of the article generator
    tags = {tag.name: len(articles) for tag, articles in article_generator.tags.items()}

    # Compute idf of the corpus
    global_idf = OrderedDict(
        {
            tag_name: log10(len(article_generator.articles) / freq)
            for tag_name, freq in tags.items()
        }
    )

    # Compute tfidf of each article
    add_tfidf_to_articles(article_generator.articles, global_idf)

    # Build similarity matrix
    similarity_matrix = build_similarity_matrix(article_generator.articles)

    # Assign the similar_articles attribute to all articles
    for article, article_similarities in similarity_matrix.items():
        # Get the 2 most similar articles
        most_similar = tuple(
            article_adverse
            for article_adverse, score in article_similarities.most_common(max_count)
            if score > min_score
        )
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(
                "%s: %s",
                article.slug,
                {
                    article_adverse.slug: round(score, 4)
                    for article_adverse, score in article_similarities.most_common(
                        max_count
                    )
                },
            )
        if most_similar:
            # Add these articles to similar_articles attribute of the current article
            # alt: setattr(article, "similar_articles", most_similar)
            article.similar_articles = most_similar

    # LOGGER.debug("Dot product cache", dot_product.cache_info())
    # LOGGER.debug("Cosine cache", compute_cosine.cache_info())

    LOGGER.info("Similar articles computation done.")


def add_tfidf_to_articles(articles, global_idf):
    """Add tfidf attribute to each article"""
    for article in articles:
        # Get tag names of the article
        article_tags = frozenset(tag.name for tag in article.metadata.get("tags", []))
        # Compute tfidf vector for the current article
        tfidf = tuple(
            # This is the tf binarization
            idf * 1 if tag_name in article_tags else 0
            for tag_name, idf in global_idf.items()
        )

        # Add tfidf to article
        article.tfidf = tfidf


def build_similarity_matrix(articles):
    """Build similarity matrix

    :return: Dict of dict (Counter) with keys of dict1 and dict2 as a couple
        of articles, values of the 2nd dict (a Counter) are cosine similarities.
    :rtype: <dict <Counter>>
    """
    # Combinations are used to avoid duplicate couples of articles
    similarity_matrix = defaultdict(Counter)
    for article_current, article_adverse in it.combinations(articles, 2):
        tfidf_current = article_current.tfidf
        tfidf_adverse = article_adverse.tfidf

        # Sort the articles to maximize cache hits
        if id(article_current) < id(article_adverse):
            cosine = compute_cosine(tfidf_current, tfidf_adverse)
        else:
            cosine = compute_cosine(tfidf_adverse, tfidf_current)  # pylint: disable=arguments-out-of-order

        similarity_matrix[article_current][article_adverse] = cosine
        similarity_matrix[article_adverse][article_current] = cosine
    return similarity_matrix


@lru_cache(maxsize=None)
def dot_product(vector_1, vector_2):
    """Compute the dot product of the 2 given vectors"""
    return sum(map(op.mul, vector_1, vector_2))


@lru_cache(maxsize=None)
def compute_cosine(tfidf_current, tfidf_adverse):
    """Compute the cosine similarity between the 2 given vectors"""
    norm_current = dot_product(tfidf_current, tfidf_current)
    prod = dot_product(tfidf_current, tfidf_adverse)
    norm_adverse = dot_product(tfidf_adverse, tfidf_adverse)

    if min(norm_current, norm_adverse) == 0:
        return 0
    return prod / ((norm_current * norm_adverse) ** 0.5)


def register():
    """Register the plugin with the `signal article_generator_finalized`"""
    signals.article_generator_finalized.connect(add_similar_articles)

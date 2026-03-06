"""
Recommendation Engine using scikit-learn and pandas.
Content-based filtering (TF-IDF + cosine similarity) and collaborative filtering.
"""
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class RecommendationEngine:

    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words='english', max_features=5000)

    def build_content_features(self, movies):
        """Build TF-IDF feature vectors from movie metadata."""
        if not movies:
            return None, None

        corpus = []
        movie_ids = []

        for movie in movies:
            genres = movie.get('genres', [])
            tags = movie.get('tags', [])
            director = movie.get('director', '')
            title = movie.get('title', '')
            year = str(movie.get('year', ''))

            # Combine all text features
            feature_text = ' '.join([
                title,
                ' '.join(genres) * 3,  # Weight genres more
                ' '.join(tags) * 2,
                director * 2,
                year
            ])
            corpus.append(feature_text)
            movie_ids.append(movie['movie_id'])

        if not corpus:
            return None, None

        try:
            tfidf_matrix = self.tfidf.fit_transform(corpus)
            return tfidf_matrix, movie_ids
        except Exception as e:
            logger.error(f"Error building TF-IDF matrix: {e}")
            return None, None

    def get_similar_movies(self, target_movie_id, movies, top_n=10):
        """Get movies similar to target using content-based filtering."""
        tfidf_matrix, movie_ids = self.build_content_features(movies)
        if tfidf_matrix is None:
            return []

        try:
            target_idx = movie_ids.index(target_movie_id)
        except ValueError:
            return []

        similarity_scores = cosine_similarity(
            tfidf_matrix[target_idx:target_idx + 1], tfidf_matrix
        ).flatten()

        # Get top N similar (excluding self)
        similar_indices = similarity_scores.argsort()[::-1][1:top_n + 1]

        results = []
        for idx in similar_indices:
            if similarity_scores[idx] > 0:
                results.append({
                    'movie_id': movie_ids[idx],
                    'score': float(similarity_scores[idx])
                })

        return results

    def get_collaborative_recommendations(self, user_id, interactions, top_n=10):
        """
        Simple collaborative filtering using user-item interaction matrix.
        Find users with similar watching patterns and recommend their movies.
        """
        import pandas as pd

        if not interactions:
            return []

        # Build interaction DataFrame
        df = pd.DataFrame(interactions)
        if df.empty or 'user_id' not in df.columns:
            return []

        # Create user-item matrix
        try:
            user_item = df.pivot_table(
                index='user_id', columns='movie_id', values='score', fill_value=0
            )
        except Exception:
            return []

        if user_id not in user_item.index:
            return []

        # Calculate user similarity
        user_similarity = cosine_similarity(user_item)
        user_idx = list(user_item.index).index(user_id)

        # Find similar users
        sim_scores = user_similarity[user_idx]
        similar_users = np.argsort(sim_scores)[::-1][1:11]  # Top 10 similar users

        # Get movies watched by similar users but not by target user
        user_movies = set(user_item.columns[user_item.loc[user_id] > 0])
        recommendations = {}

        for sim_user_idx in similar_users:
            sim_user_id = user_item.index[sim_user_idx]
            sim_weight = sim_scores[sim_user_idx]

            if sim_weight <= 0:
                continue

            sim_user_movies = set(user_item.columns[user_item.loc[sim_user_id] > 0])
            new_movies = sim_user_movies - user_movies

            for movie_id in new_movies:
                if movie_id not in recommendations:
                    recommendations[movie_id] = 0
                recommendations[movie_id] += sim_weight * user_item.loc[sim_user_id, movie_id]

        # Sort by score
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{'movie_id': int(mid), 'score': float(score)} for mid, score in sorted_recs]

    def get_trending(self, movies, top_n=15):
        """Get trending movies based on view velocity and trending score."""
        if not movies:
            return []

        scored = []
        for movie in movies:
            score = (movie.get('trending_score', 0) * 0.6 +
                     movie.get('view_count', 0) * 0.3 +
                     movie.get('rating', 0) * 0.1)
            scored.append({'movie_id': movie['movie_id'], 'score': score})

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_n]

    def get_personalized(self, user_id, user_genres, movies, interactions, top_n=15):
        """
        Combined recommendation: content-based + collaborative + trending.
        Weighted combination for personalized feed.
        """
        results = {}

        # Content-based: boost movies matching user's favorite genres
        for movie in movies:
            movie_genres = set(movie.get('genres', []))
            user_genre_set = set(user_genres)
            genre_overlap = len(movie_genres & user_genre_set)

            content_score = genre_overlap * 0.3 + movie.get('rating', 0) * 0.1
            results[movie['movie_id']] = {'content': content_score, 'collab': 0, 'trend': 0}

        # Collaborative
        collab_recs = self.get_collaborative_recommendations(user_id, interactions)
        for rec in collab_recs:
            mid = rec['movie_id']
            if mid in results:
                results[mid]['collab'] = rec['score']
            else:
                results[mid] = {'content': 0, 'collab': rec['score'], 'trend': 0}

        # Trending
        trending = self.get_trending(movies)
        for t in trending:
            mid = t['movie_id']
            if mid in results:
                results[mid]['trend'] = t['score']
            else:
                results[mid] = {'content': 0, 'collab': 0, 'trend': t['score']}

        # Weighted combination
        final = []
        for mid, scores in results.items():
            combined = (scores['content'] * 0.4 +
                        scores['collab'] * 0.35 +
                        scores['trend'] * 0.25)
            final.append({'movie_id': mid, 'score': combined})

        final.sort(key=lambda x: x['score'], reverse=True)
        return final[:top_n]


# Singleton instance
engine = RecommendationEngine()

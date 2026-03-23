with open('access_service/access/models.py', 'r') as f:
    content = f.read()

movie_hash_model = """
class MovieHash(models.Model):
    \"\"\"Generated Access Keys (Hashes) waiting to be redeemed by the user.\"\"\"
    hash_code = models.CharField(max_length=100, unique=True)
    movie_id = models.IntegerField(db_index=True)
    movie_title = models.CharField(max_length=500, default='')
    user_id = models.IntegerField(db_index=True)  # The specific user it was generated for
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'movie_hashes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hash_code} for Movie {self.movie_id}"
"""

if "class MovieHash" not in content:
    content += "\n" + movie_hash_model

with open('access_service/access/models.py', 'w') as f:
    f.write(content)

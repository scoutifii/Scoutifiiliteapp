from django.db import connections
from scoutifiiapp.models import ShardedPost


def test_sharding():
    # Test data
    test_data = [
        {'user_id': 1, 'title': 'Post 1', 'content': 'Content for Post 1'},
        {'user_id': 2, 'title': 'Post 2', 'content': 'Content for Post 2'},
        {'user_id': 3, 'title': 'Post 3', 'content': 'Content for Post 3'},
    ]

    # Create posts and verify shard routing
    for data in test_data:
        post = ShardedPost(**data)
        post.save(using=f'shard_{(data["user_id"] % (len(connections) - 1)) + 1}')
        print(f"Saved post for user_id {data['user_id']} to shard_{(data['user_id'] % (len(connections) - 1)) + 1}")

    # Verify data in shards
    for shard in range(1, len(connections)):
        with connections[f'shard_{shard}'].cursor() as cursor:
            cursor.execute("SELECT * FROM sharded_post")
            rows = cursor.fetchall()
            print(f"Data in shard_{shard}: {rows}")


if __name__ == "__main__":
    test_sharding()
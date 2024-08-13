from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


schema_registry_url = 'http://10.11.10.58:8081'

users_key_schema_str = """
{
    "type": "record",
    "name": "UsersKey",
    "fields": [
        {"name": "account_id", "type": "string"},
        {"name": "season_id", "type": "string"},
        {"name": "mode_id", "type": "string"}
    ]
}
"""
users_value_schema_str = """
{
    "type": "record",
    "name": "Users",
    "fields": [
        {"name": "account_id", "type": "string"},
        {"name": "season_id", "type": "string"},
        {"name": "mode_id", "type": "string"},
        {"name": "latest_nickname", "type": ["null", "string"], "default": null},
        {"name": "shard", "type": ["null", "string"], "default": null},
        {"name": "current_rp", "type": ["null", "int"], "default": null},
        {"name": "best_rp", "type": ["null", "int"], "default": null},
        {"name": "current_tier", "type": ["null", "string"], "default": null},
        {"name": "current_subtier", "type": ["null", "string"], "default": null},
        {"name": "best_tier", "type": ["null", "string"], "default": null},
        {"name": "best_subtier", "type": ["null", "string"], "default": null},
        {"name": "play_count", "type": ["null", "int"], "default": null},
        {"name": "avg_rank", "type": ["null", "float"], "default": null},
        {"name": "top10s", "type": ["null", "int"], "default": null},
        {"name": "wins", "type": ["null", "int"], "default": null},
        {"name": "kills", "type": ["null", "int"], "default": null},
        {"name": "assists", "type": ["null", "int"], "default": null},
        {"name": "deaths", "type": ["null", "int"], "default": null},
        {"name": "knockdowns", "type": ["null", "int"], "default": null},
        {"name": "total_damage", "type": ["null", "float"], "default": null},
        {"name": "kda", "type": ["null", "float"], "default": null},
        {"name": "latest_update", "type": ["null", "string"], "default": null}
    ]
}
"""
users_key_schema = avro.loads(users_key_schema_str)
users_value_schema = avro.loads(users_value_schema_str)
users_producer_config = {
    'bootstrap.servers': '10.11.10.58:9092',
    'schema.registry.url': schema_registry_url
}
users_producer = AvroProducer(users_producer_config, default_key_schema=users_key_schema, default_value_schema=users_value_schema)


def send_to_users(jsonified_ranked_stats_from_api):
    for mode_value in jsonified_ranked_stats_from_api.values():
        key = {
            "account_id": mode_value['account_id'],
            "season_id": mode_value['season_id'],
            "mode_id": mode_value['mode_id']
        }
        value = {
            "account_id": mode_value['account_id'],
            "season_id": mode_value['season_id'],
            "mode_id": mode_value['mode_id'],
            "latest_nickname": mode_value['latest_nickname'],
            "shard": mode_value['shard'],
            "current_rp": mode_value['current_rp'],
            "best_rp": mode_value['best_rp'],
            "current_tier": mode_value['current_tier'],
            "current_subtier": mode_value['current_subtier'],
            "best_tier": mode_value['best_tier'],
            "best_subtier": mode_value['best_subtier'],
            "play_count": mode_value['play_count'],
            "avg_rank": mode_value['avg_rank'],
            "top10s": mode_value['top10s'],
            "wins": mode_value['wins'],
            "kills": mode_value['kills'],
            "assists": mode_value['assists'],
            "deaths": mode_value['deaths'],
            "knockdowns": mode_value['knockdowns'],
            "total_damage": mode_value['total_damage'],
            "kda": mode_value['kda'],
            "latest_update": mode_value['latest_update']
        }
        users_producer.produce(topic='users-topic', key=key, value=value)
        users_producer.flush()

        print(f"sent key = {key}, value = {value} to users-topic.")

    return


matches_key_schema_str = """
{
    "type": "record",
    "name": "MatchesKey",
    "fields": [ 
        {"name": "match_id", "type": "string"}
    ]
}
"""
matches_value_schema_str = """
{
    "type": "record",
    "name": "Matches",
    "fields": [
        {"name": "match_id", "type": "string"},
        {"name": "mode_id", "type": ["null", "string"], "default": null},
        {"name": "season_id", "type": ["null", "string"], "default": null},
        {"name": "shard", "type": ["null", "string"], "default": null},
        {"name": "map_id", "type": ["null", "string"], "default": null},
        {"name": "duration", "type": ["null", "int"], "default": null},
        {"name": "played_at", "type": ["null", "string"], "default": null},
        {"name": "telemetry_url", "type": ["null", "string"], "default": null},
        {"name": "belligerence_avg", "type": ["null", "float"], "default": null},
        {"name": "belligerence_std", "type": ["null", "float"], "default": null},
        {"name": "combat_avg", "type": ["null", "float"], "default": null},
        {"name": "combat_std", "type": ["null", "float"], "default": null},
        {"name": "viability_avg", "type": ["null", "float"], "default": null},
        {"name": "viability_std", "type": ["null", "float"], "default": null},
        {"name": "utility_avg", "type": ["null", "float"], "default": null},
        {"name": "utility_std", "type": ["null", "float"], "default": null},
        {"name": "sniping_avg", "type": ["null", "float"], "default": null},
        {"name": "sniping_std", "type": ["null", "float"], "default": null}
    ]
}
"""
matches_key_schema = avro.loads(matches_key_schema_str)
matches_value_schema = avro.loads(matches_value_schema_str)
matches_producer_config = {
    'bootstrap.servers': '10.11.10.58:9092',
    'schema.registry.url': schema_registry_url
}
matches_producer = AvroProducer(matches_producer_config, default_key_schema=matches_key_schema, default_value_schema=matches_value_schema)


def send_to_matches(matches_key, matches_value):
    matches_producer.produce(topic='matches-topic', key=matches_key, value=matches_value)
    matches_producer.flush()

    print(f"sent key = {matches_key}, value = {matches_value} to matches-topic.")

    return


match_user_key_schema_str = """
{
    "type": "record",
    "name": "MatchUserKey",
    "fields" : [
        {"name": "account_id", "type": "string"},
        {"name": "match_id", "type": "string"}
    ]
}
"""
match_user_value_schema_str = """
{
    "type": "record",
    "name": "MatchUser",
    "fields" : [
        {"name": "account_id", "type": "string"},
        {"name": "season_id", "type": "string"},
        {"name": "match_id", "type": "string"},
        {"name": "mode_id", "type": ["null", "string"], "default": null},
        {"name": "shard", "type": ["null", "string"], "default": null},
        {"name": "total_shots", "type": ["null", "int"], "default": null},
        {"name": "total_distance", "type": ["null", "float"], "default": null},
        {"name": "kills", "type": ["null", "int"], "default": null},
        {"name": "assists", "type": ["null", "int"], "default": null},
        {"name": "ranking", "type": ["null", "int"], "default": null},
        {"name": "revives", "type": ["null", "int"], "default": null},
        {"name": "longest_kill_dist", "type": ["null", "float"], "default": null},
        {"name": "accuracy", "type": ["null", "float"], "default": null},
        {"name": "heal_count", "type": ["null", "int"], "default": null},
        {"name": "lifetime", "type": ["null", "int"], "default": null},
        {"name": "landed_location_x", "type": ["null", "float"], "default": null},
        {"name": "landed_location_y", "type": ["null", "float"], "default": null},
        {"name": "avg_kill_distance", "type": ["null", "float"], "default": null},
        {"name": "damage_dealt", "type": ["null", "float"], "default": null},
        {"name": "knockdowns", "type": ["null", "int"], "default": null},
        {"name": "boost_count", "type": ["null", "int"], "default": null},
        {"name": "throw_count", "type": ["null", "int"], "default": null},
        {"name": "vehicle_use_count", "type": ["null", "int"], "default": null},
        {"name": "damage_from_vehicle", "type": ["null", "float"], "default": null},
        {"name": "belligerence", "type": ["null", "float"], "default": null},
        {"name": "combat", "type": ["null", "float"], "default": null},
        {"name": "viability", "type": ["null", "float"], "default": null},
        {"name": "utility", "type": ["null", "float"], "default": null},
        {"name": "sniping", "type": ["null", "float"], "default": null}
    ]
}
"""
match_user_key_schema = avro.loads(match_user_key_schema_str)
match_user_value_schema = avro.loads(match_user_value_schema_str)
match_user_producer_config = {
    'bootstrap.servers': '10.11.10.58:9092',
    'schema.registry.url': schema_registry_url
}
match_user_producer = AvroProducer(match_user_producer_config, default_key_schema=match_user_key_schema, default_value_schema=match_user_value_schema)


def send_to_match_user(match_user_key, match_user_value):
    match_user_producer.produce(topic='match_user-topic', key=match_user_key, value=match_user_value)
    match_user_producer.flush()

    print(f"sent key = {match_user_key}, value = {match_user_value} to match_user-topic.")

    return


clustering_input_key_schema_str = """
{
    "type": "record",
    "name": "ClusteringInputKey",
    "fields" : [
        {"name": "session_id", "type": "string"}
    ]
}
"""
clustering_input_value_schema_str = """
{
    "type": "record",
    "name": "ClusteringInput",
    "fields": [
        {"name": "match_id", "type": "string"},
        {"name": "account_id", "type": "string"},
        {"name": "map_id", "type": "string"},
        {
            "name": "players_data",
            "type": {
                "type": "array",
                "items": {
                    "type": "record",
                    "name": "ClusteringInputPlayerData",
                    "fields": [
                        {"name": "account_id", "type": "string"},
                        {"name": "total_shots", "type": "int"},
                        {"name": "landing_coordinates_x", "type": "double"},
                        {"name": "landing_coordinates_y", "type": "double"}
                    ]
                }
            }
        }
    ]
}
"""
clustering_input_key_schema = avro.loads(clustering_input_key_schema_str)
clustering_input_value_schema = avro.loads(clustering_input_value_schema_str)
clustering_input_producer_config = {
    'bootstrap.servers': '10.11.10.58:9092',
    'schema.registry.url': schema_registry_url
}
clustering_input_producer = AvroProducer(clustering_input_producer_config, default_key_schema=clustering_input_key_schema, default_value_schema=clustering_input_value_schema)


def send_to_clustering_input(clustering_input_key, clustering_input_value):
    clustering_input_producer.produce(topic='clustering_input-topic', key=clustering_input_key, value=clustering_input_value)
    clustering_input_producer.flush()

    print(f"sent key = {clustering_input_key}, value = {clustering_input_value} to clustering_input-topic.")

    return

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import logging

logger = logging.getLogger(__name__)

kafka_broker = '10.11.10.58:9092'
schema_registry_url = 'http://10.11.10.58:8081'

class kafkaConnector:
    def __init__(self,kafka_broker, schema_registry_url):
        self.kafka_broker = kafka_broker
        self.schema_registry_url = schema_registry_url
        self.users_topic = 'users-topic'
        self.matches_topic = 'matches-topic'
        self.match_user_topic = 'match_user-topic'
        self.mlUser_topic = 'for_ml_user-topic'
        self.shot_topic = 'shot-topic'

    def produce_message(self, topic, key_schema_str, value_schema_str, key, value):
        print("############################## process def : produce_message ##############################")
        key_schema = avro.loads(key_schema_str)
        value_schema = avro.loads(value_schema_str)
        avro_producer = AvroProducer(
            {
                'bootstrap.servers': self.kafka_broker,
                'schema.registry.url': self.schema_registry_url
            },
            default_key_schema=key_schema,
            default_value_schema=value_schema
        )
        avro_producer.produce(topic=topic, key=key, value=value)
        avro_producer.flush()
        print(f"Record sent to Kafka topic '{topic}'")

    def produce_users_message(self, key, value):
        print("############################## process def : produce_users_message ##############################")
        key_schema_str = """
        {
        "type": "record",
        "name": "UsersKey",
        "fields": [
            {"name": "account_id",  "type": "string"},
            {"name": "season_id",   "type": "string"},
            {"name": "mode_id",     "type": "string"}
        ]
        }
        """
        value_schema_str = """
        {
        "type": "record",
        "name": "Users",
        "fields": [
            {"name": "account_id",      "type": "string"},
            {"name": "season_id",       "type": "string"},
            {"name": "mode_id",         "type": "string"},
            {"name": "latest_nickname", "type": ["null", "string"], "default": null},
            {"name": "shard",           "type": ["null", "string"], "default": null},
            {"name": "current_rp",      "type": ["null", "int"],    "default": null},
            {"name": "best_rp",         "type": ["null", "int"],    "default": null},
            {"name": "current_tier",    "type": ["null", "string"], "default": null},
            {"name": "current_subtier", "type": ["null", "string"], "default": null},
            {"name": "best_tier",       "type": ["null", "string"], "default": null},
            {"name": "best_subtier",    "type": ["null", "string"], "default": null},
            {"name": "play_count",      "type": ["null", "int"],    "default": null},
            {"name": "avg_rank",        "type": ["null", "float"],  "default": null},
            {"name": "top10s",          "type": ["null", "int"],    "default": null},
            {"name": "wins",            "type": ["null", "int"],    "default": null},
            {"name": "kills",           "type": ["null", "int"],    "default": null},
            {"name": "assists",         "type": ["null", "int"],    "default": null},
            {"name": "deaths",          "type": ["null", "int"],    "default": null},
            {"name": "knockdowns",      "type": ["null", "int"],    "default": null},
            {"name": "total_damage",    "type": ["null", "float"],  "default": null},
            {"name": "kda",             "type": ["null", "float"],  "default": null},
            {"name": "latest_update",   "type": ["null", "string"], "default": null}
        ]
        }
        """
        self.produce_message(self.users_topic, key_schema_str, value_schema_str, key, value)

    def produce_matches_message(self, key, value):
        print("##############################process def : produce_matches_message ##############################")
        key_schema_str = """
        {
        "type": "record",
        "name": "MatchesKey",
        "fields": [
            {"name": "match_id", "type": "string"}
        ]
        }
        """
        value_schema_str = """
        {
        "type": "record",
        "name": "Matches",
        "fields": [
            {"name": "match_id",        "type": "string"},
            {"name": "mode_id",         "type": ["null", "string"], "default": null},
            {"name": "season_id",       "type": ["null", "string"], "default": null},
            {"name": "shard",           "type": ["null", "string"], "default": null},
            {"name": "map_id",          "type": ["null", "string"], "default": null},
            {"name": "duration",        "type": ["null", "int"],    "default": null},
            {"name": "played_at",       "type": ["null", "string"], "default": null},
            {"name": "telemetry_url",   "type": ["null", "string"], "default": null},
            {"name": "belligerence_avg","type": ["null", "float"],  "default": null},
            {"name": "belligerence_std","type": ["null", "float"],  "default": null},
            {"name": "combat_avg",      "type": ["null", "float"],  "default": null},
            {"name": "combat_std",      "type": ["null", "float"],  "default": null},
            {"name": "viability_avg",   "type": ["null", "float"],  "default": null},
            {"name": "viability_std",   "type": ["null", "float"],  "default": null},
            {"name": "utility_avg",     "type": ["null", "float"],  "default": null},
            {"name": "utility_std",     "type": ["null", "float"],  "default": null},
            {"name": "sniping_avg",     "type": ["null", "float"],  "default": null},
            {"name": "sniping_std",     "type": ["null", "float"],  "default": null}
        ]
        }
        """
        self.produce_message(self.matches_topic, key_schema_str, value_schema_str, key, value)

    def produce_matchUser_message(self, key, value):
        logger.info("############################## process def : produce_matchUser_message ##############################")
        
        key_schema_str = """
        {
        "type": "record",
        "name": "MatchUserKey",
        "fields": [
            {"name": "account_id",  "type": "string"},
            {"name": "match_id",    "type": "string"}
        ]
        }
        """
        value_schema_str = """
        {
        "type": "record",
        "name": "MatchUser",
        "fields": [
            {"name": "account_id",          "type": "string"},
            {"name": "season_id",           "type": "string"},
            {"name": "mode_id",             "type": ["null", "string"], "default": null},
            {"name": "match_id",            "type": "string"},
            {"name": "shard",               "type": ["null", "string"], "default": null},
            {"name": "total_shots",         "type": ["null", "int"],    "default": null},
            {"name": "total_distance",      "type": ["null", "float"],  "default": null},
            {"name": "kills",               "type": ["null", "int"],    "default": null},
            {"name": "assists",             "type": ["null", "int"],    "default": null},
            {"name": "ranking",             "type": ["null", "int"],    "default": null},
            {"name": "revives",             "type": ["null", "int"],    "default": null},
            {"name": "longest_kill_dist",   "type": ["null", "float"],  "default": null},
            {"name": "accuracy",            "type": ["null", "float"],  "default": null},
            {"name": "heal_count",          "type": ["null", "int"],    "default": null},
            {"name": "lifetime",            "type": ["null", "int"],    "default": null},
            {"name": "landed_location_x",   "type": ["null", "float"],  "default": null},
            {"name": "landed_location_y",   "type": ["null", "float"],  "default": null},
            {"name": "avg_kill_distance",   "type": ["null", "float"],  "default": null},
            {"name": "damage_dealt",        "type": ["null", "float"],  "default": null},
            {"name": "knockdowns",          "type": ["null", "int"],    "default": null},
            {"name": "boost_count",         "type": ["null", "int"],    "default": null},
            {"name": "throw_count",         "type": ["null", "int"],    "default": null},
            {"name": "vehicle_use_count",   "type": ["null", "int"],    "default": null},
            {"name": "damage_from_vehicle", "type": ["null", "float"],  "default": null},
            {"name": "belligerence",        "type": ["null", "float"],  "default": null},
            {"name": "combat",              "type": ["null", "float"],  "default": null},
            {"name": "viability",           "type": ["null", "float"],  "default": null},
            {"name": "utility",             "type": ["null", "float"],  "default": null},
            {"name": "sniping",             "type": ["null", "float"],  "default": null}
        ]
        }
        """
    
        try:
            logger.debug(f"Producing message with key: {key} and value: {value}")
            self.produce_message(self.match_user_topic, key_schema_str, value_schema_str, key, value)
            logger.info("Message produced successfully")
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")

    def produce_mlUser_message(self, key, value):
        print("##############################process def : produce_mlUser_message ##############################")
        key_schema_str = """
        {
        "type": "record",
        "name": "mlUserKey",
        "fields": [
            {"name": "account_id",  "type": "string"},
            {"name": "match_id",    "type": "string"}
        ]
        }
        """
        value_schema_str = """
        {
        "type": "record",
        "name": "mlUser",
        "fields": [
            {"name": "account_id",    "type": "string"},
            {"name": "match_id",      "type": "string"},
            {"name": "current_tier",  "type": ["null", "string"],   "default": null},
            {"name": "kills",         "type": ["null", "int"],      "default": null},
            {"name": "knockdowns",    "type": ["null", "int"],      "default": null},
            {"name": "assists",       "type": ["null", "int"],      "default": null},
            {"name": "total_damage",  "type": ["null", "float"],    "default": null},
            {"name": "total_shot",    "type": ["null", "int"],      "default": null},
            {"name": "hit_count",     "type": ["null", "int"],      "default": null},
            {"name": "head_shot",     "type": ["null", "int"],      "default": null}
        ]
        }
        """
        try:
            logger.debug(f"Producing message with key: {key} and value: {value}")
            self.produce_message(self.mlUser_topic, key_schema_str, value_schema_str, key, value)
            logger.info("Message produced successfully")
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")


    def produce_shot_message(self, key, value):
        print("##############################process def : produce_shot_message ##############################")
        key_schema_str = """
        {
        "type": "record",
        "name": "shotKey",
        "fields": [
            {"name": "match_id",    "type": "string"},
            {"name": "attack_id",   "type": "int"}
        ]
        }
        """
        value_schema_str = """
        {
        "type": "record",
        "name": "shot",
        "fields": [
            {"name": "account_id",  "type": ["null", "string"], "default": null},
            {"name": "match_id",    "type": "string"},
            {"name": "attack_id",   "type": "int"},
            {"name": "weapon_id",   "type": ["null", "string"], "default": null},
            {"name": "is_hit",      "type": "boolean",          "default": false},
            {"name": "hit_point",   "type": ["null", "string"], "default": null},
            {"name": "hit_distance","type": ["null", "float"],  "default": null},
            {"name": "timeStamp",   "type": ["null", "string"], "default": null}

        ]
        }
        """
        try:
            logger.debug(f"Producing message with key: {key} and value: {value}")
            self.produce_message(self.shot_topic, key_schema_str, value_schema_str, key, value)
            logger.info("Message produced successfully")
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")

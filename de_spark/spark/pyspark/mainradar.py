from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, stddev, round
from confluent_kafka.schema_registry import SchemaRegistryClient
from pyspark.sql.avro.functions import from_avro
import pyspark.sql.functions as func
import redis
import json
import time

# Redis 설정
redis_host = '10.11.10.125'
redis_port = 6379

# Kafka config 설정
kafka_bootstrap_servers = "10.11.10.58:9092"
schema_registry_url = "http://10.11.10.58:8081"
topic = "users-topic"

# 스키마 레지스트리 클라이언트 설정
schema_registry_client = SchemaRegistryClient({'url': schema_registry_url})
input_subject_key = "users-topic-key"
input_subject_value = "users-topic-value"
key_schema = schema_registry_client.get_latest_version(input_subject_key).schema.schema_str
value_schema = schema_registry_client.get_latest_version(input_subject_value).schema.schema_str

# print(key_schema)
# print("---------------------------")
# print(value_schema)

# Redis로 데이터 보내기
def send_to_redis(partition):
    r = redis.StrictRedis(
        host=redis_host, 
        port=redis_port, 
        db=0,
        socket_timeout=10,  # 타임아웃 설정
        socket_connect_timeout=10,
        retry_on_timeout=True
    )
    for row in partition:
        try:
            key = f"{row['mode_id']}"
            value = json.dumps({
                "kills_avg": row['kills_avg'],
                "kills_std": row['kills_std'],
                "deaths_avg": row['deaths_avg'],
                "deaths_std": row['deaths_std'],
                "assists_avg": row['assists_avg'],
                "assists_std": row['assists_std'],
                "kda_avg": row['kda_avg'],
                "kda_std": row['kda_std'],
                "avg_rank_avg": row['avg_rank_avg'],
                "avg_rank_std": row['avg_rank_std']
            })
            retries = 3
            while retries > 0:
                try:
                    r.set(key, value)
                    print(f"Complete to Redis: {key}")
                    break
                except redis.ConnectionError as e:
                    retries -= 1
                    print(f"Redis connection error: {e}. Retries left: {retries}")
            if retries == 0:
                print(f"Failed to send data to Redis after retries: {key}")
        except Exception as e:
            print(f"Exception during Redis set: {e}")

# Global state to keep track of the count and buffer
global_state = {"count": 0, "buffer": []}
# foreachBatch 함수 정의
def foreach_batch_function(batch_df, batch_id):
    # 시작 시간 기록
    start_time = time.time()  

    # 현재 배치의 레코드 수를 계산
    current_batch_count = batch_df.count()
    print(f"Batch ID: {batch_id}, Number of records in this batch: {current_batch_count}")

    if current_batch_count > 0:
        # 현재 배치 데이터 가져오기
        global_state["buffer"].extend(batch_df.collect()) # 버퍼에 현재 df의 데이터 저장 
        global_state["count"] += current_batch_count     

        # 3000개 이상이 되면 데이터를 저장
        while global_state["count"] >= 3000:
            # 3000개 데이터를 가져오기
            batch_to_write = global_state["buffer"][:300]
            redis_df = spark.createDataFrame(batch_to_write, batch_df.schema)

            # mode_id 오류값 필터링
            redis_df = redis_df.filter(redis_df.mode_id.isin('squad','squad-fpp','solo','solo-fpp'))

            redis_df.filter(col("mode_id") == "solo").show()
            redis_df.show()

            # kill_per_game, deaths_per_game, assists_per_game, kda, avg_rank의 평균과 표준오차를 구함
            agg_df = redis_df.groupBy("mode_id").agg(
                round(mean("kills_per_game"), 1).alias("kills_avg"),
                round(stddev("kills_per_game"), 1).alias("kills_std"),
                round(mean("deaths_per_game"), 1).alias("deaths_avg"),
                round(stddev("deaths_per_game"), 1).alias("deaths_std"),
                round(mean("assists_per_game"), 1).alias("assists_avg"),
                round(stddev("assists_per_game"), 1).alias("assists_std"),
                round(mean("kda"), 1).alias("kda_avg"),
                round(stddev("kda"), 1).alias("kda_std"),
                round(mean("avg_rank"), 1).alias("avg_rank_avg"),
                round(stddev("avg_rank"), 1).alias("avg_rank_std")
            )

            # 결과 출력
            agg_df.show()
            agg_df.foreachPartition(send_to_redis)
            print("start to redis")

            # 경과 시간 계산
            end_time = time.time()
            elapsed_time = end_time - start_time  # 경과 시간 계산
            print(f"Processing time: {elapsed_time} seconds")

            # Global state 업데이트
            global_state["buffer"] = global_state["buffer"][3000:]
            global_state["count"] -= 3000

    # 3000개 미만인 경우 로그 출력
    if global_state["count"] < 3000:
        print(f"Batch ID: {batch_id}, Current count: {global_state['count']}, Not enough data to write to Redis")

if __name__ == '__main__':
    # SparkSession 생성
    spark = SparkSession.builder \
        .appName("MainRadarChart") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .config("spark.jars.packages", "org.apache.commons:commons-pool2:2.11.1")\
        .config("spark.jars.packages", "com.redislabs:spark-redis:3.1.0") \
        .config("spark.redis.host", redis_host)\
        .config("spark.redis.port", str(redis_port))\
        .config("spark.dynamicAllocation.enabled", "false")\
        .getOrCreate()

    df = spark.readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false")\
        .option("maxOffsetsPerTrigger", 3000)\
        .load() 
    df.printSchema()

    # # Magic Byte와 Schema ID 추출
    # df = df.withColumn("magicByte", func.expr("substring(value, 1, 1)"))
    # df = df.withColumn("keySchemaId", func.expr("substring(key, 2, 4)"))
    # df = df.withColumn("valueSchemaId", func.expr("substring(value, 2, 4)"))

    # 첫 5바이트를 제거하여 실제 Avro 데이터 추출
    df = df.withColumn("key_avroBytes", func.expr("substring(key, 6, length(key)-5)"))
    df = df.withColumn("value_avroBytes", func.expr("substring(value, 6, length(value)-5)"))
    df.printSchema()

    # Avro 데이터 역직렬화(from_avro())
    df = df.select(   
            from_avro(col("value_avroBytes"), value_schema,{"mode":"PERMISSIVE"}).alias("data") #permissive를 통해 에러가 발생한 레코드는 null로 반환하고 streaming 유지
        ).select("data.*")
    
    # 필요한 필드 선택 및 새로운 필드 계산
    df = df.select(
        col("mode_id"),
        (col("kills") / col("play_count")).alias("kills_per_game"),
        (col("deaths") / col("play_count")).alias("deaths_per_game"),
        (col("assists") / col("play_count")).alias("assists_per_game"),
        col("kda"),
        col("avg_rank")
    )
   
    # 트리거 설정 및 foreachBatch 설정
    query = df.writeStream \
        .outputMode("append") \
        .foreachBatch(foreach_batch_function) \
        .option("checkpointLocation", "/home/ec2-user/spark/checkpoint/mainradarchart")\
        .trigger(processingTime='30 seconds') \
        .start()
    
    query.awaitTermination()
  

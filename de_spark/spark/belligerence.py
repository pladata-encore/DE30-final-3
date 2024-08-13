from pyspark.sql import SparkSession
from pyspark.sql.functions import col, struct, when, abs as spark_abs, explode, avg, stddev, lit, udf
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.avro.functions import from_avro
from confluent_kafka.schema_registry import SchemaRegistryClient
from kmeanscluster import perform_kmeans_clustering
from enum import Enum
import pyspark.sql.functions as func
import redis
import json
import time

# SparkSession 생성
spark = SparkSession.builder \
    .appName("PUBG Belligerence Calculation_local_3") \
    .master("local[1]")\
    .config("spark.jars", "/home/ec2-user/spark/spark-redis_2.12-3.1.0.jar,/home/ec2-user/spark/commons-pool2-2.11.1.jar") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,\
            org.apache.spark:spark-avro_2.12:3.5.1,\
            io.confluent:kafka-schema-registry-client:6.2.0") \
    .config("spark.default.parallelism","1")\
    .config("spark.sql.shuffle.partitions","1")\
    .getOrCreate()

# Kafka config 설정
kafka_bootstrap_servers = "10.11.10.58:9092"
schema_registry_url = "http://10.11.10.58:8081"
topic = "clustering_input-topic"

# Redis 설정
redis_host = '10.11.10.125'
redis_port = 6379

# 스키마 레지스트리 클라이언트 설정
schema_registry_client = SchemaRegistryClient({'url': schema_registry_url})
input_subject_key = f"{topic}-key"
input_subject_value = f"{topic}-value"
key_schema = schema_registry_client.get_latest_version(input_subject_key).schema.schema_str
value_schema = schema_registry_client.get_latest_version(input_subject_value).schema.schema_str

# # 스키마 확인용 출력문
# print("Key Schema: ", key_schema)
# print(type(key_schema))
# print("--------------------------------------------------------")
# print("Value Schema: ", value_schema)
# print("--------------------------------------------------------")

# Kafka 데이터 읽기
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", topic) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false")\
    .load() 

# Kafka 데이터의 key와 value를 바이너리 형식으로 캐스팅
df = df.selectExpr("CAST(key AS BINARY) as key", "CAST(value AS BINARY) as value")

# # Magic Byte와 Schema ID 추출
# df = df.withColumn("magicByte", func.expr("substring(value, 1, 1)"))
# df = df.withColumn("keySchemaId", func.expr("substring(key, 2, 4)"))
# df = df.withColumn("valueSchemaId", func.expr("substring(value, 2, 4)"))

# 첫 5바이트(Magic bytesm, Schema ID)를 제거하여 실제 Avro 데이터 추출
df = df.withColumn("key_avroBytes", func.expr("substring(key, 6, length(key)-5)"))
df = df.withColumn("value_avroBytes", func.expr("substring(value, 6, length(value)-5)"))

# Avro 데이터 역직렬화(from_avro())
df = df.select(
        from_avro(col("key_avroBytes"), key_schema,{"mode":"PERMISSIVE"}).alias("key_data"),   #permissive를 통해 에러가 발생한 레코드는 null로 반환하고 streaming 유지
        from_avro(col("value_avroBytes"), value_schema,{"mode":"PERMISSIVE"}).alias("data")
    ).select("key_data.*", "data.*")

# # players_data 배열을 개별 행으로 분리
df = df.withColumn("player", explode(col("players_data"))) \
       .select(
           col("session_id"),
           col("match_id"),
           col("account_id"),
           col("map_id"),
           col("player.account_id").alias("player_account_id"),
           col("player.total_shots"),
           col("player.landing_coordinates_x").alias("landed_location_x"),
           col("player.landing_coordinates_y").alias("landed_location_y")
       )

# landed_zone_y 값을 숫자로 변환 및 맵에 따른 조정
map_y_offsets = {
    'Desert_Main': 816000,
    'Baltic_Main': 816000,
    'DihorOtok_Main': 816000,
    'Erangel_Main': 816000,
    'Tiger_Main': 816000,
    'Neon_Main': 816000,
    'Kiki_Main': 816000,
    'Savage_Main': 408000,
    'Chimera_Main': 306000,
    'Summerland_Main': 204000,
    'Heaven_Main': 102000
}
#Broadcast 변수 생성
map_y_offsets_broadcast = spark.sparkContext.broadcast(map_y_offsets)

# 데이터 처리 및 클러스터링 함수
def process_data(df):
    # 데이터가 비어있는지 확인
    if df.rdd.isEmpty():
        return None
    
    map_y_offsets = map_y_offsets_broadcast.value
    for map_name, offset in map_y_offsets.items():
        df = df.withColumn("landed_location_y", 
                           when(col("map_id") == map_name, offset - spark_abs(col("landed_location_y")))
                           .otherwise(col("landed_location_y")))

    # Spark DataFrame을 Pandas DataFrame으로 변환
    df_pandas = df.toPandas()

    #클러스터링 수행
    df = perform_kmeans_clustering(df_pandas,features_cols=["landed_location_x", "landed_location_y"])
    df = spark.createDataFrame(df)
    
    # 클러스터 점수 계산
    cluster_counts = df.filter(df["cluster"] != -1).groupBy("cluster").count()
    cluster_scores_df = cluster_counts.withColumnRenamed("count", "cluster_score")

    # Join to add cluster scores to the main dataframe
    df = df.join(cluster_scores_df, df["cluster"] == cluster_scores_df["cluster"], "left_outer") \
           .drop(cluster_scores_df["cluster"])

    # 가중치 계산
    df = df.withColumn("belligerence", col("cluster_score") * 20 + col("total_shots")) 

    return df

# Redis로 데이터 보내기
def send_to_redis(partition):
    r = redis.Redis(
        host=redis_host, 
        port=redis_port, 
        db=0,
        socket_timeout=10,  # 타임아웃 설정
        socket_connect_timeout=10,
        retry_on_timeout=True
    )
    for row in partition:
        try:
            key = f"{row['session_id']}"
            value = json.dumps({
                "match_id": row['match_id'],
                "account_id": row['account_id'],
                "belligerence": row['belligerence'],
                "belligerence_avg": row['belligerence_avg'],
                "belligerence_std": row['belligerence_std'],
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

# 클러스터링 결과 저장 및 출력 함수
def save_and_show(df, epoch_id):
    start_time = time.time()  # 시작 시간 기록
    df_processed = process_data(df)
    if df_processed is None:
        print("Empty batch received, skipping processing.")
        return

    # 필요한 컬럼만 선택 및 컬럼명 변경
    df_selected = df_processed.select(
        col("session_id"),
        col("match_id"),
        col("player_account_id").alias("account_id"),
        col("belligerence")
    )

    # 호전성의 평균과 표준편차 계산
    belligerence_stats = df_selected.agg(
        avg("belligerence").alias("belligerence_avg"),
        stddev("belligerence").alias("belligerence_std")
    ).collect()[0]
    
    df_selected = df_selected.withColumn("belligerence_avg", lit(belligerence_stats["belligerence_avg"])) \
                         .withColumn("belligerence_std", lit(belligerence_stats["belligerence_std"])) \
                         .limit(1)
    df_selected.foreachPartition(send_to_redis)
    print("start to redis")

    # 경과 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time  
    print(f"Processing time: {elapsed_time} seconds")
    
# 스트리밍 쿼리 정의 및 실행
query = df.writeStream \
    .foreachBatch(save_and_show) \
    .outputMode("append") \
    .option("checkpointLocation", "/home/ec2-user/spark/checkpoint/belligerence")\
    .start()

query.awaitTermination()


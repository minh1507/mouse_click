//mongo
docker exec -it mouse-tracker-mongodb mongosh

use mouse_tracker

db.events.count()

//hdfs
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' hdfs-namenode



curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @init.json

curl http://localhost:8083/connectors

curl http://localhost:8083/connectors/hdfs3-sink-connector/status

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d "{\"name\":\"mongo-source-connector\",\"config\":{\"connector.class\":\"com.mongodb.kafka.connect.MongoSourceConnector\",\"tasks.max\":\"1\",\"connection.uri\":\"mongodb://kafka:password@mongodb:27017/?replicaSet=rs0\",\"database\":\"mouse_tracker\",\"collection\":\"events\",\"topic.prefix\":\"mongo\",\"output.format.key\":\"json\",\"output.format.value\":\"json\",\"output.schema.infer.value\":\"true\",\"change.stream.full.document\":\"updateLookup\"}}"

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d "{\"name\":\"hdfs3-sink-connector\",\"config\":{\"connector.class\":\"io.confluent.connect.hdfs3.Hdfs3SinkConnector\",\"topics\":\"mongo.mouse_tracker.events\",\"tasks.max\":\"1\",\"hdfs.url\":\"hdfs://hdfs-namenode:9000\",\"flush.size\":\"1\",\"format.class\":\"io.confluent.connect.hdfs3.avro.AvroFormat\",\"hadoop.conf.dir\":\"/etc/hadoop/conf\",\"key.converter\":\"org.apache.kafka.connect.storage.StringConverter\",\"value.converter\":\"io.confluent.connect.avro.AvroConverter\",\"value.converter.schema.registry.url\":\"http://schema-registry:8081\",\"value.converter.schemas.enable\":\"true\",\"partitioner.class\":\"io.confluent.connect.storage.partitioner.DefaultPartitioner\",\"topics.dir\":\"/kafka\",\"confluent.topic.bootstrap.servers\":\"kafka:9092\"}}"

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json"  -d @mongo.json

curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @hdfs.json

// kafka connect
# Mở terminal vào container hdfs-namenode
docker exec -it hdfs-namenode bash

# Tạo thư mục
hdfs dfs -mkdir /kafka-data

# Cấp quyền ghi cho appuser (hoặc cho tất cả mọi người)
hdfs dfs -chmod 777 /kafka-data

hdfs dfs -chown appuser /kafka-data


hdfs dfs -ls /kafka/mongo.mouse_tracker.events/partition=0

hdfs dfs -cat /kafka/mongo.mouse_tracker.events/partition=0/mongo.mouse_tracker.events+0+0000000113+0000000113.json

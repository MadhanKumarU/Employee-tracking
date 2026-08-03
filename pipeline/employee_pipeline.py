from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("EmployeePipeline").getOrCreate()

df = spark.read.csv(
    "data/employee_attendance.csv",
    header=True,
    inferSchema=True
)

report = df.filter(
    (col("working_hours") < 7) |
    (col("idle_hours") > 2)
)

report.show()

report.write.mode("overwrite").csv("reports/hr_report")

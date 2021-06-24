Global / version := "1.0"
Global / libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.1.1" % "provided",
  "org.apache.spark" %% "spark-streaming" % "3.1.1" % "provided",
  "org.apache.spark" %% "spark-streaming-kafka-0-10" % "3.1.1",
  "com.github.jnr" % "jnr-posix" % "3.1.5",
  "net.debasishg" %% "redisclient" % "3.30",
  "io.jvm.uuid" %% "scala-uuid" % "0.3.1",
  "com.google.guava" % "guava" % "16.0.1",
  "com.datastax.oss" % "java-driver-core" % "4.11.1",
  "com.datastax.oss" % "java-driver-query-builder" % "4.11.1")
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs@_*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
assembly / assemblyJarName := "BotDetectDStream.jar"

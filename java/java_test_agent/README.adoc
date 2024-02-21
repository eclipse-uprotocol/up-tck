= Eclipse uProtocol TCK's Java Test Agent

== Introduction

This document explains the importance of a Test Agent and the steps to run the folder's Java Test Agent

== Prequisites

Need Eclipse and JAVA JDK

Git clone the entire up-tck project


== Steps to run Java Test Agent using a JAR file

1. In Eclipse, open the existing Java Maven project located in the folder up-tck\java\java_test_agent 
* If there are errors when importing a java folder, here is a guide: https://crunchify.com/mavenmvn-clean-install-update-project-and-project-clean-options-in-eclipse-ide-to-fix-any-dependency-issue/
* If Maven option is not found after right-clicking the java_test_agent Java Project, follow this: https://stackoverflow.com/questions/10362166/maven-option-is-not-found-in-eclipse
* If "Maven build ..." does not work with the goal "mvn clean install", then set the goal as "clean install"

2. To create a JAR file of the java_test_agent Java project, goto File -> Export -> Runnable JAR File -> Launch configuration: "Main - java_test_agent" -> (Update Export Destination e.g. Downloads) -> Library handling: Extract required libraries into generated JAR -> Finish

3. Place the newly-created "JavaTestAgent.jar" in the up-tck/java folder.

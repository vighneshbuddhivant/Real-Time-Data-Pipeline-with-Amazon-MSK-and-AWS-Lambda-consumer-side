# **Real-Time Data Pipeline with Amazon MSK and AWS Lambda Consumer Side**

## **Project Overview**
This project implements a real-time data pipeline using **Amazon MSK (Managed Streaming for Apache Kafka)** as the event source for **AWS Lambda**. The data flows through the MSK cluster and triggers a Lambda function that processes incoming messages. After processing, the data is stored in **Amazon S3**, **Amazon RDS**, and **Amazon DynamoDB**. The system is designed to be highly available and scalable, ensuring secure communication between services by utilizing AWS best practices such as VPCs, subnets, NAT gateways, and private networking.

## **Objective:**
- Stream real-time data from a Kafka producer to MSK.
- Trigger AWS Lambda on new messages from MSK.
- Process and transform the data in Lambda.
- Store transformed data in **Amazon S3**, **RDS**, and **DynamoDB** for future analysis.


## **Architecture**
![Architecture Diagram](./architecture.png)


## **MSK Cluster Architecture**
The MSK cluster is deployed in two availability zones with brokers in private subnets, ensuring high availability and fault tolerance. Public subnets are used only for the NAT Gateway and bastion host, ensuring that sensitive services remain private and secure.

## **Tools and Technologies Used**
- **Amazon MSK (Managed Streaming for Apache Kafka)**: For streaming data events.
- **AWS Lambda**: To process real-time data from MSK.
- **Amazon S3**: To store raw or transformed data.
- **Amazon RDS**: To store relational data.
- **Amazon DynamoDB**: For NoSQL data storage.
- **VPC, Subnets, NAT Gateway**: For networking and security.
- **EC2**: To manage Kafka topics and interact with MSK cluster.
- **AWS IAM Roles and Policies**: For secure communication between services.

## **Workflow**
1. **MSK (Managed Kafka Service)** is the primary event source in this architecture, running in **private subnets** for enhanced security. Kafka brokers are deployed in **multiple availability zones** for high availability.
   
2. **Amazon MSK triggers AWS Lambda** when a new message is published to an MSK topic.
   
3. **AWS Lambda** processes the message, performs transformations or data modifications, and writes the processed data into storage.
   
4. **NAT Gateway** is used to allow private resources (MSK brokers, private EC2 instances) to access the internet for necessary updates or communications with other AWS services.


## **Technical Details**

### **VPC and Networking**
1. **Create VPC**  
   - Name: `virtual-private-cloud-lambda`  
   - CIDR: `11.0.0.0/16`

2. **Create Subnets**:
   - **Public Subnet A** (11.0.0.0/24)
   - **Public Subnet B** (11.0.1.0/24)
   - **Private Subnet A** (11.0.2.0/24)
   - **Private Subnet B** (11.0.3.0/24)

3. **Configure Internet Gateway**: Attach an internet gateway to the VPC and associate it with the **public subnets**.

4. **Route Tables**:  
   - Public Route Table: Routes to the internet via the Internet Gateway.  
   - Private Route Table: Routes outgoing traffic to the NAT Gateway.

5. **NAT Gateway**:  
   - Create a NAT Gateway in the **public subnet** and attach it to the private subnet route table to enable the MSK cluster and private EC2 instances to communicate with external services.

### **Amazon MSK (Managed Kafka Service) Setup**
6. **Create MSK Cluster** in the private subnets.  
   - Configure MSK to use at least two availability zones to ensure high availability.
   - Use a **Kafka client** to create topics in the MSK cluster by launching an **EC2 instance in the private subnet**.

7. **Create Kafka Topic**:
   ```bash
   bin/kafka-topics.sh --create --topic demo_topic --bootstrap-server <broker_endpoints> --replication-factor 2 --partitions 2
   ```

### **Lambda and Trigger Configuration**
8. **Create AWS Lambda Function**:  
   Use the following Python code to process incoming Kafka messages:

```python
import base64
import boto3
import json

def lambda_handler(event, context):
    print("Event received from MSK:", event)
    for partition_key in event['records']:
        partition_value = event['records'][partition_key]
        for record_value in partition_value:
            message = (base64.b64decode(record_value['value'])).decode()
            print("Processed Message:", message)
            # Add transformation logic and save data to S3, RDS, DynamoDB here
```

9. **Add MSK as Trigger to Lambda**:  
   - Configure the MSK topic to invoke the Lambda function whenever a message is sent to the topic.

### **EC2 Instances for MSK Cluster Management**
10. **Launch EC2 Instances**:
    - **Public EC2 instance**: Acts as a bastion host to SSH into private EC2.
    - **Private EC2 instance**: Used for managing the MSK cluster and Kafka topics. Install Kafka CLI to create and test topics.

11. **Connect Public EC2 to Private EC2**:
    - Use SSH keys to connect from the **public EC2** to the **private EC2** for managing MSK topics.

12. **Install Kafka**:  
   SSH into the **private EC2** instance and install Kafka:
   ```bash
   sudo yum install java-1.8.0-openjdk
   wget https://archive.apache.org/dist/kafka/2.8.1/kafka_2.12-2.8.1.tgz
   tar -xvf kafka_2.12-2.8.1.tgz
   cd kafka_2.12-2.8.1
   ```

### **Testing**
13. **Kafka Producer**:
   Publish messages to the Kafka topic from the **private EC2** instance:
   ```bash
   bin/kafka-console-producer.sh --topic demo_topic --bootstrap-server <broker_endpoints>
   ```

14. **Kafka Consumer**:
   Use Kafka Console Consumer to verify if the messages are received on the **private EC2**:
   ```bash
   bin/kafka-console-consumer.sh --topic demo_topic --bootstrap-server <broker_endpoints>
   ```

15. **Verify Lambda Execution**:  
   Check **AWS CloudWatch Logs** to confirm that Lambda processed the Kafka messages and triggered the downstream actions (storing in S3, RDS, DynamoDB).


## **Conclusion**
This project showcases the integration of **Amazon MSK** with **AWS Lambda** to build a **highly available, scalable, and secure real-time data pipeline**. By utilizing AWS managed services, we significantly reduced operational overhead and improved the reliability of the system. The architecture ensures that data can be processed in real-time and stored in different services for further analysis and use.



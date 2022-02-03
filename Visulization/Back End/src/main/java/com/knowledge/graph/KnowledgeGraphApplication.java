package com.knowledge.graph;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;


@SpringBootApplication
@EnableAutoConfiguration
@MapperScan("com.knowledge.graph.mapper")
public class KnowledgeGraphApplication {
    public static void main(String[] args) {
        SpringApplication.run(KnowledgeGraphApplication.class);
    }
}

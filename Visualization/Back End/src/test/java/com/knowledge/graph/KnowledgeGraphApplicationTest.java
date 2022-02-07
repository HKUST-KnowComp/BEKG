package com.knowledge.graph;

import com.knowledge.graph.service.BIMService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = KnowledgeGraphApplication.class,webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class KnowledgeGraphApplicationTest {


    @Autowired
    private BIMService bimService;

    @Test
    void contextLoads() {
        System.out.println(bimService.getAnotherNodeWithRelationshipById(51l));
        System.out.println("查询成功");
    }
}

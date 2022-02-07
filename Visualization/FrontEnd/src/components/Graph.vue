<template>
  <div class="rootWin">
    <HeaderManu />
    <dmanu :detailList="param.detailList" :display="param.showDetail" />
    <smanu
      :nodesList="param.searchResult"
      @search="getNodesByName"
      @addNode="
        (node) => {
          this.addNode(node);
          this.rebuildGraph();
        }
      "
    ></smanu>
    <div class="container"></div>
  </div>
</template>

<script>
import manu from "./manu.vue";
import searchManu from "./searchManu.vue";
import HeaderManu from "./headerManu.vue";
import detailManu from "./detailManu.vue";

var d3 = require("d3");

export default {
  components: { manu, smanu: searchManu, HeaderManu, dmanu: detailManu },
  name: "Graph",
  data() {
    return {
      graph: { nodes: [], links: [] },

      linkWare: new Map(),

      selectors: {
        Node: [],
        Link: [],
        NodeText: [],
        LinkText: [],
        detailManu: [],
      },

      param: { searchResult: [], detailList: [], showDetail: false },

      config: {
        width: 1600,
        height: 1200,
        nodeRadius: 15,
        //力度调整，正数为引力
        strength: -20,
      },

      simulation: null,
    };
  },

  mounted() {
    this.createViewbox();

    this.createGraph(this.graph);

    console.log("mounted done");

    this.selectors.detailManu = d3.select(".detailManu").selectAll("div");
  },

  computed: {},

  methods: {
    //初始化viewBox
    createViewbox() {
      //创建视窗
      const svg = d3
        .select(".container")
        .append("svg")
        .classed("view", true)
        .attr("viewBox", [0, 0, this.config.width, this.config.height]);

      //用<g>包住结点和连接
      const group = svg.append("g").classed("group", true);

      const def = group.append("defs");

      const marker = def
        .append("marker")
        .attr("id", "arrow")
        .attr("markerUnists", "userSpaceOnUse")
        .attr("orient", "auto")
        .style("overflow", "visible")
        .append("path")
        .attr(
          "d",
          () =>
            `M${5.5 - this.config.nodeRadius},0,` +
            `L${-0 - this.config.nodeRadius},3,` +
            `L${-0 - this.config.nodeRadius},-3 z`
        );

      //
      //d3的缩放事件
      //创建缩放对象
      var zoom = d3
        .zoom()
        .scaleExtent([0.1, 10]) // 鼠标缩放的距离, 范围
        .on("zoom", (event) => {
          // console.log(e);
          d3.select(".view")
            .select(".group")
            .attr(
              "transform",
              `translate(${event.transform.x},${event.transform.y}) scale(${event.transform.k})`
            );
        }); //在.group的html上添加缩放属性

      //绑定对象到svg上，鼠标在，view上的缩放都会触发
      d3.select(".view")
        .call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(1));
    },

    // 建立图
    createGraph(d3_graph) {
      d3_graph.nodes = d3_graph.nodes.map((d) => Object.create(d));
      d3_graph.links = d3_graph.links.map((d) => {
        while (typeof d.source == "object") {
          d.source = d.source.id;
          d.target = d.target.id;
        }
        return Object.create(d);
      });

      //创建仿真器
      this.simulation = d3.forceSimulation(d3_graph.nodes).force(
        "link",
        d3
          .forceLink(d3_graph.links)
          .id((d, i) => {
            //这是links的source和target的识别根据，返回结点的id
            return d.id;
          })
          .distance((d, i) => 10 * this.config.nodeRadius)
      );

      // 设置仿真器参数
      this.simulation = this.simulation
        .force("charge", d3.forceManyBody().strength(this.config.strength))
        .force(
          "collide",
          d3.forceCollide().radius(() => 1.5 * this.config.nodeRadius)
        )
        .force(
          "center",
          d3.forceCenter(this.config.width / 2, this.config.height / 2.5)
        );

      //生成连接
      this.selectors.Link = d3
        .select(".group")
        .append("g")
        .classed("link", true)
        .selectAll("path")
        .data(d3_graph.links)
        .join("path")
        .attr("marker-end", "url(#arrow)")
        .attr("id", (d) => "linkId-" + d.id);

      // 生成结点
      this.selectors.Node = d3
        .select(".group")
        .append("g")
        .classed("node", true)
        .selectAll("circle")
        .data(d3_graph.nodes)
        .join("circle")
        .attr("id", (d) => "nodeId-" + d.id)
        .attr("r", this.config.nodeRadius)
        .attr("fill", this.color())

        // 绑定点击事件
        .on("click", (event, data) => {
          this.getRelationship(data.id);
        })
        .on("mouseover", (event, data) => {
          this.param.detailList = [
            data.id,
            data.properties.properties.lable,
            data.properties.properties.name,
          ];
          this.param.showDetail = true;
          d3.select(".detailManu")
            .style("left", event.clientX + "px")
            .style("top", event.clientY + "px");

          this.focusNode(data.id, false);
        })
        .on("mouseout", (event, data) => {
          this.param.showDetail = false;
          this.focusNode(data.id, true);
        })

        //调用拖动事件绑定
        .call(this.drag(this.simulation));

      this.selectors.Node.append("title").text((d) => {
        if (d.properties.properties.lable == "Entity2") {
          return "点击展开";
        } else return "";
      });

      this.selectors.NodeText = d3
        .select(".group")
        .append("g")
        .classed("nodeText", true)
        .selectAll("text")
        .data(d3_graph.nodes)
        .join("text")
        .attr("id", (d) => "nodeTextId-" + d.id)
        .text((d) => {
          return d.properties.properties.name;
        });

      this.selectors.NodeText.attr("text-anchor", "middle").attr(
        "dy",
        (d, i) => {
          return this.config.nodeRadius * 1.5;
        }
      );

      this.selectors.LinkText = d3
        .select(".group")
        .append("g")
        .classed("linkText", true)
        .selectAll("text")
        .data(d3_graph.links)
        .join("text")
        .attr("dy", "-3px")
        .attr("id", (d) => "linkTextId-" + d.id);

      this.selectors.LinkText.append("textPath")
        .attr("xlink:href", (d) => "#linkId-" + d.id)
        .text((d) => {
          return d.type;
        })
        .attr("startOffset", "50%");

      // 开启仿真器
      this.simulation.on("tick", () => {
        this.selectors.Link.attr("d", (d) => {
          var N;
          if (this.linkWare.has(d.key)) {
            N = this.linkWare.get(d.key);
          } else {
            console.log(`无法找到linkWare[${d.key}]`);
          }

          if (N == 1) {
            return `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`;
          }

          return this.getPath(
            { x: d.source.x, y: d.source.y },
            { x: d.target.x, y: d.target.y },
            d.linkNum,
            N
          );
        });
        //links的坐标仿真运动,根据id绑定位置

        this.selectors.Node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
        //nodes的坐标仿真运动

        this.selectors.NodeText.attr("x", (d) => d.x).attr("y", (d) => d.y);
      });
      //文本的仿真运动

      // invalidation.then(() => this.simulation.stop());

      return d3.select(".view").select(".group").node();
    },

    //重建图
    rebuildGraph() {
      this.simulation.stop();
      d3.select(".container")
        .select(".view")
        .select(".group")
        .selectAll("g")
        .remove();
      this.createGraph(this.graph);
      // console.log("graph:", this.graph);
    },

    //突出节点
    focusNode(id, flag) {
      var value;
      value = flag ? 1 : 0.15;

      this.selectors.Node.attr("fill-opacity", value).attr(
        "stroke-opacity",
        value
      );

      this.selectors.Link.attr("stroke-opacity", value);
      /* .selectAll("path")
        .attr("marker-end", (flag) => {
          flag ? "none" : "url(#arrow)";
        }); */
      this.selectors.NodeText.attr("opacity", value);
      this.selectors.LinkText.attr("opacity", value);

      d3.select("#nodeTextId-" + id).attr("opacity", 1);

      if (flag == false) {
        d3.select("#nodeId-" + id)
          .attr("fill-opacity", 1)
          .attr("stroke-opacity", 1);
        for (var i in this.graph.links) {
          var nodeId;
          var linkId = this.graph.links[i].id;

          if (this.graph.links[i].source.id == id)
            nodeId = this.graph.links[i].target.id;
          else if (this.graph.links[i].target.id == id)
            nodeId = this.graph.links[i].source.id;
          else continue; //判断匹配

          d3.select("#linkId-" + linkId).attr("stroke-opacity", 1);
          /*   .selectAll("path")
              .attr("marker-end", "url(#arrow)"); */

          d3.select("#nodeId-" + nodeId)
            .attr("fill-opacity", 1)
            .attr("stroke-opacity", 1);

          d3.select("#linkTextId-" + linkId).attr("opacity", 1);
          d3.select("#nodeTextId-" + nodeId).attr("opacity", 1);
        }
      }
    },

    // 根据关键词模糊搜索
    getNodesByName(key) {
      console.log("正在通过关键词搜索:", key);
      this.$axios
        .post("getNodeByName/" + key)
        .then((response) => {
          console.log("搜索关键字:", key, "成功", response);

          if (response.data.data.nodes.length == 0) {
            alert("数据库无匹配结果");
          } else {
            this.param.searchResult = response.data.data.nodes;
          }
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    // 根据id搜索存在关系
    getRelationship(id) {
      console.log("正在搜索关系:", id);
      this.$axios
        .get("getAnotherNodeById/" + id)
        .then((response) => {
          console.log("搜索Id关系:", id, "成功");
          // console.log("data", response.data.data);
          var anotherNodes =
            response.data.data.endNodesWithRelationship.anotherNodes;
          var relationshipNodes =
            response.data.data.endNodesWithRelationship.relationshipNodes;
          for (var i = 0; i < anotherNodes.length; i++) {
            this.addNode(anotherNodes[i]);
          }
          for (var i = 0; i < relationshipNodes.length; i++) {
            this.addRelationship(relationshipNodes[i]);
          }
          this.rebuildGraph();
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    //根据id搜索结点
    getNodeById(id) {
      this.$axios
        .get("getNodeById/" + id)
        .then((response) => {
          console.log("搜索结点Id:", id, "成功");
          console.log("data", response.data.data);
          this.addNode(response.data.data.node);
          this.rebuildGraph();
        })
        .catch(function (error) {
          console.log(error);
        });
    }, //dy

    getAllGraph() {
      console.log("正在取出所有节点和关系");
      this.$axios
        .get("getAllNode")
        .then((response) => {
          console.log("搜索所有结点成功", response.data.data.nodes);
          this.graph.nodes = [...response.data.data.nodes];
          this.getAllRelationship();
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    getAllRelationship() {
      this.$axios
        .get("getAllRelationship")
        .then((response) => {
          console.log("搜索所有关系成功", response.data.data.relationships);
          this.graph.links = [...response.data.data.relationships];
          this.rebuildGraph();
        })
        .catch(function (error) {
          console.log(error);
        });
    },

    //添加数据
    addNode(node) {
      var included = false;
      for (var i = 0; i < this.graph.nodes.length; i++) {
        // console.log(this.d3_graph.nodes[i].id);
        if (node.id == this.graph.nodes[i].id) included = true;
      }
      if (!included) {
        node.x = this.config.width / 2;
        node.y = this.config.height / 3;
        this.graph.nodes.push(node);
        // console.log("添加结点", node);
      }
    },

    addRelationship(relationship) {
      var included = false;
      for (var i = 0; i < this.graph.links.length; i++) {
        if (relationship.id == this.graph.links[i].id) included = true;
      }
      if (!included) {
        // console.log("添加关系:", relationship);
        var key = relationship.source + "->" + relationship.target;
        relationship.key = key;
        if (!this.linkWare.has(key)) {
          this.linkWare.set(key, 1);
          // console.log("创建", key, this.linkWare);
          relationship.linkNum = 0;
        } else {
          var value = this.linkWare.get(key);
          this.linkWare.set(key, value + 1);
          // console.log("添加", key, this.linkWare);
          relationship.linkNum = value;
        }

        this.graph.links.push(relationship);
      }
    },

    color() {
      const scale = d3.scaleOrdinal(d3.schemeCategory10);
      return (d) => scale(d.properties.properties.lable);
    }, //根据group属性进行分类

    drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
      //绑定3个事件
    },
    getPath(PBegin, PEnd, n, N) {
      var R = this.config.nodeRadius;
      var k;
      if (N % 2 ^ (n % 2 == 0)) {
        k = (n + 1) / 2;
      } else {
        k = n / -2;
      }

      var dis = k * R;
      var K_angle = Math.PI / 2;
      var angle = Math.atan2(PEnd.y - PBegin.y, PEnd.x - PBegin.x);
      var theta = angle + K_angle;

      var defx = dis * Math.cos(theta);
      var defy = dis * Math.sin(theta);

      return (
        `M${PBegin.x},${PBegin.y},` +
        `C${PBegin.x + defx},${PBegin.y + defy},` +
        `${PEnd.x + defx},${PEnd.y + defy},` +
        `${PEnd.x},${PEnd.y},`
      );
    },
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  margin: 0;
  padding: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;

  /* background: #0E1155; */
  /* background: #385663; */
  /* background:#FDD272; */
  /* background: #FFB26D; */
  /* background: #FF7F60; */
  /* background: #797F8C; */
  /*background: #f2e0d5;*/
  /* background: #A6938F; */
  /* background: #d9cbba; */
  background:#fff;

  border-radius: 5px;

  user-select: none;

  z-index: -10;
}
</style>

<style>
.view {
  overflow: visible;
  background: inherit;
}

.view #arrow {
  fill: #aaa;
}

.view .node {
  stroke: #fff;
  stroke-width: 1;
}

.view .node:hover {
  fill: #ff0005;
  stroke-width: 3px;
}

.view .link {
  stroke-width: 1.5;
  stroke: #999;
  fill: none;
}

.view .nodeText {
  fill: #666;
  font-size: 0.5em;
}

.view .linkText {
  fill: #666;
  text-anchor: middle;
  font-size: 0.5rem;
}
</style>

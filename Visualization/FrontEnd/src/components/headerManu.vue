<template>
  <div class="HeaderManu">
    <link
      href="http://fonts.googleapis.com/css?family=Anton"
      rel="stylesheet"
      type="text/css"
    />
    <link
      href="http://fonts.googleapis.com/css?family=Prompt:500"
      rel="stylesheet"
      type="text/css"
    />
    <input type="radio" name="chooseManu" id="knowledgeGraph" checked />
    <label for="knowledgeGraph">
      <div>knowledgeGraph</div>
    </label>

    <div class="chooseManu">
      <input type="radio" name="chooseManu" id="introduction" />
      <label for="introduction">
        <div>Introduction</div>
      </label>
      <div class="viewPage">
        <div></div>
        <div class="textPage">
          <h1>简介</h1>
          <p>
            知识图谱可以有效地通过引文聚类的分析方式，特别是通过在引文当中形成的网状关系进行深入的研究，进而可以有效地体现出每一个学科之间的亲缘关系以及具体的结构类型，还可以很好地对作者集体进行划分。同时，在分析的过程中，可以较为准确地对不同学科当中存在的交叉、渗透以及延伸的趋势进行分析。甚至还可以在分析的过程中，充分地掌握学科产生的背景、发展以及一些具有着突破性的成就，体现科学动态结构以及内在的一些发展规律。对于形成的科学图谱而言，就是通过形成的引文网络图，有效地对学科其前沿与学科当中的实际关系进行连接和梳理，进而充分保障研究人员能够在科研的过程中，有着较为可靠的技术支持。知识图谱已在电子政务、智慧金融、医疗健康等诸多领域得到广泛应用。
          </p>
        </div>
      </div>

      <input type="radio" name="chooseManu" id="operationGuide" />
      <label for="operationGuide">
        <div>Guide</div>
      </label>
      <div class="viewPage">
        <div></div>
        <div class="textPage">
          <h1>操作指南</h1>
          <p>
            - 在屏幕下方的搜索框输入需要的节点名称，
            可以不需要输入全名，点击放大镜或者键入Enter进行搜索。
          </p>
          <p>
            - 搜索结果会在搜索框的上方排列显示，
            点击需要的结果可以在图谱上添加相应的节点。
          </p>
          <p>- 鼠标移动到节点上会显示红色， 点击即可查看该节点的一阶邻居。</p>
          <p>- 鼠标移动到连线上会显示关系类型。</p>
        </div>
      </div>

      <input type="radio" name="chooseManu" id="others" />
      <label for="others">
        <div>Others</div>
      </label>
      <div class="viewPage">
        <div></div>
        <div class="textPage">其他</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style scoped>
.HeaderManu {
  width: 100vw;
  height: 6vh;
  min-height: 2.4rem;
  background-color: #4c594e;
  background: #607353;
  display: flex;

  position: sticky;
  top: 0;
}

.HeaderManu input {
  display: none;
}

.HeaderManu #knowledgeGraph + label {
  color: #f2f2f2;
  z-index: 100;
  flex-grow: 1;
  display: flex;
  justify-content: start;
  align-items: center;
}

.HeaderManu #knowledgeGraph + label div {
  font-family: "Anton", sans-serif;
  font-size: 2rem;
  text-align: center;
  padding: 0 3vw;
}

.chooseManu {
  z-index: inherit;
  position: relative;
  right: 0;
  background: inherit;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: 1fr;
}

.chooseManu label {
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-grow: 1;
}

.chooseManu label div {
  color: #f2f2f2;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 1.2rem;
  letter-spacing: 0.05rem;
  margin: 0 2rem;
}

.chooseManu input:checked + label {
  background: #f2a341;
}

.chooseManu label + .viewPage {
  display: none;
  background: rgba(0, 0, 0, 0);
  width: 100vw;
  height: 100%;
  position: fixed;
  left: 0;
  top: 0;
  font-size: 1rem;
  color: #f2f2f2;
}

.chooseManu label + .viewPage div:nth-child(1) {
  width: 100vw;
  height: 6vh;
  min-height: 2.4rem;
}

.chooseManu label + .viewPage div:nth-child(2) {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  min-height: 100vh;
  padding: 2cm;
  overflow: scroll;
}

.chooseManu input:checked + label + div {
  display: unset;
}

.chooseManu label + .viewPage div:nth-child(2) p {
  font-size: 1.3rem;
}
</style>
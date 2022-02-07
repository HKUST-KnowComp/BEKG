<template>
  <div class="searchManu">
    <div class="searchResult"></div>
    <div class="searchBox">
      <input
        type="text"
        class="search-text"
        placeholder="搜索节点"
        v-model="keyword"
        @keyup.enter="updateKey"
        @input="inputChange"
      />
      <button id="searchBottun" @click="updateKey">
        <svg class="search-icon" viewBox="0 0 23 23" fill="currentColor">
          <path
            fill-rule="evenodd"
            d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
var d3 = require("d3");

export default {
  name: "searchManu",
  props: {
    nodesList: {
      type: Array,
      default: () => {
        return ["name"];
      },
    },
  },
  data() {
    return {
      showList: [],
      keyword: "",
    };
  },

  mounted() {},

  watch: {
    nodesList: function () {
      this.showList = this.nodesList;
    },
    showList: function () {
      d3.select(".searchResult")
        .selectAll("div")
        .data(this.showList)
        .join("div")
        .text((d) => {
          return d.properties.properties.name;
        })
        .on("click", (event, d) => {
          this.showList = [];
          this.$emit("addNode", d);
        });
    },
  },

  methods: {
    updateKey() {
      if (this.keyword != "") {
        this.$emit("search", this.keyword);
      } else {
        alert("输入不能为空");
      }
    },
    inputChange() {
      if (this.showList != []) {
        this.showList = [];
      }
    },
  },
};
</script>

<style>
.searchManu {
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background-color: #373531;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(3px);
  display: flex;
  flex-direction: column;
  position: fixed;

  padding: 5px;
  border-radius: 6px;

  box-shadow: 0 1.7px 13.2px rgba(0, 0, 0, 0.037),
    0 4.3px 20.6px rgba(0, 0, 0, 0.049), 0 8.7px 26.4px rgba(0, 0, 0, 0.057),
    0 17.9px 34.2px rgba(0, 0, 0, 0.066), 0 49px 60px rgba(0, 0, 0, 0.08);
}

.searchResult {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.searchResult div {
  font-family: Arial, Helvetica, sans-serif;
  font-size: 1rem;
  color: #eee;
  user-select: none;
  padding-left: 1rem;
  margin-bottom: 0.5rem;
  margin-top: 0.2rem;
}

.searchResult div:hover {
  color: goldenrod;
}

.searchBox {
  display: flex;
  flex-direction: row;
  height: 1.6rem;
  background-color: #ffffff;

  padding: 3px;
  border-radius: 3px;
}

.search-text {
  width: 20rem;
  font-size: 0.8rem;
  background-color: #ffffff;
  border: none;
  /* outline: none; */
  outline-style: none;

  flex-grow: 1;
}

#searchBottun {
  border: none;
  background-color: #ffffff;
  padding: 0;
  margin: 0;
}

#searchBottun:active .search-icon {
  fill: #767169;
}

.search-icon {
  fill: #373531;
  stroke-width: 0;

  width: 2rem;
  height: 2rem;
}
</style>
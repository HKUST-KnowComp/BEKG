<template>
  <div class="detailManu">
    <div class="manuTitle">Node Info</div>
    <div class="detailItem">
      <div class="itemName">
        <div>id:</div>
        <div>label:</div>
        <div>name:</div>
      </div>
      <div class="itmeContent"></div>
    </div>
  </div>
</template>

<script>
var d3 = require("d3");
export default {
  name: "detailManu",
  props: {
    detailList: {
      type: Array,
      required: true,
    },

    display: {
      type: Boolean,
      required: true,
      default: false,
    },
  },

  data() {
    return {
      detailManu: null,
    };
  },

  mounted() {
    this.detailManu = d3.select(".detailManu").style("display", "none");
  },

  watch: {
    detailList: function (value) {
      // console.log({ value });

      this.detailManu
        .select(".itmeContent")
        .selectAll("div")
        .data(value)
        .join("div")
        .text((d) => d);
    },
    display: function (value) {
      // console.log({ value });

      if (value == true) {
        this.detailManu.style("display", "flex");
      } else {
        this.detailManu.style("display", "none");
      }
    },
  },
};
</script>

<style>
.detailManu {
  position: absolute;
  display: flex;
  background: rgba(2, 2, 2, 0.65);
  backdrop-filter: blur(3px);

  color: #eee;

  flex-direction: column;
  transform: translate(-100%, 30%);

  border-radius: 0.3rem;

  box-shadow: 0 20.5px 35.3px -5px rgba(0, 0, 0, 0.047),
    0 34.2px 55.8px -5px rgba(0, 0, 0, 0.064),
    0 43.2px 66.2px -5px rgba(0, 0, 0, 0.078),
    0 50.5px 72.1px -5px rgba(0, 0, 0, 0.093),
    0 61px 82.6px -5px rgba(0, 0, 0, 0.116),
    0 100px 137px -5px rgba(0, 0, 0, 0.18);

  overflow: hidden;
}
.detailManu .manuTitle {
  background: #668c4a;
  padding: 0.6rem;
  font-size: 1.1rem;
  text-align: center;
}

.detailManu .detailItem {
  display: flex;
  flex-direction: row;
}

.detailManu .detailItem div {
  padding: 0.2rem;
}
.detailManu .detailItem .itemName {
  text-align: center;
}
</style>
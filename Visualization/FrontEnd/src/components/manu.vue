<template>
  <div class="manu">
    <input type="checkbox" id="toggler" />
    <label for="toggler">
      <!-- <div class="box"></div> -->
      <div class="hamburger-container">
        <div></div>
        <div></div>
      </div>
    </label>

    <div class="manu-top"></div>
    <div class="manu-items">
      <ul>
        <li>item1</li>
        <li>item2</li>
        <li>item3</li>
        <li>item4</li>
        <li>item5</li>
        <li>item6</li>
        <li>item7</li>
        <li>item8</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "manu",
};
</script>

<style>
.manu {
  display: flex;
  position: fixed;
  flex-direction: column;

  left: 0.8rem;
  top: 0.9rem;
}

#toggler {
  display: none;
}

#toggler + label {
  width: 44px;
  height: 44px;
}

/* 开关 */

.hamburger-container {
  /* 横线容器 */
  background-color: #222;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
}

.hamburger-container div {
  /* 横线 */
  overflow: visible;
  background-color: #fff;
  position: relative;
  border-radius: 1px;
  height: 2px;
  width: 60%;

  transition: transform 0.3s ease-in-out, top 0.3s ease-in-out 0.3s;
}

.hamburger-container div:nth-child(1) {
  top: -4.5px;
}

.hamburger-container div:nth-child(2) {
  top: 4.5px;
}

#toggler:checked + label .hamburger-container div:nth-child(1) {
  top: 1px;
  transform: rotate(45deg);

  transition: top 0.3s ease-in-out, transform 0.3s ease-in-out 0.3s;
}

#toggler:checked + label .hamburger-container div:nth-child(2) {
  top: -1px;
  transform: rotate(-45deg);

  transition: top 0.3s ease-in-out, transform 0.3s ease-in-out 0.3s;
}

/* 菜单项 */
#toggler:checked ~ .manu-top {
  border-radius: 4px 4px 0 0;
  transform: scaleX(1);
  transition: border-radius 0.3s ease-in-out, transform 0.3s ease-in-out 0.3s;
}

#toggler:checked ~ .manu-items {
  transform: scaleY(1);
  opacity: 1;
  transform: all 0 ease-in-out;
  transition: transform 0.3s ease-in-out 0.6s, opacity 0.3s ease-in-out 0.6s;
}

.manu-top {
  width: 270px;
  height: 44px;
  background-color: #222;
  position: relative;
  top: -44px;
  z-index: -1;

  transform-origin: 0 0;
  transform: scaleX(calc(44 / 300));
  border-radius: 50%;
  transform: all 0;
  transition: transform 0.3s ease-in-out 0.3s,
    border-radius 0.3s ease-in-out 0.6s;
}

.manu-items {
  width: 270px;
  height: fit-content;
  background: rgba(32, 32, 32, 0.8);
  backdrop-filter: blur(3px);
  position: relative;
  top: -44px;
  z-index: -2;
  border-radius: 0 0 4px 4px;

  transform-origin: 0 0;
  transform: scaleY(0);
  opacity: 0;
  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;

  color: #fff;

  box-shadow: 0 1.5px 26.6px -17px rgba(0, 0, 0, 0.031),
    0 3.2px 36.2px -17px rgba(0, 0, 0, 0.046),
    0 5.5px 44px -17px rgba(0, 0, 0, 0.057),
    0 8.5px 51.8px -17px rgba(0, 0, 0, 0.066),
    0 12.6px 60.8px -17px rgba(0, 0, 0, 0.074),
    0 18.5px 72.3px -17px rgba(0, 0, 0, 0.083),
    0 27.8px 88.1px -17px rgba(0, 0, 0, 0.094),
    0 44.3px 112.8px -17px rgba(0, 0, 0, 0.109),
    0 83px 181px -17px rgba(0, 0, 0, 0.14);
}
</style>
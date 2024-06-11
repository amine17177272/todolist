console.log("JavaScript file is loaded and working.");
const menu = document.querySelector('.menu');
const links = document.querySelectorAll('.menu a');

function activateParallax() {
  links.forEach((link, i) => {
    link.addEventListener('mouseover', () => {
      menu.dataset.index = i
    }, false);
  });
}

window.addEventListener('load', activateParallax, false);
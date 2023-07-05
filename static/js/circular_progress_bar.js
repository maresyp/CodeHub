document.addEventListener("DOMContentLoaded", function() {
  var containers = document.querySelectorAll(".progressBarContainer");
  
  containers.forEach((container) => {
    var progress = container.getAttribute("data-progress");

    var bar = new ProgressBar.SemiCircle(container, {
      strokeWidth: 6,
      color: '#FFEA82',
      trailColor: '#eee',
      trailWidth: 1,
      easing: 'easeInOut',
      duration: 1400,
      svgStyle: null,
      text: {
        value: '',
        alignToBottom: false
      },
      from: {color: '#008000'},
      to: {color: '#FF0000'},
      step: (state, bar) => {
        bar.path.setAttribute('stroke', state.color);
        var value = Math.round(bar.value() * 100);
        if (value === 0) {
          bar.setText('');
        } else {
          bar.setText(value);
        }
        bar.text.style.color = state.color;
      }
    });

    bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    bar.text.style.fontSize = '2rem';

    // Przełożenie wartości na skale od 0 do 1
    var progressDecimal = progress / 100;

    bar.animate(progressDecimal);  // Number from 0.0 to 1.0
  });
});

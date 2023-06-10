// Po załadowaniu strony
document.addEventListener("DOMContentLoaded", function() {
    var progressCircles = document.querySelectorAll(".progress-circle");
  
    progressCircles.forEach(function(circle) {
      var progress = parseInt(circle.getAttribute("data-progress"));
      var radius = parseInt(circle.querySelector(".progress-circle__background").getAttribute("r"));
      var circumference = 2 * Math.PI * radius;
      var offset = circumference - (progress / 100) * circumference;
  
      circle.querySelector(".progress-circle__progress").style.strokeDashoffset = offset;
    });
  });
  
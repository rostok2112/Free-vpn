window.addEventListener('load', function() {
    var logoText = document.querySelector('.logo-text');
    var logoImage = document.querySelector('.logo-img');
    
    var logoTextHeight = logoText.clientHeight;
    logoImage.style.height = logoTextHeight + 25 + 'px';
});

function onProxyClick(url) {
    setTimeout(function () {
        document.querySelector('.loader-overlay').style.display = 'flex';
        window.location.replace(url);
    }, 350);
}
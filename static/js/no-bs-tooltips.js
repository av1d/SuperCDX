// no BS tooltips
// https://gist.github.com/av1d/b64632c33ccf8c673b14b6cf164a93cb

function displayQuote(event, url) {
    var quoteElement = document.getElementById("no-BS-tooltips");
    quoteElement.textContent = url;

    quoteElement.style.position = "fixed";
    quoteElement.style.left = event.clientX + "px";
    quoteElement.style.top = event.clientY + "px";
    quoteElement.style.backgroundColor = "#fff";
    quoteElement.style.border = "1px solid #ccc";
    quoteElement.style.padding = "5px 10px";
    quoteElement.style.borderRadius = "3px";
    quoteElement.style.zIndex = "10000";
    quoteElement.style.fontSize = "14px";
    quoteElement.style.boxShadow = "0 2px 5px rgba(0,0,0,0.2)";
}

function eraseQuote() {
    document.getElementById("no-BS-tooltips").textContent = "";
}

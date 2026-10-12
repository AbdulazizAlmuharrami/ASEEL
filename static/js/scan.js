(function () {
  var reader = document.getElementById("qr-reader");
  var status = document.getElementById("scan-status");
  if (!reader || typeof Html5Qrcode === "undefined") {
    if (status) status.textContent = "Camera scanning is unavailable in this browser. Enter the code instead.";
    return;
  }

  var scanner = new Html5Qrcode("qr-reader");

  function onSuccess(decodedText) {
    scanner.stop().catch(function () {});
    if (status) status.textContent = "Code found. Opening authentication record…";
    try {
      var url = new URL(decodedText);
      window.location.href = url.pathname + url.search;
      return;
    } catch (error) {
      window.location.href = "/verify/" + encodeURIComponent(decodedText.trim());
    }
  }

  Html5Qrcode.getCameras()
    .then(function (cameras) {
      if (!cameras.length) {
        status.textContent = "No camera found. Enter the unique code instead.";
        return;
      }
      status.textContent = "Hold the Smart QR Tag inside the frame.";
      return scanner.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 220, height: 220 } },
        onSuccess
      );
    })
    .catch(function () {
      status.textContent = "Camera permission was blocked. You can still type the unique code.";
    });
})();

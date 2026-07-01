/* Compresión de fotos en el navegador antes de subir.
   Reduce el lado mayor a 1600px y recodifica a JPEG (~0.72) para ahorrar datos
   y tiempo de subida desde el celular. Si algo falla, sube el archivo original;
   el servidor igual recomprime como garantía. */
(function () {
  var form = document.querySelector("form[enctype='multipart/form-data']");
  if (!form) return;
  var input = form.querySelector("input[type=file][name=fotos]");
  if (!input || typeof createImageBitmap === "undefined") return;

  var MAX = 1600, CALIDAD = 0.72;

  function comprimirUna(file) {
    if (!file.type || file.type.indexOf("image/") !== 0) return Promise.resolve(file);
    return createImageBitmap(file, { imageOrientation: "from-image" })
      .then(function (bmp) {
        var escala = Math.min(1, MAX / Math.max(bmp.width, bmp.height));
        var w = Math.round(bmp.width * escala), h = Math.round(bmp.height * escala);
        var canvas = document.createElement("canvas");
        canvas.width = w; canvas.height = h;
        canvas.getContext("2d").drawImage(bmp, 0, 0, w, h);
        return new Promise(function (res) {
          canvas.toBlob(function (blob) {
            if (!blob) { res(file); return; }
            var nombre = file.name.replace(/\.\w+$/, "") + ".jpg";
            res(new File([blob], nombre, { type: "image/jpeg" }));
          }, "image/jpeg", CALIDAD);
        });
      })
      .catch(function () { return file; });
  }

  function enviarCon(accion) {
    var oculto = document.createElement("input");
    oculto.type = "hidden"; oculto.name = "accion"; oculto.value = accion;
    form.appendChild(oculto);
    Promise.all(Array.prototype.map.call(input.files, comprimirUna))
      .then(function (files) {
        try {
          var dt = new DataTransfer();
          files.forEach(function (f) { dt.items.add(f); });
          input.files = dt.files;
        } catch (e) { /* si el navegador no permite, sube lo original */ }
        form.submit();
      })
      .catch(function () { form.submit(); });
  }

  form.querySelectorAll(".verdict").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      // Sin fotos seleccionadas: envío normal (el botón ya manda 'accion').
      if (!input.files || !input.files.length) return;
      e.preventDefault();
      enviarCon(btn.value);
    });
  });
})();

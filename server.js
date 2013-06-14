var app = require('http').createServer(handler)
   , io = require('socket.io').listen(app)
   , fs = require('fs');

app.listen(4949);

function end(res) {
  res.writeHead(200);
  res.end("");
}

function writeError(res) {
  res.writeHead(500);
  res.end("");
}

var clients = {};
function handler (req, res) {
  // console.log("Request with " + req.method + " for " + req.url);

  if (req.method === "GET") {
    console.log("Ignoring GET request");
    return end(res);
  } else {
    var splat = req.url.split("/");
    if (splat.length === 3) {
      var device = splat[1]
        , action = splat[2];

      var client = clients[device];
      // Pretty sure this has security implications
      // Maaaybe a typecheck will let me get away with it
      if (client !== undefined) // && (typeof client === "io.socket")
      {
        // More dealing with malicious input
        if (action === "next") {
          client.next();
        } else if (action === "prev") {
          client.prev();
        } else if (action === "toggle") {
          client.toggle();
        }
      }
    }
    return writeError(res);
  }
}

io.sockets.on('connection', function (socket) {
  for (var k in socket) {
    console.log(k);
  }
});

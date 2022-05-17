function onDrop(source, target, piece, orientation) {
  var pn = piece.includes('b')
    ? piece.toUpperCase().substring(1, 2)
    : piece.substring(1, 2);
  pn = piece.includes('P') ? '' : pn;
  var move = piece.includes('P')
    ? source + target
    : pn + source.substring(0, 1) + target;
  move =
    piece.includes('P') && target.includes('8')
      ? target.substring(0, 1) + '8Q'
      : move; // pawn promotion

  $.get('/move', {move: move}, function(data) {
    console.log(data);
    if (data.game_over !== 'true') {

      board.position(data.fen);
      $(".card-body#game-moves").scrollTop($(".card-body#game-moves")[0].scrollHeight);
    } else {
        document.querySelectorAll(".game-over")[1].innerText = "Game lost";
    }
  });
}

// to fix player with white/black peices from messing arround with other player's pieces.
// can be bypassed tho., that's why its also validated in back-end too.
function onDragStart(source, piece, position, orientation) {
  if (
    (orientation === 'white' && piece.search(/^w/) === -1) ||
    (orientation === 'black' && piece.search(/^b/) === -1)
  ) {
    return false;
  }
}

$('#reset').click(function() {
  $.get('/reset', function(data) {
    board.position(data.fen);
    document.querySelector('#pgn').innerText = data.pgn;
  });
});

$('#undo').click(function() {
  if (!$(this).hasClass('text-muted')) {
    $.get('/undo', function(data) {
      board.position(data.fen);
      document.querySelector('#pgn').innerText = data.pgn;
    });
  } else {
    //
  }
});

$('#redo').click(function() {
  if (!$(this).hasClass('text-muted')) {
    $.get('/redo', function(data) {
      board.position(data.fen);
      document.querySelector('#pgn').innerText = data.pgn;
    });
  } else {
    //
  }
});

var cfg = {
    position: '8/8/8/8/8/8/8/8',
    showNotation: true,
    draggable: true,
    // onDragStart: onDragStart,
    // onDrop: onDrop,
    // onMouseoutSquare: onMouseoutSquare,
    // onMouseoverSquare: onMouseoverSquare
};
var board = ChessBoard('board', cfg);

$("#btn_camera").click( function() {

    console.log('Camera clicked');

    $.get('/detect_cam_fen', function(fen) {
        board.position(fen)
    })

})


var ai_color = $('input[name="ai_colour"]:checked').val()
ai_color = ai_color=='black' ? true : false
$('input[name="ai_colour"]').on('change', function () {
    ai_color = $('input[name="ai_colour"]:checked').val()
    ai_color = ai_color=='ai_black' ? true : false
})
$("#btn_startAI").click( function() {
    console.log('AI clicked');
    
    let fen = board.fen()

    $.get('/detect_ai_fen', {
        fen: fen,
        ai_color: ai_color
    }, function(fen) {
        board.position(fen)
    })
    
})
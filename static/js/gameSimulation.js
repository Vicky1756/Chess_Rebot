var human_time=false, ai_time=false
var human_timeleft=0, ai_timeleft=0

function forceMoveAI(firstTurn=true) {

    let move

    human_time = false
    // human_timeleft = 0
    ai_time = true
    ai_timeleft = 120

    if(firstTurn) {
        move = 'computer first'
        // console.log(move);
        
        $.get('/move', {move: move}, function(data) {
            // console.log(data);
    
            human_time = true
            human_timeleft = data.human_time
            ai_time = false
            // ai_timeleft = 0
            
            if (data.game_over !== 'true') {
                board.position(data.fen);
            } else {
                board.position(data.fen);

                
                // $(".game-over").text("Checkmate !!!");
                alert("Checkmate !!!");
            }
        })
    }
    else {
        // move = 'd5d4'

        console.log(move_ai);
        let play = (move_ai) ? 'black':'white'
        $("#player_turn").val(play)
        
        let board_fen = board.fen()
        $("#player_board").val(board_fen)
        
        // let play_ai = 'true'
        // $("#force_board").val(play_ai)

        $("#start_game_link")[0].click()
    }

}

function onDrop(source, target, piece, orientation) {
    var pn = piece.includes('b') ? piece.toUpperCase().substring(1, 2) : piece.substring(1, 2); 
    pn = piece.includes('P') ? '' : pn;
    var move = piece.includes('P') ? source + target : pn + source.substring(0, 1) + target;
    move = piece.includes('P') && target.includes('8') ? target.substring(0, 1) + '8Q' : move; // pawn promotion
    

    // removeGreySquares();

    // console.log(source);
    // console.log(target);
    // console.log(piece);
    // console.log(orientation);
    console.log(move);

    human_time = false
    // human_timeleft = 0
    ai_time = true
    ai_timeleft = 120

    $.get('/move', {move: move}, function(data) {
        console.log(data);
        // console.log(data.game_over != 'true');

        if (data.game_over != 'true') {

            human_time = true
            human_timeleft = data.human_time
            ai_time = false
            // ai_timeleft = 0

            board.position(data.fen);
        } else {
            // console.log('Game lost');
            // $(".game-over").text("Checkmate !!!");


            human_timeleft = 0
            ai_timeleft = 0
            
            board.position(data.fen);

            
            alert("Checkmate !!!");

        }
    });
}

// Game.prototype.castleRook = function(rookName){
// 	var rook = this.getPieceByName(rookName);
// 	if (rookName.indexOf('Rook2') != -1) 
// 		var newPosition = rook.position - 2;
// 	else
// 		var newPosition = rook.position + 2;

// 	this.setClickedPiece(rook);
// 	var chosenSquare = document.getElementById(newPosition);
// 	chosenSquare.classList.add('allowed');
// 	this.movePiece('', chosenSquare );
// 	this.changeTurn();
// }


// to fix player with white/black peices from messing arround with other player's pieces.
// can be bypassed tho., that's why its also validated in back-end too.
function onDragStart(source, piece, position, orientation) {
    if ( (orientation === 'white' && piece.search(/^w/) === -1) || (orientation === 'black' && piece.search(/^b/) === -1) ) {
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



// function onMouseoutSquare(square, piece) {
//     removeGreySquares();
// };

// function onMouseoverSquare(square, piece) {
//     let moves = board.moves({
//         square: square,
//         verbose: true
//     });

//     if (moves.length === 0) return;

//     greySquare(square);

//     for (var i = 0; i < moves.length; i++) {
//         greySquare(moves[i].to);
//     }
// };

// function removeGreySquares() {
//     $('#board .square-55d63').css('background', '');
// };

// function greySquare(square) {
//     let squareEl = $('#board .square-' + square);

//     let background = '#a9a9a9';
//     if (squareEl.hasClass('black-3c85d') === true) {
//         background = '#696969';
//     }

//     squareEl.css('background', background);
// };
    
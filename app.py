#!/usr/bin/env python3


# coding : utf-8

from cmath import log
from flask import Flask, Response, request, render_template, url_for, redirect
import chess, chess.pgn
import chess.engine
import traceback
import time
import collections
import json
from gevent.pywsgi import WSGIServer
import main
import ai
import test_bog2
from random import choice
import cv2
from camera import VideoCamera
from flask_socketio import SocketIO
import time
from test import BoardCamera



class Player(object):
    def __init__(self, board, game_time=120):
        self.__current_board = board

    def make_move(self, move):
        raise NotImplementedError()

class Player1(Player):
    def __init__(self, board, game_time=120):
        self.__current_board = board
        self.__game_time = game_time
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None
        self.__now_turn = True

    def get_board(self):
        return self.__current_board

    def set_board(self, board):
        self.__current_board = board

    def make_move(self, move):
        if self.__current_board.turn == self.__now_turn:
            if self.__first_move_timestamp is not None:
                self.__first_move_timestamp = int(time.time())
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's Blacks Turn (Player2)***")

        return self.__current_board

    def undo_last_move(self):
        self.__current_board.pop()
        return self.__current_board

    def is_turn(self):
        return self.__current_board.turn == self.__now_turn
    
    def set_turn(self, turn=True):
        self.__now_turn = turn
        return self.__now_turn


    def get_game_time(self):
        return self.__game_time

    def get_time_left(self):
        return self.__time_left

    def reset(self):
        self.__current_board = None
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None


class Player2(Player):
    def __init__(self, board, game_time=120):
        self.__current_board = board
        self.__game_time = game_time
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None
        self.__now_turn = False

    def get_board(self):
        return self.__current_board

    def set_board(self, board):
        self.__current_board = board

    def make_move(self, move):
        if self.__current_board.turn == self.__now_turn:
            if self.__first_move_timestamp is not None:
                self.__first_move_timestamp = int(time.time())
            try:
                self.__current_board.push_san(move)
            except ValueError:
                print('Not a legal move')
        else:
            print("Error: ****It's White's Turn (Player1)***")

        return self.__current_board

    def undo_last_move(self):
        self.__current_board.pop()
        return self.__current_board

    def is_turn(self):
        return self.__current_board.turn == self.__now_turn
    
    def set_turn(self, turn=False):
        self.__now_turn = turn
        return self.__now_turn

    def get_game_time(self):
        return self.__game_time

    def get_time_left(self):
        return self.__time_left

    def reset(self):
        self.__current_board = None
        self.__time_left = self.__game_time
        self.__first_move_timestamp = None


    def engine_move(self):

        # ToDo is_player_white
        is_player_white = not self.__now_turn
        ai.AI(self.__current_board, is_player_white).ai_move()

        return self.__current_board


def board_to_game(board):
    game = chess.pgn.Game()

    # undo all moves
    switchyard = collections.deque()
    while board.move_stack:
        switchyard.append(board.pop())

    game.setup(board)
    node = game

    # Replay all moves
    while switchyard:
        move = switchyard.pop()
        node = node.add_variation(move)
        board.push(move)

    game.headers["Result"] = board.result()
    return game


def console_demo():
    global board
    board = chess.Board()
    p1 = Player1(board)
    p2 = Player2(board)
    print(board)
    print("------------------------------------------")

    while True:
        move_san = input('White move: ').strip()
        board = p1.make_move(move_san)
        print(board)
        print('-'*50)
        move_san = input('Black to move: ').strip()
        board = p2.make_move(move_san)
        print(board)
        print("-"*50)


app = Flask(__name__, static_url_path='')
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
# # camera open
# vid = cv2.VideoCapture(0)
@app.route('/', methods=['GET'])
def init():
    return redirect("/home")
    # return redirect(url_for("simulation", play=False))

@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', config='[0,0,0,0]', taskspace='[0,0,0,0]' )

def gen(camera):
    while True:
        #get camera frame
        (frame, status) = camera.get_frame()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if not status:
            break
        # time.sleep(1)

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

    
@app.route('/get_cam_fen', methods=['GET'])
def get_cam_fen(new_fen):
    if main:
        frame = main.new_fen
        resp = {
            'frame': frame
        }
        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        return False

@app.route('/detect_cam_fen', methods=['GET'])
def detect_cam_fen():
    fen = BoardCamera('white').main()

    # fen = test_bog2.bog()
    print( fen )
    return fen

@app.route('/detect_ai_fen', methods=['GET'])
def detect_ai_fen():

    old_fen = request.args.get('fen', default='')
    old_board = chess.Board(old_fen)
    
    ai_color = request.args.get('ai_color')
    ai_color = ai_color=='true' if True else False
    
    old_board.turn = not ai_color

    # old_board.turn = not old_board.turn
    self_ai = ai.AI(old_board, ai_color)
    self_ai.ai_move()
    
    fen = self_ai.board.fen()

    print( fen )
    return fen

@app.route('/settings', methods=['GET'])
def settings():
    # VideoCamera().__del__()
    return render_template('settings.html')

@app.route('/start_game', methods=['GET'])
def start_game():
    global board, Human, engine
    global undo_moves_stack

    player_side = request.args.get('turn', default='')
    player_board = request.args.get('board', default='')
    force_play = request.args.get('force', default='false')


    turn = False
    if player_side=='white':
        turn = False
    elif player_side=='black':
        turn = True
    else:
        turn = choice([True, False])

    
    if force_play != 'false':
        board.turn = not board.turn

    Human.reset()
    engine.reset()
    board = chess.Board(player_board)
    Human.set_board(board)
    engine.set_board(board)

    if not turn :
        Human.set_turn(True)
        engine.set_turn(False)
    else:
        Human.set_turn(False)
        engine.set_turn(True)

    return redirect(url_for("simulation", play=turn))


def run_game():
    global board, Human, engine
    global undo_moves_stack
    undo_moves_stack = []
    board = chess.Board()
    Human  = Player1(board)
    engine = Player2(board)

    @app.route('/simulation', methods=['GET'])
    def simulation():
        move_ai = request.args.get('play', default=False)
        global board
        return render_template('gameSimulation.html', fen=board.board_fen(), pgn=str(board_to_game(board).mainline_moves()), move_ai=move_ai)


    @app.route('/move', methods=['GET'])
    def move():
        global board
        global undo_moves_stack

        # print( board.outcome() )

        if not board.is_game_over():
            move_san = request.args.get('move', default='')
            if move_san is not None and move_san != '':
                try:
                    if Human.is_turn():
                        print("White's turn to play:")
                    else:
                        print("Black's turn to play")
                    if Human.is_turn():
                        board = Human.make_move(str(move_san))
                        undo_moves_stack = [] #make undo moves stack empty if any move is done.
                        if engine.is_turn():
                            board = engine.engine_move()
                    else:
                        board = engine.engine_move()
                    print(board)
                except Exception:
                    traceback.print_exc()
                game_moves_san = [move_uci.san() for move_uci in board_to_game(board).mainline()]
                print(game_moves_san)
                if board.is_game_over():
                    resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'true', 'human_time': Human.get_time_left(), 'ai_time': engine.get_time_left() }
                else:
                    resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'false', 'human_time': Human.get_time_left(), 'ai_time': engine.get_time_left() }
                response = app.response_class(
                    response=json.dumps(resp),
                    status=200,
                    mimetype='application/json'
                )
                return response
        else:
            game_moves_san = [move_uci.san() for move_uci in board_to_game(board).mainline()]
            print(game_moves_san)
            resp = {'fen': board.board_fen(), 'moves': game_moves_san, 'game_over': 'true', 'human_time': 0, 'ai_time': 0 }
            response = app.response_class(
                response=json.dumps(resp),
                status=200,
                mimetype='application/json'
            )
            return response
        return index()

    @app.route("/reset", methods=["GET"])
    def reset():
        global board
        Human.reset()
        engine.reset()
        board = chess.Board()
        Human.set_board(board)
        engine.set_board(board)

        resp = {"fen": board.board_fen(), 'pgn': str(board_to_game(board).mainline_moves())}
        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )

        return response


    @app.route("/undo", methods=["GET"])
    def undo():
        global board
        global undo_moves_stack
        try:
            undo_moves_stack.append(board.pop())
        except IndexError:
            print("fuck")

        resp = {'fen': board.board_fen(), 'pgn': str(board_to_game(board).mainline_moves())}
        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )
        return response


    @app.route("/redo", methods=["GET"])
    def redo():
        global board
        global undo_moves_stack
        if len(undo_moves_stack) != 0:
            board.push(undo_moves_stack.pop())
        else:
            pass

        resp = {'fen': board.board_fen(), 'pgn': str(board_to_game(board).mainline_moves())}

        response = app.response_class(
            response=json.dumps(resp),
            status=200,
            mimetype='application/json'
        )

        return response


    # http_server = WSGIServer(('0.0.0.0', 1337), app)
    # http_server.serve_forever()

    #app.run(host='127.0.0.1', debug=True)


if __name__ == "__main__":
    #console_demo()
    run_game()


    count = 1
    board = chess.Board()
    
    print("Starting server on http://127.0.0.1:1337/")
    http_server = WSGIServer(('0.0.0.0', 1337), app)
    http_server.serve_forever()
    app.run(host='127.0.0.1', debug=True)
    # socketio.run(app)



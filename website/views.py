from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/todolist', methods=['GET', 'POST'])
@login_required
def todolist():
    if request.method == 'POST': 
        note = request.form.get('note')
        difficulty = request.form.get('difficulty')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            if difficulty:  # If difficulty is provided
                new_note = Note(data=note, user_id=current_user.id, difficulty=difficulty)
            else:
                new_note = Note(data=note, user_id=current_user.id)

            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("todolist.html", user=current_user)



def update_level(user):
    global INITIAL_XP_THRESHOLD  # Declare the variable as global

    next_xp_threshold = INITIAL_XP_THRESHOLD 
    
    if user.xp >= next_xp_threshold:
        user.level += 1
        pre_xp_threshold = INITIAL_XP_THRESHOLD
        INITIAL_XP_THRESHOLD += 50
        db.session.add(user)
        db.session.commit()
        return True
    
    return False


DIFFICULTY_XP_MULTIPLIER = {
    'easy': 1,
    'medium': 1.5,
    'hard': 2
}
def check_level(user,initial_xp_threshold):
    
    next_xp_threshold = initial_xp_threshold
    pre_xp_threshold = initial_xp_threshold
    
    if user.xp >= next_xp_threshold:
        
        user.level += 1
        db.session.add(user)
        db.session.commit()
    elif user.xp < pre_xp_threshold:
        user.level -=1
        db.session.add(user)
        db.session.commit()


# Update the update_xp function to pass the initial XP threshold
@views.route('/update-xp', methods=['POST'])
def update_xp():
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note and note.user_id == current_user.id:
        difficulty = note.difficulty.lower()
        multiplier = DIFFICULTY_XP_MULTIPLIER.get(difficulty, 1)  
        xp_reward = 10 * multiplier
        current_user.xp += xp_reward
        initial_xp_threshold = 50*current_user.level
        check_level(current_user,initial_xp_threshold)
        db.session.delete(note)
        db.session.commit()
    return jsonify({})


# Update the delete_note function to reduce XP and check for level down
@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            current_user.xp -= 10
            initial_xp_threshold = 50*current_user.level
            check_level(current_user,initial_xp_threshold)
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
    


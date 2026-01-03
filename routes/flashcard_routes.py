"""Flashcard routes blueprint"""
import os
import json
from flask import Blueprint, request, jsonify

bp = Blueprint('flashcard', __name__, url_prefix='/flashcard')

# Flashcard state variables
current_deck = []
current_card_index = 0
current_side = 'front'  # 'front' or 'back'
deck_name = None
deck_metadata = None


@bp.route('/2', methods=['GET'])
def flashcard2():
    global current_deck, current_card_index, current_side, deck_name, deck_metadata
    
    command = request.args.get('command')
    
    if not command:
        return jsonify({'error': 'Missing command parameter'}), 400
    
    try:
        if command == 'load':
            name = request.args.get('name')
            if not name:
                return jsonify({'error': 'Missing name parameter for load command'}), 400
            
            deck_path = f'/var/www/html/mp3/{name}.json'
            if not os.path.exists(deck_path):
                return jsonify({'error': f'Deck "{name}" not found'}), 404
            
            with open(deck_path, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)
            
            # Extract cards array from the new format
            if 'cards' not in deck_data:
                return jsonify({'error': 'Invalid deck format: missing "cards" array'}), 400
                
            current_deck = deck_data['cards']
            deck_metadata = {
                'name': deck_data.get('name', name),
                'created': deck_data.get('created', ''),
                'card_count': deck_data.get('card_count', len(current_deck))
            }
            
            current_card_index = 0
            current_side = 'front'
            deck_name = name
            
            return jsonify({
                'result': 'success',
                'message': f'Deck "{deck_metadata["name"]}" loaded with {len(current_deck)} cards',
                'deck_info': deck_metadata
            })
        
        elif command == 'play':
            if not current_deck:
                return jsonify({'error': 'No deck loaded'}), 400
            
            if current_card_index >= len(current_deck):
                return jsonify({'error': 'No more cards in deck'}), 400
            
            current_card = current_deck[current_card_index]
            url = current_card[current_side]
            
            return jsonify({
                'url': url,
                'side': current_side,
                'card_index': current_card_index,
                'total_cards': len(current_deck)
            })
        
        elif command == 'flip':
            if not current_deck:
                return jsonify({'error': 'No deck loaded'}), 400
            
            if current_card_index >= len(current_deck):
                return jsonify({'error': 'No more cards in deck'}), 400
            
            current_side = 'back' if current_side == 'front' else 'front'
            
            return jsonify({
                'result': 'success',
                'side': current_side,
                'message': f'Card flipped to {current_side} side'
            })
        
        elif command == 'return':
            if not current_deck:
                return jsonify({'error': 'No deck loaded'}), 400
            
            if current_card_index >= len(current_deck):
                return jsonify({'error': 'No more cards in deck'}), 400
            
            # Move current card to the end of the deck
            card_to_move = current_deck.pop(current_card_index)
            current_deck.append(card_to_move)
            current_side = 'front'  # Reset to front side
            
            # Don't increment index since we removed the current card
            if current_card_index >= len(current_deck):
                current_card_index = 0
            
            return jsonify({
                'result': 'success',
                'message': 'Card moved to back of deck',
                'cards_remaining': len(current_deck)
            })
        
        elif command == 'remove':
            if not current_deck:
                return jsonify({'error': 'No deck loaded'}), 400
            
            if current_card_index >= len(current_deck):
                return jsonify({'error': 'No more cards in deck'}), 400
            
            # Remove current card from deck
            removed_card = current_deck.pop(current_card_index)
            current_side = 'front'  # Reset to front side
            
            # Adjust index if we're at the end
            if current_card_index >= len(current_deck) and len(current_deck) > 0:
                current_card_index = 0
            
            return jsonify({
                'result': 'success',
                'message': 'Card removed from deck',
                'cards_remaining': len(current_deck),
                'removed_card': removed_card
            })
        
        else:
            return jsonify({'error': f'Unknown command: {command}'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500
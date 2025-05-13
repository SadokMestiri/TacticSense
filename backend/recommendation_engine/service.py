# filepath: c:\Users\Nassi\Desktop\education\ESPRIT\4eme\S2\PI\Platform\TacticSense\backend\recommendation_engine\service.py
import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

recommendation_models = None
# Adjust the path to go up one level from 'recommendation_engine' to 'backend', then into 'models'
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'recommendation_models.pkl')

def load_models_from_pickle():
    global recommendation_models
    try:
        if not os.path.exists(MODEL_PATH):
            app.logger.error(f"Model file not found at {MODEL_PATH}")
            recommendation_models = None
            return
        with open(MODEL_PATH, 'rb') as f:
            recommendation_models = pickle.load(f)
            app.logger.info(f"Recommendation models loaded successfully in service from {MODEL_PATH}.")
            # You might want to validate the loaded models/keys here as well
            required_model_keys = [
                'club_model', 'player_model', 'agents_model', 'staff_model', # Core models
                'agency_id_map_club', 'club_id_map', 'id_to_club', 'club_id_to_name', # For clubs/agency
                'agency_id_map_player', 'player_id_map', 'id_to_player', 'player_id_to_name', # For players/agency
                'id_to_agency_player', 'agency_id_to_name', # For agencies/player
                'transfer_df', # For clubs/player & players/club
                'id_to_agency_club', # For agencies/club
                'id_to_agency_agent', 'agents_to_name', 'agent_id_map_agency', # For agents/agency
                'id_to_agent_agency', # For agencies/agent
                'user_id_map_s', 'id_to_item_s', 'id_to_user_s', 'staff_name_map', 'item_id_map_s' # For staff/club
            ]
            missing_keys = [key for key in required_model_keys if key not in recommendation_models]
            if missing_keys:
                app.logger.error(f"Missing required keys in loaded models: {missing_keys}")
                recommendation_models = None # Invalidate if essential parts are missing

    except Exception as e:
        app.logger.error(f"Error loading recommendation models in service: {str(e)}")
        recommendation_models = None

def score_to_stars(score, max_stars=5):
    score = float(score) # Ensure score is float
    score = max(0, min(score, 1)) # Normalize if scores are 0-1, adjust if they are raw scores
    stars_val = round(score * max_stars)
    return '★' * int(stars_val) + '☆' * int(max_stars - stars_val)

@app.route('/recommend', methods=['POST'])
def get_recommendations_from_service():
    if recommendation_models is None:
        load_models_from_pickle() # Attempt to reload if None
        if recommendation_models is None:
            return jsonify({'error': 'Recommendation system not ready or models failed to load in service'}), 503

    data = request.json
    recommendation_type = data.get('type')
    user_info = data.get('user_info') # Expected: {'id': '...', 'role': '...', 'name': '...'}
    top_n = int(data.get('top_n', 5))

    if not recommendation_type or not user_info:
        return jsonify({'error': 'Missing recommendation_type or user_info in service request'}), 400

    current_user_id_str = str(user_info.get('id'))
    current_user_role = user_info.get('role')
    current_user_name = user_info.get('name', '').strip().lower() # Use for name-based lookups

    recommendations = []
    try:
        # CLUBS TO AGENCY
        if recommendation_type == 'clubs_to_agency':
            if current_user_role != 'Agency': return jsonify({'message': 'User is not an Agency'}), 200
            model = recommendation_models['club_model']
            agency_idx = recommendation_models['agency_id_map_club'].get(current_user_id_str)
            if agency_idx is None: return jsonify([])
            scores = model.predict(agency_idx, np.arange(len(recommendation_models['club_id_map'])))
            for idx in np.argsort(-scores)[:top_n]:
                club_id = recommendation_models['id_to_club'][idx]
                recommendations.append({
                    'club': recommendation_models['club_id_to_name'].get(club_id, "Unknown Club"),
                    'score': float(scores[idx]), 'club_id': club_id,
                    'recommended_stars': score_to_stars(scores[idx])})

        # PLAYERS TO AGENCY
        elif recommendation_type == 'players_to_agency':
            if current_user_role != 'Agency': return jsonify({'message': 'User is not an Agency'}), 200
            model = recommendation_models['player_model']
            agency_idx = recommendation_models['agency_id_map_player'].get(current_user_id_str)
            if agency_idx is None: return jsonify([])
            scores = model.predict(agency_idx, np.arange(len(recommendation_models['player_id_map'])))
            for idx in np.argsort(-scores)[:top_n]:
                player_id = recommendation_models['id_to_player'][idx]
                recommendations.append({
                    'player': recommendation_models['player_id_to_name'].get(player_id, "Unknown Player"),
                    'score': float(scores[idx]), 'player_id': player_id,
                    'recommended_stars': score_to_stars(scores[idx])})

        # AGENCIES TO PLAYER
        elif recommendation_type == 'agencies_to_player':
            if current_user_role != 'Player': return jsonify({'message': 'User is not a Player'}), 200
            model = recommendation_models['player_model']
            player_idx = recommendation_models['player_id_map'].get(current_user_id_str)
            if player_idx is None: return jsonify([])
            scores = model.predict(user_ids=np.arange(len(recommendation_models['agency_id_map_player'])),
                                   item_ids=np.repeat(player_idx, len(recommendation_models['agency_id_map_player'])))
            for idx in np.argsort(-scores):
                if len(recommendations) >= top_n: break
                agency_id = recommendation_models['id_to_agency_player'][idx]
                agency_name = recommendation_models['agency_id_to_name'].get(agency_id, agency_id)
                if pd.isna(agency_name): continue
                recommendations.append({
                    'agency': str(agency_name), 'score': float(scores[idx]),
                    'agency_id': agency_id, 'recommended_stars': score_to_stars(scores[idx])})

        # CLUBS TO PLAYER
        elif recommendation_type == 'clubs_to_player':
            if current_user_role != 'Player': return jsonify({'message': 'User is not a Player'}), 200
            player_agencies = set(recommendation_models['transfer_df'][recommendation_models['transfer_df']['Player Id'].astype(str) == current_user_id_str]['Agency Id'].astype(str).unique())
            if not player_agencies: return jsonify([])
            all_scores = np.zeros(len(recommendation_models['club_id_map']))
            valid_agencies = 0
            for agency_id in player_agencies:
                agency_idx = recommendation_models['agency_id_map_club'].get(agency_id)
                if agency_idx is not None:
                    all_scores += recommendation_models['club_model'].predict(agency_idx, np.arange(len(recommendation_models['club_id_map'])))
                    valid_agencies += 1
            if valid_agencies == 0: return jsonify({'message': 'No valid agency mappings'}), 200
            all_scores /= valid_agencies
            for idx in np.argsort(-all_scores)[:top_n]: # Original code had fixed top_n=3 here
                club_id = recommendation_models['id_to_club'].get(idx)
                club_name = recommendation_models['club_id_to_name'].get(club_id, f"Club_{club_id}")
                if pd.isna(club_name): continue
                recommendations.append({
                    'club': str(club_name), 'score': float(all_scores[idx]),
                    'club_id': str(club_id), 'recommended_stars': score_to_stars(all_scores[idx])})

        # PLAYERS TO CLUB
        elif recommendation_type == 'players_to_club':
            if current_user_role != 'Club': return jsonify({'message': 'User is not a Club'}), 200
            club_norm = current_user_id_str # Assuming club ID is passed as user_info.id
            if club_norm not in recommendation_models['club_id_map']: return jsonify({'message': 'Club not in map'}), 200
            # club_idx = recommendation_models['club_id_map'][club_norm] # Not directly used in this logic path
            club_agencies = set(recommendation_models['transfer_df'][recommendation_models['transfer_df']['Club_norm'] == club_norm]['Agency_norm'])
            if not club_agencies: return jsonify([])
            num_players = len(recommendation_models['player_id_map'])
            all_scores = np.zeros(num_players)
            valid_agency_count = 0
            for agency_norm in club_agencies:
                agency_idx = recommendation_models['agency_id_map_player'].get(agency_norm)
                if agency_idx is not None:
                    all_scores += recommendation_models['player_model'].predict(agency_idx, np.arange(num_players))
                    valid_agency_count += 1
            if valid_agency_count == 0: return jsonify({'message': 'No valid player mappings'}), 200
            all_scores /= valid_agency_count
            if np.all(all_scores < 0): all_scores += 2 # Adjustment from original
            for idx in np.argsort(-all_scores)[:top_n]:
                player_id = recommendation_models['id_to_player'].get(idx)
                player_name = recommendation_models['player_id_to_name'].get(player_id, f"Player {player_id}")
                recommendations.append({
                    'player_id': player_id, 'player': player_name, 'score': float(all_scores[idx]),
                    'recommended_stars': score_to_stars(all_scores[idx])})
            return jsonify({'success': True, 'club_id': current_user_id_str, 'recommendations': recommendations}) # Special structure

        # AGENCIES TO CLUB
        elif recommendation_type == 'agencies_to_club':
            if current_user_role != 'Club': return jsonify({'message': 'User is not a Club'}), 200
            club_idx = recommendation_models['club_id_map'].get(current_user_id_str)
            if club_idx is None: return jsonify([])
            scores = recommendation_models['club_model'].predict(user_ids=np.arange(len(recommendation_models['agency_id_map_club'])),
                                                                item_ids=np.repeat(club_idx, len(recommendation_models['agency_id_map_club'])))
            for idx in np.argsort(-scores):
                if len(recommendations) >= top_n: break
                agency_id = recommendation_models['id_to_agency_club'][idx]
                agency_name = recommendation_models['agency_id_to_name'].get(agency_id, agency_id)
                if pd.isna(agency_name): continue
                recommendations.append({
                    'agency': str(agency_name), 'score': float(scores[idx]),
                    'agency_id': agency_id, 'recommended_stars': score_to_stars(scores[idx])})

        # AGENTS TO AGENCY (Agency is current_user, looking for Agents)
        elif recommendation_type == 'agents_to_agency':
            if current_user_role != 'Agency': return jsonify({'message': 'User is not an Agency'}), 200
            model = recommendation_models['agents_model']
            # This route implies an Agency (current_user) wants recommendations for Agents.
            # The original logic was confusing. A more logical approach:
            # Agency is the "item" context; we predict scores for all "user" agents.
            # Requires mappings: agency_name -> item_idx for agents_model, user_idx -> agent_id
            agency_name_for_model = current_user_name # Agency's name
            agency_item_idx = recommendation_models.get('agency_name_to_item_idx_for_agents_model', {}).get(agency_name_for_model)
            id_to_agent_user = recommendation_models.get('id_to_agent_user_for_agents_model', {}) # user_idx -> agent_id
            agent_id_to_name_map = recommendation_models.get('agent_id_to_name', {}) # agent_id -> agent_name

            if agency_item_idx is None: return jsonify([])
            
            num_agents_in_model = len(id_to_agent_user)
            if num_agents_in_model == 0: return jsonify([])

            scores = model.predict(
                user_ids=np.arange(num_agents_in_model), # All agent user_indices
                item_ids=np.repeat(agency_item_idx, num_agents_in_model) # Current agency item_index
            )
            for agent_user_idx in np.argsort(-scores):
                if len(recommendations) >= top_n: break
                agent_id = id_to_agent_user.get(agent_user_idx)
                if agent_id is None: continue
                agent_name_rec = agent_id_to_name_map.get(agent_id)
                if agent_name_rec is None or pd.isna(agent_name_rec): continue
                recommendations.append({
                    'agent': str(agent_name_rec), 'score': float(scores[agent_user_idx]),
                    'agent_id': str(agent_id), 'recommended_stars': score_to_stars(scores[agent_user_idx])})

        # AGENCIES TO AGENT (Agent is current_user, looking for Agencies)
        elif recommendation_type == 'agencies_to_agent':
            if current_user_role != 'Agent': return jsonify({'message': 'User is not an Agent'}), 200
            model = recommendation_models['agents_model']
            # Agent is "user" context; we predict scores for all "item" agencies.
            # Requires mappings: agent_name -> user_idx for agents_model, item_idx -> agency_id
            agent_name_for_model = current_user_name # Agent's name
            agent_user_idx = recommendation_models.get('agent_name_to_user_idx_for_agents_model', {}).get(agent_name_for_model)
            id_to_agency_item = recommendation_models.get('id_to_agency_item_for_agents_model', {}) # item_idx -> agency_id
            agency_id_to_name_map = recommendation_models.get('agency_id_to_name', {}) # agency_id -> agency_name

            if agent_user_idx is None: return jsonify([])
            
            num_agencies_in_model = len(id_to_agency_item)
            if num_agencies_in_model == 0: return jsonify([])

            scores = model.predict(
                user_ids=np.repeat(agent_user_idx, num_agencies_in_model), # Current agent user_idx
                item_ids=np.arange(num_agencies_in_model) # All agency item_indices
            )
            for agency_item_idx in np.argsort(-scores):
                if len(recommendations) >= top_n: break
                agency_id = id_to_agency_item.get(agency_item_idx)
                if agency_id is None: continue
                agency_name_rec = agency_id_to_name_map.get(agency_id)
                if agency_name_rec is None or pd.isna(agency_name_rec): continue
                recommendations.append({
                    'agency': str(agency_name_rec), 'score': float(scores[agency_item_idx]),
                    'agency_id': str(agency_id), 'recommended_stars': score_to_stars(scores[agency_item_idx])})
        
        # CLUBS TO STAFF (Staff is current_user, looking for Clubs)
        elif recommendation_type == 'clubs_to_staff':
            if current_user_role != 'Staff': return jsonify({'message': 'User is not Staff'}), 200
            model = recommendation_models['staff_model']
            staff_user_idx = None
            for name, idx_val in recommendation_models['user_id_map_s'].items(): # staff_name -> user_idx
                if name.strip().lower() == current_user_name:
                    staff_user_idx = idx_val
                    break
            if staff_user_idx is None: return jsonify([])
            scores = model.predict(user_ids=np.repeat(staff_user_idx, len(recommendation_models['id_to_item_s'])),
                                   item_ids=np.arange(len(recommendation_models['id_to_item_s'])))
            for idx in np.argsort(-scores):
                if len(recommendations) >= top_n: break
                club_id = recommendation_models['id_to_item_s'].get(idx) # item_idx -> club_id
                club_name = recommendation_models['club_id_to_name'].get(club_id, club_id)
                if pd.isna(club_name): continue
                recommendations.append({
                    'club': str(club_name), 'score': float(scores[idx]),
                    'club_id': club_id, 'recommended_stars': score_to_stars(scores[idx])})

        # STAFF TO CLUB (Club is current_user, looking for Staff)
        elif recommendation_type == 'staff_to_club':
            if current_user_role != 'Club': return jsonify({'message': 'User is not a Club'}), 200
            model = recommendation_models['staff_model']
            club_item_idx = recommendation_models['item_id_map_s'].get(current_user_name) # club_name -> item_idx
            if club_item_idx is None: return jsonify({'message': 'Club not in mapping'}), 404
            scores = model.predict(user_ids=np.arange(len(recommendation_models['user_id_map_s'])),
                                   item_ids=np.repeat(club_item_idx, len(recommendation_models['user_id_map_s'])))
            for idx in np.argsort(-scores):
                if len(recommendations) >= top_n: break
                staff_id_or_name = recommendation_models['id_to_user_s'].get(idx) # user_idx -> staff_name/id
                staff_display_name = recommendation_models.get('staff_name_map', {}).get(staff_id_or_name, staff_id_or_name)
                if pd.isna(staff_display_name): continue
                recommendations.append({
                    'staff': str(staff_display_name), 'score': float(scores[idx]),
                    'recommended_stars': score_to_stars(scores[idx])})
        else:
            return jsonify({'error': f'Unknown recommendation type: {recommendation_type}'}), 400

        return jsonify(recommendations)

    except KeyError as e:
        app.logger.error(f"KeyError in recommendation logic for type '{recommendation_type}': {str(e)}. Check model mappings.")
        return jsonify({'error': f'Model component missing for {recommendation_type}: {str(e)}'}), 500
    except Exception as e:
        import traceback
        app.logger.error(f"Error processing {recommendation_type} in service: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Internal error in recommendation service for {recommendation_type}'}), 500

if __name__ == '__main__':
    load_models_from_pickle() # Load models at startup
    app.run(host='0.0.0.0', port=5001) # Run on a different port

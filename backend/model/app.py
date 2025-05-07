from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Load models and metadata at startup
performance_model = joblib.load('performance_model.pkl')
longevity_model = joblib.load('longevity_model.pkl')
imputer = joblib.load('imputer.pkl')
with open('model_metadata.json', 'r') as f:
    metadata = json.load(f)
    feature_names = metadata['feature_names']

DATA_PATH = os.path.join(os.path.dirname(__file__), 'player_stats_with_positions.csv')

def process_new_player_data(career_stats):
    df = pd.DataFrame(career_stats)
    df['position'] = df['position'].str.upper().str.strip()
    valid_positions = ['DF', 'MF', 'FW']
    df['position'] = df['position'].apply(lambda x: x if x in valid_positions else 'FW')
    df['minutes_adj'] = df['minutes'].replace(0, 1)
    df['goals_per_90'] = (df['goals'] * 90) / df['minutes_adj']
    df['assists_per_90'] = (df['assists'] * 90) / df['minutes_adj']
    primary_position = df['position'].mode()[0] if not df['position'].mode().empty else 'FW'
    pos_DF = 1 if primary_position == 'DF' else 0
    pos_MF = 1 if primary_position == 'MF' else 0
    pos_FW = 1 if primary_position == 'FW' else 0
    max_minutes = 5000
    if primary_position == 'FW':
        df['position_score'] = 0.7 * df['goals_per_90'] + 0.3 * df['assists_per_90']
    elif primary_position == 'MF':
        df['position_score'] = 0.4 * df['goals_per_90'] + 0.6 * df['assists_per_90']
    else:
        df['position_score'] = 0.2 * df['goals_per_90'] + 0.3 * df['assists_per_90'] + 0.5 * (df['minutes'] / max_minutes)
    last_3 = df.iloc[-3:] if len(df) >= 3 else df
    weights = np.arange(1, len(last_3)+1)
    def safe_avg(series): return np.average(series, weights=weights[:len(series)]) if len(series) else 0
    last_season = df.iloc[-1]
    matches_adj = max(last_season['matches'], 1)
    minutes_adj = max(last_season['minutes'], 1)
    rolling_3season_mins = df['minutes'].iloc[-3:].mean() if len(df) >= 3 else df['minutes'].mean()
    rolling_3season_mins_pct = (df['minutes'] / (df['matches'] * 90)).replace(0, 1).iloc[-3:].mean() if len(df) >= 3 else (df['minutes'] / (df['matches'] * 90)).replace(0, 1).mean()
    features = {
        'age': last_season['age'],
        'pos_DF': pos_DF,
        'pos_MF': pos_MF,
        'pos_FW': pos_FW,
        'team_encoded': 0.5,
        'season_start': 2025,
        'goals_per_90': last_season['goals_per_90'],
        'assists_per_90': last_season['assists_per_90'],
        'position_score': last_season['position_score'],
        'goals_per_90_weighted_recent': safe_avg(last_3['goals_per_90']),
        'assists_per_90_weighted_recent': safe_avg(last_3['assists_per_90']),
        'position_score_weighted_recent': safe_avg(last_3['position_score']),
        'minutes_weighted_recent': safe_avg(last_3['minutes']),
        'mins_per_appearance': minutes_adj / matches_adj,
        'availability': matches_adj / df['matches'].max() if df['matches'].max() > 0 else 1,
        'seasons_since_debut': len(df),
        'recent_form': df['position_score'].iloc[-3:].mean() if len(df) >= 3 else df['position_score'].mean(),
        'team_strength': 0.5,
        'injury_prone': int((minutes_adj / (matches_adj * 90)) < 0.6) if matches_adj > 0 else 0,
        'mins_pct_possible': minutes_adj / (matches_adj * 90) if matches_adj > 0 else 1,
        'rolling_3season_mins': rolling_3season_mins,
        'rolling_3season_mins_pct': rolling_3season_mins_pct,
        'minutes_weighted_recent': safe_avg(last_3['minutes'])
    }
    # Fill missing features with 0
    for fname in feature_names:
        if fname not in features:
            features[fname] = 0.0
    return pd.DataFrame([features])[feature_names]

def get_player_features_from_dataset(player_name):
    df = pd.read_csv(DATA_PATH, thousands=',', quotechar='"')
    # Normalize player names for robust matching
    df['player_name_norm'] = df['player_name'].astype(str).str.strip().str.lower()
    player_name_norm = player_name.strip().lower()
    # Feature engineering (must match your training pipeline)
    df['position'] = df['position'].str.upper().str.strip()
    valid_positions = ['DF', 'MF', 'FW']
    df['position'] = df['position'].apply(lambda x: x if x in valid_positions else 'FW')
    df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce')
    df['goals'] = pd.to_numeric(df['goals'], errors='coerce')
    df['assists'] = pd.to_numeric(df['assists'], errors='coerce')
    df['mp'] = pd.to_numeric(df['mp'], errors='coerce')
    df['minutes_adj'] = df['minutes'].replace(0, 1)
    df['goals_per_90'] = (df['goals'] * 90) / df['minutes_adj']
    df['assists_per_90'] = (df['assists'] * 90) / df['minutes_adj']
    # One-hot for position
    for pos in ['DF', 'MF', 'FW']:
        df[f'pos_{pos}'] = (df['position'] == pos).astype(int)
    # Team encoding (neutral for API)
    df['team_encoded'] = 0.5
    # Season start
    df['season_start'] = pd.to_numeric(df['season'].str.split('-').str[0], errors='coerce').fillna(-1).astype(int)
    # Position score
    max_minutes = df['minutes'].max() or 1
    df['position_score'] = (
        0.7 * df['goals_per_90'] + 0.3 * df['assists_per_90']
    ) * df['pos_FW'] + (
        0.4 * df['goals_per_90'] + 0.6 * df['assists_per_90']
    ) * df['pos_MF'] + (
        0.2 * df['goals_per_90'] + 0.3 * df['assists_per_90'] + 0.5 * (df['minutes'] / max_minutes)
    ) * df['pos_DF']
    # Weighted recent features
    player_df = df[df['player_name_norm'] == player_name_norm].sort_values('season_start')
    if player_df.empty:
        return None
    last_3 = player_df.iloc[-3:] if len(player_df) >= 3 else player_df
    weights = np.arange(1, len(last_3)+1)
    def safe_avg(series): return np.average(series, weights=weights[:len(series)]) if len(series) else 0
    last_season = player_df.iloc[-1]
    matches_adj = max(last_season['mp'], 1)
    minutes_adj = max(last_season['minutes'], 1)
    rolling_3season_mins = player_df['minutes'].iloc[-3:].mean() if len(player_df) >= 3 else player_df['minutes'].mean()
    rolling_3season_mins_pct = (player_df['minutes'] / (player_df['mp'] * 90)).replace(0, 1).iloc[-3:].mean() if len(player_df) >= 3 else (player_df['minutes'] / (player_df['mp'] * 90)).replace(0, 1).mean()
    features = {
        'age': last_season['age'],
        'pos_DF': last_season['pos_DF'],
        'pos_MF': last_season['pos_MF'],
        'pos_FW': last_season['pos_FW'],
        'team_encoded': 0.5,
        'season_start': last_season['season_start'] + 1,  # Predict for next season
        'goals_per_90': last_season['goals_per_90'],
        'assists_per_90': last_season['assists_per_90'],
        'position_score': last_season['position_score'],
        'goals_per_90_weighted_recent': safe_avg(last_3['goals_per_90']),
        'assists_per_90_weighted_recent': safe_avg(last_3['assists_per_90']),
        'position_score_weighted_recent': safe_avg(last_3['position_score']),
        'minutes_weighted_recent': safe_avg(last_3['minutes']),
        'mins_per_appearance': minutes_adj / matches_adj,
        'availability': matches_adj / player_df['mp'].max() if player_df['mp'].max() > 0 else 1,
        'seasons_since_debut': len(player_df),
        'recent_form': player_df['position_score'].iloc[-3:].mean() if len(player_df) >= 3 else player_df['position_score'].mean(),
        'team_strength': 0.5,
        'injury_prone': int((minutes_adj / (matches_adj * 90)) < 0.6) if matches_adj > 0 else 0,
        'mins_pct_possible': minutes_adj / (matches_adj * 90) if matches_adj > 0 else 1,
        'rolling_3season_mins': rolling_3season_mins,
        'rolling_3season_mins_pct': rolling_3season_mins_pct,
        'minutes_weighted_recent': safe_avg(last_3['minutes'])
    }
    for fname in feature_names:
        if fname not in features:
            features[fname] = 0.0
    return pd.DataFrame([features])[feature_names]

@app.route('/predict/player/<player_name>', methods=['GET'])
def predict_player(player_name):
    features_df = get_player_features_from_dataset(player_name)
    if features_df is None:
        return jsonify({"error": f"Player '{player_name}' not found in dataset"}), 404
    features_imputed = imputer.transform(features_df)
    perf_pred = performance_model.predict(features_imputed)[0]
    longevity_prob = longevity_model.predict_proba(features_imputed)[0][1]
    return jsonify({
        "player_name": player_name,
        "predictions": {
            "goals": float(perf_pred[0]),
            "assists": float(perf_pred[1]),
            "matches": float(perf_pred[2]),
            "minutes": float(perf_pred[3])
        },
        "probability_playing_next_season": float(longevity_prob)
    })

@app.route('/predict/new_player', methods=['POST'])
def predict_new_player():
    data = request.json
    if not data or 'career_stats' not in data:
        return jsonify({"error": "Missing 'career_stats' in request"}), 400
    features_df = process_new_player_data(data['career_stats'])
    features_imputed = imputer.transform(features_df)
    perf_pred = performance_model.predict(features_imputed)[0]
    longevity_prob = longevity_model.predict_proba(features_imputed)[0][1]
    return jsonify({
        "player_name": data.get('name', 'New Player'),
        "predictions": {
            "goals": float(perf_pred[0]),
            "assists": float(perf_pred[1]),
            "matches": float(perf_pred[2]),
            "minutes": float(perf_pred[3])
        },
        "probability_playing_next_season": float(longevity_prob)
    })

@app.route('/players', methods=['GET'])
def get_players():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df['season_start'] = df['season'].astype(str).str.extract(r'(\d{4})')[0]
    df['season_start'] = pd.to_numeric(df['season_start'], errors='coerce').fillna(0).astype(int)
    latest = df.sort_values('season_start').groupby('player_name').tail(1)
    players = [
        {
            "name": row['player_name'],
            "age": int(row['age']) if pd.notnull(row['age']) else None,
            "position": row['position'],
            "team": row['team']
        }
        for _, row in latest.iterrows()
    ]
    return jsonify(players)
@app.route('/player/<name>/career', methods=['GET'])
def player_career(name):
    import pandas as pd
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    player_df = df[df['player_name'] == name]
    if player_df.empty:
        return jsonify({"error": "Player not found"}), 404
    player_df = player_df.sort_values('season')
    info = player_df.iloc[-1][['player_name', 'age', 'position', 'team']].to_dict()
    career = player_df[['season', 'goals', 'assists', 'minutes', 'mp']].to_dict(orient='records')
    return jsonify({'info': info, 'career': career})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
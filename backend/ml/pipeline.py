"""
ML Training Pipeline — trains 4 models on career data, builds ensemble, stores predictions.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path

from backend.db.database import SessionLocal
from backend.ml.features import extract_features, FEATURE_COLUMNS, TARGET_COLUMNS
from backend.models.prediction import Prediction, EnsemblePrediction
from backend.models.career import Career


MODELS_DIR = Path(__file__).parent / "saved_models"
MODELS_DIR.mkdir(exist_ok=True)


def get_models():
    return {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42
        ),
        "neural_network": MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            max_iter=500,
            early_stopping=True,
            random_state=42,
            validation_fraction=0.15,
        ),
    }


def train_and_evaluate():
    db = SessionLocal()

    try:
        print("Extracting features from database...")
        df = extract_features(db)
        print(f"  Total records: {len(df)}")

        # Encode category as numeric
        le = LabelEncoder()
        df["category_encoded"] = le.fit_transform(df["category"].fillna("Other"))
        joblib.dump(le, MODELS_DIR / "label_encoder.joblib")

        feature_cols = FEATURE_COLUMNS + ["category_encoded"]

        # Check we have target columns
        for target in TARGET_COLUMNS:
            if target not in df.columns:
                print(f"  Warning: target '{target}' not found, skipping.")
                continue

        X = df[feature_cols].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, MODELS_DIR / "scaler.joblib")

        results = {}

        for target in TARGET_COLUMNS:
            if target not in df.columns:
                continue

            y = df[target].fillna(df[target].median())
            print(f"\n{'='*60}")
            print(f"Training models for target: {target}")
            print(f"{'='*60}")

            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )

            target_results = {}
            models = get_models()

            for name, model in models.items():
                print(f"\n  Training {name}...")
                model.fit(X_train, y_train)

                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)

                mae = mean_absolute_error(y_test, y_pred_test)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
                r2 = r2_score(y_test, y_pred_test)
                train_r2 = r2_score(y_train, y_pred_train)

                print(f"    Train R²: {train_r2:.4f}")
                print(f"    Test  R²: {r2:.4f}")
                print(f"    MAE:      {mae:.2f}")
                print(f"    RMSE:     {rmse:.2f}")

                model_path = MODELS_DIR / f"{name}_{target}.joblib"
                joblib.dump(model, model_path)
                print(f"    Saved to: {model_path}")

                target_results[name] = {
                    "model": model,
                    "mae": mae,
                    "rmse": rmse,
                    "r2": r2,
                    "train_r2": train_r2,
                }

            results[target] = target_results

        # Generate predictions for all careers
        print(f"\n{'='*60}")
        print("Generating ensemble predictions for all careers...")
        print(f"{'='*60}")

        # Clear existing predictions
        db.query(Prediction).delete()
        db.query(EnsemblePrediction).delete()
        db.commit()

        X_all = scaler.transform(df[feature_cols].fillna(0))

        for idx, row in df.iterrows():
            career_id = int(row["career_id"])
            x = X_all[idx].reshape(1, -1)

            model_preds = {}
            for target in TARGET_COLUMNS:
                if target not in results:
                    continue
                model_preds[target] = {}
                for model_name, info in results[target].items():
                    pred_value = info["model"].predict(x)[0]
                    model_preds[target][model_name] = pred_value

            # Store individual model predictions
            for model_name in get_models().keys():
                risk = model_preds.get("automation_risk_score", {}).get(model_name, 50)
                year = model_preds.get("disruption_year", {}).get(model_name, 2035)
                stability = model_preds.get("job_stability_score", {}).get(model_name, 50)

                risk = max(5, min(95, risk))
                year = max(2026, min(2050, int(year)))
                stability = max(10, min(95, stability))

                salary_impact = -(risk * 0.4) + np.random.normal(0, 3)
                salary_impact = max(-45, min(25, salary_impact))

                pred = Prediction(
                    career_id=career_id,
                    model_name=model_name,
                    automation_risk_score=round(risk, 1),
                    disruption_year=year,
                    salary_impact_pct=round(salary_impact, 1),
                    job_stability_score=round(stability, 1),
                    confidence_interval_low=round(max(0, risk - 8), 1),
                    confidence_interval_high=round(min(100, risk + 8), 1),
                )
                db.add(pred)

            # Ensemble: inverse-MAE weighted average
            ensemble_values = {}
            for target in TARGET_COLUMNS:
                if target not in results:
                    continue
                weights = []
                values = []
                for model_name, info in results[target].items():
                    w = 1.0 / max(info["mae"], 0.01)
                    weights.append(w)
                    values.append(model_preds[target][model_name])
                total_w = sum(weights)
                ensemble_values[target] = sum(v * w for v, w in zip(values, weights)) / total_w

            risk_score = max(5, min(95, ensemble_values.get("automation_risk_score", 50)))
            disruption = max(2026, min(2050, int(ensemble_values.get("disruption_year", 2035))))
            stability = max(10, min(95, ensemble_values.get("job_stability_score", 50)))

            if risk_score >= 70:
                risk_level = "critical"
            elif risk_score >= 50:
                risk_level = "high"
            elif risk_score >= 30:
                risk_level = "medium"
            else:
                risk_level = "low"

            salary = row["median_salary"]
            growth = row["growth_rate_pct"]
            impact_pct = -(risk_score * 0.4)
            salary_5yr = salary * (1 + (impact_pct / 100) * 0.4 + growth / 100 * 0.5)
            salary_10yr = salary * (1 + (impact_pct / 100) * 0.8 + growth / 100)

            ensemble = EnsemblePrediction(
                career_id=career_id,
                automation_risk_score=round(risk_score, 1),
                disruption_year=disruption,
                salary_5yr_projection=round(salary_5yr, 0),
                salary_10yr_projection=round(salary_10yr, 0),
                job_stability_score=round(stability, 1),
                risk_level=risk_level,
            )
            db.add(ensemble)

        db.commit()
        total = db.query(EnsemblePrediction).count()
        print(f"\nDone! Generated ensemble predictions for {total} careers.")

        # Print summary
        print(f"\n{'='*60}")
        print("MODEL PERFORMANCE SUMMARY")
        print(f"{'='*60}")
        for target, target_results in results.items():
            print(f"\n  Target: {target}")
            for name, info in sorted(target_results.items(), key=lambda x: x[1]["mae"]):
                print(f"    {name:25s}  MAE={info['mae']:.2f}  R²={info['r2']:.4f}")

    finally:
        db.close()


if __name__ == "__main__":
    train_and_evaluate()

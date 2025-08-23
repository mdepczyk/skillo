import os

from joblib import load

from skillo.utils.logger import logger


class ProfileClassifier:
    """Classifies CV profiles using pre-trained ML model."""

    def __init__(self):
        """Initialize classifier and load models."""
        self._vectorizer = None
        self._model = None
        self._label_encoder = None
        self._loaded = False
        self._load_models()

    def _load_models(self):
        """Load ML models from joblib files."""
        try:
            models_dir = os.path.join(
                os.path.dirname(__file__), "..", "models"
            )

            vectorizer_path = os.path.join(models_dir, "vectorizer.joblib")
            model_path = os.path.join(
                models_dir, "KNeighborsClassifier.joblib"
            )
            encoder_path = os.path.join(models_dir, "label_encoder.joblib")

            if not all(
                os.path.exists(p)
                for p in [vectorizer_path, model_path, encoder_path]
            ):
                logger.error(
                    "PROFILE_CLASSIFIER",
                    "Model files not found",
                    f"Missing files: {vectorizer_path}, {model_path}, {encoder_path}",
                )
                self._loaded = False
                return

            self._vectorizer = load(vectorizer_path)
            self._model = load(model_path)
            self._label_encoder = load(encoder_path)
            self._loaded = True

            logger.success(
                "PROFILE_CLASSIFIER", "Trained model loaded successfully"
            )

        except Exception as e:
            logger.error("PROFILE_CLASSIFIER", "Error loading models", str(e))
            self._loaded = False

    def classify_profile(self, cv_content: str) -> str:
        """
        Classify CV profile based on content.

        Args:
            cv_content: Raw CV text content

        Returns:
            Predicted profile/category (e.g., "developer", "designer", etc.)
        """
        if not self._loaded:
            logger.warning(
                "PROFILE_CLASSIFIER",
                "Models not loaded",
                "Returning 'Unknown' profile",
            )
            return "Unknown"

        try:

            X_new = self._vectorizer.transform([cv_content])

            y_pred_num = self._model.predict(X_new)

            y_pred_label = self._label_encoder.inverse_transform(y_pred_num)

            profile = y_pred_label[0]
            logger.info(
                "PROFILE_CLASSIFIER",
                "Profile classified",
                f"Predicted profile: {profile}",
            )

            return profile

        except Exception as e:
            logger.error(
                "PROFILE_CLASSIFIER", "Error during classification", str(e)
            )
            return "Unknown"
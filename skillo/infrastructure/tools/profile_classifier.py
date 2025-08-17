import os
from typing import Any

from joblib import load  # type: ignore

from skillo.domain.services import ProfileClassificationService
from skillo.infrastructure.logger import logger


class ProfileClassifier(ProfileClassificationService):
    """CV profile classifier using ML model."""

    def __init__(self, models_dir_path: str) -> None:
        """Initialize with models directory path."""
        self._models_dir = models_dir_path
        self._vectorizer: Any = None
        self._model: Any = None
        self._label_encoder: Any = None
        self._loaded = False

    def _load_models(self) -> None:
        """Load ML models from files."""
        try:
            vectorizer_path = os.path.join(
                self._models_dir, "vectorizer.joblib"
            )
            model_path = os.path.join(
                self._models_dir, "KNeighborsClassifier.joblib"
            )
            encoder_path = os.path.join(
                self._models_dir, "label_encoder.joblib"
            )

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
        """Classify CV profile based on content."""
        if not self._loaded:
            self._load_models()

        try:
            X = self._vectorizer.transform([cv_content])
            y_pred_num = self._model.predict(X)
            y_pred_label = self._label_encoder.inverse_transform(y_pred_num)

            profile = y_pred_label[0]
            logger.info(
                "PROFILE_CLASSIFIER",
                "Profile classified",
                f"Predicted profile: {profile}",
            )

            return str(profile)

        except Exception as e:
            logger.error(
                "PROFILE_CLASSIFIER", "Error during classification", str(e)
            )
            return "Unknown"
